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

URL_ROOT = 'https://www.parliament.gh/'
URL_PATTERN = 'https://www.parliament.gh/mps?mp=%s'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}


def make_urls():
    for i in xrange(0, 300):
        yield i

def remove_el(l, el):
    return [v for v in l if v != el]

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
    

def scrape_person(csv, i):
    url = URL_PATTERN % i
    res = requests_retry_session().get(url, headers=HEADERS)
    print("######### %s ##########################################################" % i)
    page = {
        'url': url,
        'http_status': res.status_code,
        'content': res.content
    }
    if 'internal server error' in page['content'] or 'Either BOF or EOF is True, or the current record has been deleted' in page['content'] or page['http_status'] != 200:
        return
    data = {}
    soup = BeautifulSoup(page['content'])
    table = soup.find_all("table")[0]
    els = table.find_all("td")
    name_pic = els[0]
    details = els[1]
    details_els = details.find_all("td")
    constituency_region = name_pic.center.get_text().replace('\n', '').split('\r')[1].strip()
    constituency = constituency_region.split(',')[0].replace('MP for', '').replace('constituency', '').strip()
    region = constituency_region.split(',')[1].replace('.', '').strip()
    name = name_pic.h4.get_text().replace('HON.','').strip()
    party_data = details_els[3].get_text().replace('(', ',').replace(')', '').split(',')
    party_name = party_data[0].strip()
    party_status = party_data[1].strip()

    employments = details_els[13].font.renderContents().replace('<p>', '').replace('</p>', '').split('<br/>')
    employments = remove_el(employments, '')
    p={}
    org_type = ''
    if len(employments) > 1 :
        positions = []
        for e in employments:
            date_company = e.split(',')[-1].strip()
            if '(' not in date_company: date_company = e.split(',')[-2] + date_company
            position = e.replace(date_company, '').strip()
            date_position = date_company.split(' (')[0].strip()
            company_name = date_company.replace(date_position, '').strip()
            try: 
                company_name = re.search(r'\((.*)\)', company_name).group(1)
            except:
                pass

            p = {
                'name': name,
                'position': position,
                'date_position': date_position,
                'company_name': company_name,
                'organization_type': org_type,
                'data_source': url,
                'scraped_time': str(datetime.datetime.now())
            }
            csv.write('pag/pag_directorships.csv', p)
            positions.append(p)

    elif len(employments) == 1:
    	e = employments[0].replace('(', ',').replace(')','').strip().split(',')
        position = e[0].strip()
        date_position = e[1].strip()
        company_name = e[2].strip()
        org_type = ''
        if 'NGO' in company_name:
            company_name = company_name.replace('NGO', '').strip()
            org_type = 'NGO'
        p = {
	        'name': name,
	        'position': position,
	        'date_position': date_position,
	        'company_name': company_name,
	        'organization_type': org_type,
	        'data_source': url,
	        'scraped_time': str(datetime.datetime.now())
        }
        csv.write('pag/pag_directorships.csv', p)


    data = {
        'data_source': url,
        'name': name,
        'image_url': URL_ROOT + name_pic.img['src'].strip(),
        'constituency': constituency,
        'region': region,
        'hometown': details_els[1].get_text().strip(),
        'party_name': party_name,
        'party_status': party_status,
        'education': details_els[5].get_text().strip(),
        'date_birth': details_els[7].get_text().strip(),
        'religion': details_els[9].get_text().strip(),
        'email': details_els[11].get_text().strip(),
        'employment': details_els[13].get_text().strip(),
        'scraped_time': str(datetime.datetime.now())
    }

    csv.write('pag/pa_memberships.csv', data)
    

def scrape_persons():
    csv = MultiCSV()
    threaded(make_urls(), lambda i: scrape_person(csv, i), num_threads=25)
    csv.close()
    

if __name__ == '__main__':
    scrape_persons()


