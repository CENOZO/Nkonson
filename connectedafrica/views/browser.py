from flask import Blueprint, render_template, request
from apikit import Pager

from connectedafrica.core import grano, schemata
from connectedafrica.util.relations import get_country_name

blueprint = Blueprint('browser', __name__)


@blueprint.route('/search')
def view():
        query = grano.entities.query()
        query = query.filter('q', request.args.get('q', ''))
        schema_active = request.args.getlist('schema')
        country_active = request.args.getlist('country')
        country_name = None
        main_schema = None
        if not len(schema_active):
            # TODO: get this from schema 'meta':
            schema_active = ['Person', 'Organization', 'Company', 'Agency', 'NonProfit', 'EducationalInstitution']
        else:
            main_schema = schemata.by_name(schema_active[0])

        if country_active: 
            query = query.filter('property-country_code', country_active)
            country_name = get_country_name(country_active[0])

        query = query.filter('schema', schema_active)
        query = query.filter('sort', '-degree')
        query = query.limit(10)
        pager = Pager(query, limit=10)
        if query.data['results'] :
            entity = query.data['results'][0]
        else :
            entity = None 
            print("NOOOOOOO Result")
        
        return render_template('data_browser.html',
                               main_schema=main_schema,
                               pager=pager,
                               entity=entity,
                               country_active= country_active,
                               country_name = country_name)

