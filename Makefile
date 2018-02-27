export GRANO_HOST=http://grano.nanoapp.io
export GRANO_PROJECT=nkonson-0001
export GRANO_APIKEY=5oj3akecjci1tj5


# load: loadschema loadpag

# install:
# 	bower install


loadschema:
	@granoloader --create-project schema data/schema.yaml


#loadpag:
#	@granoloader csv -t 5 data/pag/pag_persons.csv.yaml data/pag/pag_persons.csv
#	@granoloader csv -t 5 data/pag/pag_parties.csv.yaml data/pag/pag_parties.csv
#	@granoloader csv -t 5 data/pag/pag_partymemberships.csv.yaml data/pag/pag_partymemberships.csv
#	@granoloader csv -t 5 data/pag/pag_companies.csv.yaml data/pag/pag_companies.csv
#	@granoloader csv -t 5 data/pag/pag_companydirectorship.csv.yaml data/pag/pag_companydirectorship.csv


# loadppa:
#	@granoloader csv -t 5 data/ppa/ppa_company.csv.yaml data/ppa/ppa_company.csv
#	@granoloader csv -t 5 data/ppa/ppa_agencies.csv.yaml data/ppa/ppa_agencies.csv
# 	@granoloader csv -t 5 data/ppa/ppa_contracts.csv.yaml data/ppa/ppa_contracts.csv
# 	@granoloader csv -t 5 data/ppa/ppa_contracting.csv.yaml data/ppa/ppa_contracting.csv

# loadgse:
# 	@granoloader csv -t 5 data/gse/gse_company_profiles.csv.yaml data//gse/gse_company_profiles.csv
# 	@granoloader csv -t 5 data/gse/gse_directors.csv.yaml data//gse/gse_directors.csv
# 	@granoloader csv -t 5 data/gse/gse_directorship.csv.yaml data//gse/gse_directorship.csv