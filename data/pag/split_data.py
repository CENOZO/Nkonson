def split_data():
    import pandas as pd
    data = pd.read_csv("nkonson.csv")
    data["country"] = "Ghana"
    data["country_code"] = "GHA"
    gse_company_profiles = data[data["File"] == "gse_company_profiles.csv"]
    gse_company_profiles = gse_company_profiles[['country', 'country_code', 'telephone', 'scraped_time', 'registered_office', 'comments', 'issued_shares', 'company_name', 'email', 'website', 'fax', 'postal_address', 'symbol', 'change_of_name', 'types_of_traded_securities', 'security', 'authorised_shares', 'data_source', 'date_incorporated', 'date_listed', 'incorporation_comments', 'directors', 'nature_of_business', 'stated_capital']]
    gse_company_profiles["industry"] = "NA"
    gse_company_profiles.to_csv("gse_company_profiles.csv", index=False)
    gse_directors = data[data["File"] == "gse_directors.csv"]
    gse_directors = gse_directors[['country', 'country_code', 'position', 'data_source', 'scraped_time', 'person_name', 'company_name']]
    gse_directors.to_csv("gse_directors.csv", index=False)
    gse_directorship = data[data["File"] == "gse_directorship.csv"]
    gse_directorship = gse_directorship[['country', 'country_code', 'position', 'data_source', 'scraped_time', 'person_name', 'company_name']]
    gse_directorship.to_csv("gse_directorship.csv", index=False)
    pag_companies = data[data["File"] == "pag_companies.csv"]
    pag_companies = pag_companies[['country', 'country_code', 'data_source', 'scraped_time', 'organization_type', 'company_name']]
    pag_companies["industry"] = "NA"
    pag_companies.to_csv("pag_companies.csv", index=False)
    pag_companydirectorship = data[data["File"] == "pag_companydirectorship.csv"]
    pag_companydirectorship = pag_companydirectorship[['country', 'country_code', 'data_source', 'scraped_time', 'person_name', 'organization_type', 'company_name', 'position', 'date_position']]
    pag_companydirectorship.to_csv("pag_companydirectorship.csv", index=False)
    pag_parties = data[data["File"] == "pag_parties.csv"]
    pag_parties = pag_parties[['country', 'country_code', 'party_name', 'data_source', 'scraped_time', 'org_category', 'legal_form']]
    pag_parties.to_csv("pag_parties.csv", index=False)
    pag_partymemberships = data[data["File"] == "pag_partymemberships.csv"]
    pag_partymemberships = pag_partymemberships[['country', 'country_code', 'person_name', 'party_name', 'data_source', 'scraped_time', 'constituency', 'party_status', 'region', 'role', 'start_date', 'end_date']]
    pag_partymemberships.to_csv("pag_partymemberships.csv", index=False)
    pag_persons = data[data["File"] == "pag_persons.csv"]
    pag_persons = pag_persons[['country', 'country_code', 'person_name', 'email', 'image_url', 'education', 'religion', 'date_birth', 'employment', 'hometown', 'data_source', 'scraped_time', 'family_name', 'given_name']]
    pag_persons.to_csv("pag_persons.csv", index=False)
    ppa_agencies = data[data["File"] == "ppa_agencies.csv"]
    ppa_agencies = ppa_agencies[['country', 'country_code', 'agency_name', 'awarding_agency_link', 'ministry_name', 'data_source']]
    ppa_agencies["industry"] = "NA"
    ppa_agencies.to_csv("ppa_agencies.csv", index=False)
    ppa_company = data[data["File"] == "ppa_company.csv"]
    ppa_company = ppa_company[['country', 'country_code', 'company_name', 'company_email', 'address', 'data_source']]
    ppa_company["industry"] = "NA"
    ppa_company.to_csv("ppa_company.csv", index=False)
    ppa_contracting = data[data["File"] == "ppa_contracting.csv"]
    ppa_contracting = ppa_contracting[[ 'country', 'country_code', 'agency_name', 'company_name', 'contract_award_price', 'contract_signed_on', 'contract_title', 'contract_id_title', 'currency', 'data_source']]
    ppa_contracting["industry"] = "NA"
    ppa_contracting.to_csv("ppa_contracting.csv", index=False)
    ppa_contracts = data[data["File"] == "ppa_contracts.csv"]
    ppa_contracts = ppa_contracts[['country', 'country_code', 'agency_name', 'awarding_agency_link', 'company_name', 'contract_award_price', 'contract_id', 'contract_signed_on', 'contract_title', 'contract_id_title', 'currency', 'estimated_contract_completion_date', 'tender_description', 'tender_lot_numbers', 'tender_package_no', 'tender_type', 'data_source']]
    ppa_contracts["industry"] = "NA"
    ppa_contracts.to_csv("ppa_contracts.csv", index=False)
