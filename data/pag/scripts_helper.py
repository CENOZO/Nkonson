def scrape_record(csv, i):
    """ Scrape data regarding a single listed company. """
    record = http_get(ISSUER, i).get('GetIssuerResult')
    if not record.get('LongName'):
        return
    log.info('Scraping: %s', record.get('LongName'))
    nob = http_get(BUSINESS, i).get('GetIssuerNatureOfBusinessResult')
    record['NatureOfBusiness'] = nob
    res = http_get(ASSOCIATED, i)
    assocs = res.get('GetIssuerAssociatedRolesResult', [])
    record['source_url'] = SOURCE_URL % i
    record.pop('Contacts', None)
    csv.write('jse_entities.csv', record)
    for assoc in assocs:
        assoc.pop('Contacts', None)
        assoc['source_url'] = record['source_url']
        csv.write('jse_entities.csv', assoc)
        link = {
            'SourceName': assoc.get('LongName'),
            'TargetName': record.get('LongName'),
            'Role': assoc.get('RoleDescription'),
            'source_url': record['source_url']
        }
        csv.write('jse_links.csv', link)




import requests
URL_PATTERN = 'https://www.ppaghana.org/contractdetail.asp?Con_ID=%s'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
url = URL_PATTERN % 432
try: 
    res = requests.get(url, headers=HEADERS)
except ConnectionError as e:
    z = e

print z



try:
    res = requests.get(url, headers=HEADERS)
except requests.exceptions.Timeout:
    # Maybe set up for a retry, or continue in a retry loop
except requests.exceptions.HTTPError:
    # Tell the user their URL was bad and try a different one
except requests.exceptions.RequestException as e:
    # catastrophic error. bail.
    print e
    sys.exit(1)





import pandas as pd
f3 = pd.read_csv("ppa_contracts3.csv")
f4 = pd.read_csv("ppa_contracts4.csv")
f5 = pd.read_csv("ppa_contracts5.csv")
f6 = pd.read_csv("ppa_contracts6.csv")
f7 = pd.read_csv("ppa_contracts7.csv")
f8 = pd.read_csv("ppa_contracts8.csv")
f = pd.concat([f3, f4, f5, f6, f7, f8])



import pandas as pd
ppa_contracts = pd.read_csv("ppa_contracts.csv")
f = pd.read_csv("f.csv")
f = pd.concat([f, ppa_contracts])
f.sort_values(['contract_id'], ascending=[True], inplace=True)
f["contract_signed_on"] = pd.to_datetime(f["contract_signed_on"])
f["estimated_contract_completion_date"] = pd.to_datetime(f["estimated_contract_completion_date"])
orig_len = len(f)
f.drop_duplicates(keep='first', inplace=True)
dedu_len = len(f)
print("Original length = %s ----- Deduplicate length = %s and de difference is: %s " % (orig_len, dedu_len, orig_len - dedu_len))
orig_len - dedu_len
f.to_csv("f.csv", index=False)
all = pd.Index(range(0,5067))
l = all.difference(f.contract_id)
len(l)


f = pd.read_csv("f.csv")
f["contract_id"].astype('category').describe()
f["contract_awarded_to"].astype('category').describe()
f["awarding_agency"].astype('category').describe()
f["awarding_ministry"].astype('category').describe()
f["tender_type"].astype('category').describe()



s = "Mr. Seth Adjei - Chairman\n\nMr. E. Kwasi Okoh - Managing Director\n\nTogbe Afede XIV - Member\n\nMr. Victor K. Djangmah - Member\n\nMr. Anthony Ebow Spio - Member\n\nProf. Lade Wosornu - Member\n\nMr. Kingsley O. Ofosu Obeng - Member\n\nMr.Joseph Simple Siilo - Member"
def remove_el(l, el):
   return [v for v in l if v != el]


s = s.split('\n')
s = remove_el(s, '')
s


persons = []
for el in s :
    p = {}
    p['name'] = el.split('-')[0].strip()
    p['position'] = el.split('-')[1].strip()
    persons.append(p)






ngos = pd.read_csv("ghanayello_ngos4.csv")
ngos_m = pd.read_csv("ghanayello_ngos.csv")
f2 = pd.concat([ngos, ngos_m])
f2.to_csv("f2.csv", index=False)

def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]



###### Split PAG data ##########
def split_pag_data():
    import pandas as pd
    pag_memberships = pd.read_csv("pag_data_memberships.csv")
    pag_persons = pag_memberships[['name','email', 'image_url', 'education', 'religion', 'date_birth', 'employment', 'hometown', 'data_source', 'scraped_time']]
    pag_persons = pag_persons.loc[pag_persons['name'].notnull()]
    pag_persons.sort_values(by='name', ascending=1)
    splitted = pag_persons['name'].str.rsplit(' ', 1)
    pag_persons['family_name'] = splitted.str[-1]
    pag_persons['given_name'] =  splitted.str[0]
    pag_persons.to_csv("pag_persons.csv", index=False)
    pag_parties = pag_memberships[['party_name', 'data_source', 'scraped_time']]
    pag_parties = pag_parties.loc[pag_parties['party_name'].notnull()]
    pag_parties['org_category'] = 'Party'
    pag_parties['legal_form'] = 'Political Party'
    pag_parties.drop_duplicates(keep='first', inplace=True)
    pag_parties.sort_values(by='party_name', ascending=1)
    pag_parties.to_csv("pag_parties.csv", index=False)
    pag_directorships = pd.read_csv("pag_data_directorships.csv")
    pag_companies = pag_directorships[['data_source', 'scraped_time', 'organization_type', 'company_name']]
    pag_companies.drop_duplicates(keep='first', inplace=True)
    pag_companies.sort_values(by='company_name', ascending=1)
    pag_companies.to_csv("pag_companies.csv", index=False)
    pag_partymemberships = pag_memberships[['name', 'party_name', 'data_source', 'scraped_time', 'constituency', 'party_status', 'region']]
    pag_partymemberships = pag_partymemberships.loc[pag_partymemberships['name'].notnull()]
    pag_partymemberships = pag_partymemberships.loc[pag_partymemberships['party_name'].notnull()]
    pag_partymemberships['role'] = 'Member'
    pag_partymemberships['start_date'] = ''
    pag_partymemberships['end_date'] = ''
    pag_partymemberships.to_csv("pag_partymemberships.csv", index=False)
    pag_companydirectorship = pag_directorships[['data_source', 'scraped_time', 'organization_type', 'company_name', 'position', 'date_position']]
    pag_companydirectorship.loc['end_date'] = ''
    pag_companydirectorship.to_csv("pag_companydirectorship.csv", index=False)


# Database scripts

DELETE FROM grano_property WHERE entity_id = 'betn406pf6w5uz1';
DELETE FROM grano_entity WHERE project_id = 5;

DELETE FROM grano_attribute WHERE id >= 275;
DELETE FROM grano_schema WHERE project_id = 5;



DELETE FROM grano_attribute WHERE schema_id >= 65;


def split_ppa_data():
    import pandas as pd
    ppa_data = pd.read_csv("ppaghana_contracts.csv")
    ppa_company = ppa_data[['contract_awarded_to','company_email', 'address', 'data_source']]
    ppa_company = ppa_company.loc[ppa_company['contract_awarded_to'].notnull()]
    ppa_company.drop_duplicates(subset='contract_awarded_to', keep='first', inplace=True)
    ppa_company["country"] = "Ghana"
    ppa_company["country_code"] = "GHA"
    ppa_company.to_csv("ppa_company.csv", index=False)



def clean_pag_companies():
    import pandas as pd
    pag_companies = pd.read_csv("pag_companies.csv")
    pag_companies = pag_companies.loc[pag_companies['company_name'].notnull()]
    pag_companies.drop_duplicates(subset='company_name', keep='first', inplace=True)
    pag_companies["country"] = "Ghana"
    pag_companies["country_code"] = "GHA"
    pag_companies.to_csv("pag_companies.csv", index=False)

def clean_pag_companydirectorship():
    import pandas as pd
    pag_companydirectorship = pd.read_csv("pag_companydirectorship.csv")
    pag_companydirectorship = pag_companydirectorship.loc[pag_companydirectorship['company_name'].notnull()]
    pag_companydirectorship = pag_companydirectorship.loc[pag_companydirectorship['name'].notnull()]
    pag_companydirectorship.drop_duplicates(subset=['company_name', 'name'], keep='first', inplace=True)
    pag_companydirectorship["country"] = "Ghana"
    pag_companydirectorship["country_code"] = "GHA"
    pag_companydirectorship.to_csv("pag_companydirectorship.csv", index=False)



def split_ppa_data():
    import pandas as pd
    ppa_data = pd.read_csv("ppaghana_contracts.csv")
    ppa_company = ppa_data[['contract_awarded_to','company_email', 'address', 'data_source']]
    ppa_company = ppa_company.loc[ppa_company['contract_awarded_to'].notnull()]
    ppa_company.drop_duplicates(subset='contract_awarded_to', keep='first', inplace=True)
    ppa_company["country"] = "Ghana"
    ppa_company["country_code"] = "GHA"
    ppa_company.to_csv("ppa_company.csv", index=False)
    ppa_agencies = ppa_data[['awarding_agency','awarding_agency_link', 'awarding_ministry', 'data_source']]
    ppa_agencies = ppa_agencies.loc[ppa_agencies['awarding_agency'].notnull()]
    ppa_agencies.drop_duplicates(subset='awarding_agency', keep='first', inplace=True)
    ppa_agencies["country"] = "Ghana"
    ppa_agencies["country_code"] = "GHA"
    ppa_agencies.to_csv("ppa_agencies.csv", index=False)
    ppa_contracts = ppa_data[['awarding_agency', 'awarding_agency_link', 'contract_awarded_to', 'contract_award_price', 'contract_id', 'contract_signed_on', 'contract_title', 'currency', 'estimated_contract_completion_date', 'tender_description', 'tender_lot_Numbers', 'tender_package_no', 'tender_type', 'data_source']]
    ppa_contracts = ppa_contracts.loc[ppa_contracts['contract_title'].notnull()]
    ppa_contracts = ppa_contracts.loc[ppa_contracts['awarding_agency'].notnull()]
    ppa_contracts = ppa_contracts.loc[ppa_contracts['contract_awarded_to'].notnull()]
    ppa_contracts.drop_duplicates(subset='contract_id', keep='first', inplace=True)
    ppa_contracts["country"] = "Ghana"
    ppa_contracts["country_code"] = "GHA"
    ppa_contracts.to_csv("ppa_contracts.csv", index=False)
    ppa_contracting = ppa_data[['awarding_agency', 'contract_awarded_to', 'contract_award_price', 'contract_signed_on', 'contract_title', 'currency', 'data_source']]
    ppa_contracting = ppa_contracting.loc[ppa_contracting['contract_title'].notnull()]
    ppa_contracting = ppa_contracting.loc[ppa_contracting['awarding_agency'].notnull()]
    ppa_contracting = ppa_contracting.loc[ppa_contracting['contract_awarded_to'].notnull()]
    ppa_contracting.drop_duplicates(subset='contract_title', keep='first', inplace=True)
    ppa_contracting["country"] = "Ghana"
    ppa_contracting["country_code"] = "GHA"
    ppa_contracting.to_csv("ppa_contracting.csv", index=False)


def two_decimals(a):
    return str("%.2f" % a)

import pandas as pd
ppa_contracting = pd.read_csv("ppa_contracting.csv")
ppa_contracting['contract_award_price'] = ppa_contracting['contract_award_price'].apply(two_decimals)
ppa_contracting.to_csv("ppa_contracting.csv", index=False)

