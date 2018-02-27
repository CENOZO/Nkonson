import logging
import json
import os
import re
import pandas as pd
import string
import requests
import datetime
#from pprint import pprint
#from itertools import count
from urlparse import urljoin
from bs4 import BeautifulSoup
import urllib
from lxml import html
from thready import threaded
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from scrapekit.util import collapse_whitespace
from dateutil import parser


from connectedafrica.scrapers.util import MultiCSV
from connectedafrica.scrapers.util import make_path

URL_PATTERN = 'https://www.ppaghana.org/contractdetail.asp?Con_ID=%s'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

def make_urls():
    for i in xrange(2200, 5100):
        yield i

def make_urls2():
    f = pd.read_csv("f.csv")
    all = pd.Index(range(1730,5100))
    # (105, 320, 609, 619)
    l = all.difference(f.contract_id)
    for i in l:
        yield i

def make_urls3():
    for i in (105, 320, 609, 619):
        yield i


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session






def scrape_contract(csv, i):
    url = URL_PATTERN % i
    res = requests_retry_session().get(url, headers=HEADERS)
    print("######### %s ########################################################## %s " % (str(i), res.status_code))
    page = {
        'url': url,
        'http_status': res.status_code,
        'content': res.content
    }
    if 'internal server error' in page['content'] or 'Either BOF or EOF is True, or the current record has been deleted' in page['content'] or page['http_status'] != 200:
        return
    data = {}
    soup = BeautifulSoup(page['content'])
    table = soup.find_all("table", class_="pagecentre")[0]
    els = table.find_all("td")
    contract_award_price_text = els[12].get_text().strip()
    non_decimal = re.compile(r'[^\d.]+')
    contract_award_price = non_decimal.sub('', contract_award_price_text)
    data = {
        'data_source': url,
        'contract_id' : i,
        'contract_title': els[0].get_text().strip(),
        'awarding_agency': els[1].get_text().split('/')[0].strip(),
        'awarding_ministry': els[1].get_text().split('/')[1].strip(),
        'awarding_agency_ministry': els[1].get_text().strip(),
        'awarding_agency_link': 'https://www.ppaghana.org/' + els[1].a['href'],
        'tender_description': els[2].get_text().strip(),
        'tender_package_no': els[3].get_text().strip(),
        'tender_type': els[4].get_text().strip(),
        'tender_lot_Numbers': els[5].get_text().strip(),
        'contract_awarded_to': els[6].get_text().strip(),
        'address': els[7].get_text().strip(),
        'company_email': els[8].get_text().strip(),
        'contract_signed_on': els[9].get_text().strip(),
        'estimated_contract_completion_date': els[10].get_text().strip(),
        'currency': els[11].get_text().strip(),
        'contract_award_price': contract_award_price,
        'scraped_time': str(datetime.datetime.now())
	}

    csv.write('ppa/ppa_contracts.csv', data)



def scrape_contracts():
    csv = MultiCSV()
    threaded(make_urls2(), lambda i: scrape_contract(csv, i), num_threads=30)
    csv.close()

if __name__ == '__main__':
    scrape_contracts()


