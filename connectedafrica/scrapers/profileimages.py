import re
import urllib
import urlparse

from lxml import html
import requests
from thready import threaded

from connectedafrica.scrapers.util import (ScraperException, MultiCSV,
                                           gdocs_persons, make_abs_url,
                                           ACCEPTED_IMAGE_EXTENSIONS)
from connectedafrica.scrapers.wikipedia import ENDPOINT_URL as WIKI_ENDPOINT_URL


THREAD_COUNT = 10
WIKI_PARAMS = {
    'format': 'json',
    'action': 'query',
    'prop': 'imageinfo',
    'iiprop': 'url',
    'iiurlwidth': 512
}


def _scrape_from_pa(resp):
    root = html.fromstring(resp.text)
    pic_el = root.find_class('profile-pic')
    if pic_el:
        pic_el = pic_el[0].xpath('img[1]')
        if pic_el:
            return pic_el[0].get('src')
    raise ScraperException("Image not found at %s" % resp.url)


def _scrape_from_google(resp):
    parts = urlparse.urlparse(resp.url)
    if parts.path == '/imgres':
        params = dict(urlparse.parse_qsl(parts.query, True))
        if 'imgurl' in params:
            return params['imgurl']
    elif parts.path == '/search':
        if parts.fragment.strip() != '':
            params = dict(urlparse.parse_qsl(parts.fragment, True))
            if 'imgrc' in params:
                url = urllib.unquote(params['imgrc']).split(';')[-4]
                return urllib.unquote(url)
    raise ScraperException("Image not found at %s" % resp.url)


def _scrape_from_whoswho(resp):
    root = html.fromstring(resp.text)
    pic_el = root.get_element_by_id('profile-pic', None)
    if pic_el is not None:
        pic_el = pic_el.xpath('a[1]/img')
        if pic_el:
            return pic_el[0].get('src')
    raise ScraperException("Image not found at %s" % resp.url)


def _scrape_from_wikipedia(resp):
    match = re.search(r'(#mediaviewer|wiki)/(?P<filename>File:.*)$', resp.url)
    if match:
        filename = match.group('filename')
    else:
        root = html.fromstring(resp.text)
        image_el = root.find_class('vcard')[0].find_class('image')
        if not image_el:
            raise ScraperException("Image not found at %s" % resp.url)
        filename = image_el[0].get('href')
        filename = filename[filename.index('File:'):]
    # use the Wikimedia API to get the file url at a reasonable size
    params = WIKI_PARAMS.copy()
    params['titles'] = filename.replace('_', ' ')
    response = requests.get(WIKI_ENDPOINT_URL, params=params)
    data = response.json()['query']
    if 'pages' not in data or len(data['pages']) == 0:
        raise ScraperException("Image not found at %s" % resp.url)
    return data['pages'].values()[0]['imageinfo'][0]['thumburl']


def _scrape_from_parliament(resp):
    root = html.fromstring(resp.text)
    # selects the first image after the brownHeading el
    # NOTE: should we rather not scrape this at all?
    img_el = root.xpath("//*[@class='brownHeading']//following::*//img")
    if len(img_el) > 0:
        return img_el[0].get('src')
    raise ScraperException("Image not found at %s" % resp.url)


VALID_ENDPOINTS = {
    "www.pa.org.za": _scrape_from_pa,
    "www.google.co.za": _scrape_from_google,
    "whoswho.co.za": _scrape_from_whoswho,
    "en.wikipedia.org": _scrape_from_wikipedia,
    "www.parliament.gov.za": _scrape_from_parliament
}


def scrape_image(name, url, csv, image_credit=''):
    url = url.strip()
    if not url:
        return

    print "scraping %s" % name
    parts = urlparse.urlparse(url)
    if not parts.scheme:
        url = 'http://%s' % url
        parts = urlparse.urlparse(url)
    resp = requests.get(url)
    mime_type = resp.headers['content-type']
    if not mime_type.startswith('image/'):
        scrape_func = VALID_ENDPOINTS.get(parts.netloc, None)
        if scrape_func is None:
            raise ScraperException("Cannot scrape image from %s" % parts.netloc)
        image_url = scrape_func(resp)
        url = make_abs_url(url, image_url)
    elif '.%s' % mime_type.split('/')[1] not in ACCEPTED_IMAGE_EXTENSIONS:
        raise ScraperException("Unsupported image format at %s" % url)

    csv.write('profileimages.csv', {
        'name': name,
        'image_url': url,
        'image_credit': image_credit
    })


def scrape():
    csv = MultiCSV()
    threaded(
        gdocs_persons(),
        lambda data: scrape_image(data['Full Name'], data['Image URL'], csv,
                                  data['Image Credit']),
        num_threads=THREAD_COUNT
    )
    csv.close()


if __name__ == '__main__':
    scrape()
