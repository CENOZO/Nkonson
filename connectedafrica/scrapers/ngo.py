import logging
import json
import time
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

URL_ROOT = 'http://www.ghanayello.com'
URL_PATTERN = 'http://www.ghanayello.com/companies/NGO/%s'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}



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
    

def ngo_urls():
    next_page = True
    i = 1
    company_urls = []
    data = {}
    csv = MultiCSV()
    while next_page:
        url = URL_PATTERN % i
        res = requests_retry_session().get(url, headers=HEADERS)
        page = {
            'url': url,
            'http_status': res.status_code,
            'content': res.content
        }
        soup = BeautifulSoup(page['content'], "html.parser")
        urls = [URL_ROOT + a["href"] for a in soup.select("div h4 a")]
        company_urls += urls
        data = { "page": i, "urls": urls}
        csv.write('ngos/ghanayello_ngos_urls.csv', data)
        i += 1
        if ('404 error: Page not found' in page['content']):
            next_page = False
    csv.close()
    return company_urls


def make_urls():
    urls = ngo_urls()  
    for url in urls:
        # time.sleep(5)
        yield url


def scrape_ngo(csv, url):
    res = requests_retry_session().get(url, headers=HEADERS)
    print("\n\n\n ########   %s  ######" % url)
    page = {
        'url': url,
        'http_status': res.status_code,
        'content': res.content
    }
    if 'internal server error' in page['content'] or 'Either BOF or EOF is True, or the current record has been deleted' in page['content'] or page['http_status'] != 200:
        return
    data = {}
    soup = BeautifulSoup(page['content'], "lxml")

    infos = soup.find_all("div", class_= "info")

    comp = []
    i = 0
    r = { 'k': None, 'v': None}
    for d in infos:
        key = None
        if d.select("div"):
            key = d.select("div")[0].get_text().strip()
        else:
            key = d.span.text

        value = None

        if key == 'Listed in categories':
            categories = soup.find_all("div", class_= "categories")[0]
            cats = []
            if categories.find_all("a"):
                for cat in categories.find_all("a"):
                    cats.append({"url": cat["href"], "text": cat.get_text().strip()})
            value = cats
        elif key == 'E-mail':
            value = d.find_all("a")[0]["href"]
        elif key == 'Location map \r\n\t\t\t\t\r\n\t\t\t\tGet Directions':
            key = 'Location url'
            value = d.find_all("a")[0]["href"]

        else:
            if d.find_all("div", class_= "text"):
                value = d.find_all("div", class_= "text")[0].get_text().strip()
            elif d.select("span"):
                if len(d.select("span")) > 1:
                   value = d.select("span")[1].get_text().strip()
                else:
                    if d.find_all("div"):
                        value = d.select("span")[0].get_text().strip()
                    else: 
                        d.find('span').decompose()
                        value = d.get_text().strip()


        r = { 'k': key, 'v': value}
        comp.append(r)

    data["url"] = url
    data["country"] = "Ghana"
    data["country_code"] = "GHA"
    data["scraped_time"] = str(datetime.datetime.now())
    cols=['Company name', 'Address', 'Phone', 'Website', 'Establishment year', 'Employees', 'Company manager', 'E-mail', 'Location url', 'Description', 'Listed in categories']
    for c in comp:
        if c["k"] in cols:
            data[c["k"]] = c["v"]
    
    # data = {"url": url, "content": comp}

    csv.write('ngos/ghanayello_ngos_data.csv', data)
    print("################## Data #################")
    print(data)


def scrape_ngos():
    csv = MultiCSV()
    threaded(make_urls(), lambda url: scrape_ngo(csv, url), num_threads=13)
    csv.close()

def cd():
    for d in divs:
        try:
            print(d["class"])
        except:
            pass



if __name__ == '__main__':
    scrape_ngos()
