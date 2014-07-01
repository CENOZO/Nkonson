import re
from datetime import datetime
import urlparse

from lxml import html
import requests


class ScraperException(Exception):
    pass


class Scraper(object):

    endpoint_url = 'http://whoswho.co.za/'
    date_format = '%d-%m-%Y'
    r_year_range = re.compile(
        r'(?P<start>\d{4})(\s+-\s+((?P<current>present)|(?P<end>\d{4})))?$'
    )

    def scrape(self, url, degrees=0, scraped_urls=None):
        print 'Scraping %s' % url
        if scraped_urls is None:
            scraped_urls = set()

        abs_url = self.get_absolute_url(url)
        if abs_url in scraped_urls:
            return
        data = self.get_data(abs_url)
        scraped_urls.add(abs_url)
        yield data

        if degrees > 0:
            for related_profile in data['related_profiles']:
                for data in self.scrape(related_profile['url'],
                                        degrees - 1, scraped_urls):
                    yield data

    def get_absolute_url(self, url):
        if not url.startswith(Scraper.endpoint_url):
            parts = urlparse.urlparse(url)
            if parts.scheme == 'https':
                raise ScraperException("Who's Who does not accept https connections")
            elif parts.netloc:
                raise ScraperException("'%s' is not a Who's Who URL" % url)
            return urlparse.urlunparse(['http', 'whoswho.co.za'] + list(parts[2:]))
        return url

    def parse_content(self, content):
        # TODO: education + achievements sections
        # TODO: don't rely as much on order of simple tags
        data = {
            'related_profiles': [],
            'professional_details': [],
            'activities': [],
        }
        root = html.fromstring(content)

        # basic info
        basic_el = root.get_element_by_id('profiles-form-edit') \
                       .xpath("//div[@itemtype='http://schema.org/Person'][1]")
        if len(basic_el) == 0:
            raise ScraperException("Content doesn't appear to be a person's profile")
        basic_el = basic_el[0]
        name_short = basic_el.xpath("h1[@itemprop='name'][1]/text()")[0].strip()
        name_full = basic_el.xpath("p[1]/em/text()")[0].strip()
        job_title = basic_el.xpath("h4[@itemprop='jobTitle'][1]/text()")[0].strip()
        bio = basic_el.xpath("p[3]/text()")[0].strip()
        data['basic_info'] = {
            'name_short': name_short,
            'name_full': name_full,
            'job_title': job_title,
            'bio': bio
        }
        # date of birth
        birth_node = basic_el.xpath("p[2]")[0]
        birth_date = birth_node.xpath('a[1]/text()')
        if birth_date:
            data['basic_info']['birth_date'] = datetime.strptime(
                birth_date[0],
                Scraper.date_format
            )
        birth_town = birth_node.find_class('locality')
        if birth_town:
            if birth_town[0].xpath('a'):
                data['basic_info']['birth_town'] = birth_town[0].xpath('a[1]/text()')[0]
            elif birth_town[0].text:
                text = birth_town[0].text.strip()
                if text.startswith('in '):
                    text = text[3:]
                data['basic_info']['birth_town'] = text
        birth_country = birth_node.xpath("//span[@itemprop='nationality'][1]/text()")
        if birth_country:
            data['basic_info']['country'] = birth_country[0]

        # professional info
        prof_el = root.get_element_by_id('professional-details', None)
        if prof_el is not None:
            current = None
            for el in prof_el:
                if el.tag == 'h2':
                    if current is None:
                        current = True
                    else:
                        current = False
                elif el.tag == 'div' and current is not None:
                    role_parts = [s.strip() for s in 
                                  el.xpath('h6/br/preceding-sibling::text()[1]')[0]
                                    .split('|')
                                  if s.strip() != '']
                    date_parts = [s.strip() for s in 
                                  el.xpath('h6/br/following-sibling::text()[1]')[0]
                                    .split('|')
                                  if s.strip() != '']
                    role_data = {
                        'role_name': role_parts[0],
                        'status': 'active' if current else 'inactive'
                    }
                    # get start and end year
                    if date_parts:
                        date_parts = Scraper.r_year_range.match(date_parts[-1])
                        if date_parts:
                            role_data['role_start_year'] = int(date_parts.group('start'))
                            if date_parts.group('current'):
                                assert current
                            elif date_parts.group('end'):
                                role_data['role_end_year'] = int(date_parts.group('end'))
                            elif not current:
                                role_data['role_end_year'] = role_data['role_start_year']
                    # get organization info
                    org_el = el.xpath('h6/a[last()]')
                    if len(org_el) > 0:
                        org_el = org_el[0]
                        role_data['organization_name'] = org_el.text
                        role_data['organization_url'] = org_el.get('href', None)
                    # the organization doesn't have a url
                    # use 2nd last piece of plain text
                    elif len(role_parts) > 2:
                        role_data['organization_name'] = role_parts[-2]
                    else:
                        continue
                    data['professional_details'].append(role_data)

        # activities info
        activity_el = root.get_element_by_id('activities', None)
        if activity_el is not None:
            # only doing memberships
            for el in activity_el.xpath("h2[.='Memberships']/following-sibling::node()"):
                if not isinstance(el, html.HtmlElement) or el.tag != 'div':
                    break
                org_name = el.xpath('h6[1]/text()')[0]
                role_parts = el.xpath('p[1]/em/text()')[0].split(',')
                role_data = {
                    'role_name': role_parts[0].strip(),
                    'organization_name': org_name,
                }
                if len(role_parts) == 2:
                    date_parts = Scraper.r_year_range.match(role_parts[1])
                    if date_parts:
                        role_data['role_start_year'] = int(date_parts.group('start'))
                        if date_parts.group('current'):
                            role_data['status'] = 'active'
                        elif date_parts.group('end'):
                            role_data['status'] = 'inactive'
                            role_data['role_end_year'] = int(date_parts.group('end'))
                data['activities'].append(role_data)

        # related profile info
        related_el = root.get_element_by_id('related', None)
        if related_el is not None:
            for el in related_el.find_class('item'):
                a_el = el.xpath('a')[0]
                related_data = {'url': a_el.get('href')}
                img_el = a_el.xpath('img')
                if len(img_el) > 0:
                    img_el = img_el[0]
                    related_data['image_url'] = img_el.get('src')
                    related_data['title'] = img_el.get('title')
                data['related_profiles'].append(related_data)

        return data

    def get_data(self, abs_url):
        response = requests.get(abs_url)
        response.raise_for_status()

        whoswho_id = abs_url.rsplit('-', 1)[-1]
        try:
            whoswho_id = int(whoswho_id)
        except ValueError:
            whoswho_id = None

        data = self.parse_content(response.text)
        data['whoswho_id'] = whoswho_id
        data['url'] = abs_url
        return data
