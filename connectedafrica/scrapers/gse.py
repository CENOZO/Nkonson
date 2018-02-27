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

URL_ROOT = 'https://gse.com.gh/listing/listed-companies'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}


def make_urls():
    res = requests_retry_session().get(URL_ROOT, headers=HEADERS)
    page = {
        'url': URL_ROOT,
        'http_status': res.status_code,
        'content': res.content
    }
    if 'internal server error' in page['content'] or 'Either BOF or EOF is True, or the current record has been deleted' in page['content'] or page['http_status'] != 200:
        return
    soup = BeautifulSoup(page['content'])
    table = soup.find_all("table", class_="col-md-12 table-bordered table-striped table-condensed cf")[0]
    els = table.find_all("a")    
    for url in els:
        yield url['href']


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

def remove_el(l, el):
    return [v for v in l if v != el]
    

def scrape_company(csv, url):
    res = requests_retry_session().get(url, headers=HEADERS)
    print("######### %s ##########################################################" % url)
    page = {
        'url': url,
        'http_status': res.status_code,
        'content': res.content
    }
    if 'internal server error' in page['content'] or 'Either BOF or EOF is True, or the current record has been deleted' in page['content'] or page['http_status'] != 200:
        return
    data = {}
    soup = BeautifulSoup(page['content'])
    table = soup.find_all("table", class_="table custom-table1")[0]
    els = table.find_all("td")
    company_name = els[1].get_text().strip()
    directors =  els[17].get_text().strip()
    data = {
        'data_source': url,

        'symbol' : els[0].get_text().strip(),
        'company_name': company_name,
        'stated_capital': els[2].get_text().strip(),
        'security': els[3].get_text().strip(),
        'nature_of_business': els[4].get_text().strip(),

        'date_incorporated': els[5].get_text().strip(),
        'incorporation_comments': els[6].get_text().strip(),        
        'date_listed': els[7].get_text().strip(),
        'registered_office': els[8].get_text().strip(),        
        'postal_address': els[9].get_text().strip(),

        'telephone': els[10].get_text().strip(),
        'fax': els[11].get_text().strip(),        
        'email': els[12].get_text().strip(),
        'website': els[13].get_text().strip(),        
        'types_of_traded_securities': els[14].get_text().strip(),
    
        'issued_shares': els[15].get_text().strip(),
        'authorised_shares': els[16].get_text().strip(),
        'directors': directors,
        'change_of_name': els[18].get_text().strip(),
        'comments': els[19].get_text().strip(),

        'scraped_time': str(datetime.datetime.now())
    }
    directors = directors.split('\n')
    directors = remove_el(directors, '')
    p={}
    for el in directors:
    	if el.split('- ')[0].strip() != el : name = el.split('- ')[0].strip()
    	if el.split(' -')[0].strip() != el : name = el.split(' -')[0].strip()
    	position = 'Managing Member'
        try:
	    	position = el.split('- ')[1].strip()
        except:
        	pass

        try:
	    	position = el.split(' -')[1].strip()
        except:
        	pass

        p = {
            'name': name,
            'position': position,
            'company_name': company_name,
            'data_source': url,
            'scraped_time': str(datetime.datetime.now())
        }
        csv.write('gse/company_directors.csv', p)
    csv.write('gse/company_profiles.csv', data)
    

def scrape_companies():
    csv = MultiCSV()
    threaded(make_urls(), lambda url: scrape_company(csv, url), num_threads=5)
    csv.close()
    

if __name__ == '__main__':
    scrape_companies()


