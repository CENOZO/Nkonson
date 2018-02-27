from apikit import Pager
from connectedafrica import util
from connectedafrica.core import grano, schemata
from connectedafrica.util.properties import Properties
from granoclient import Grano
from connectedafrica.scrapers.util import MultiCSV



def load_relations(entity, id, slug):
    relation_sections = []
    q = grano.relations.query().limit(0)
    print(q.total)
    q = q.filter('facet', 'schema').filter('entity', id)
    print(q.total)
    schema_types = q.data.get('facets', {}).get('schema', {})
    for (schema, count) in schema_types.get('results', []):
        iq = grano.relations.query().limit(15)
        iq = iq.filter('entity', id)
        iq = iq.filter('schema', schema.get('name'))
        pager = Pager(iq, name=schema.get('name'), id=id, slug=slug)
        relations = []
        for r in pager:
            r.props = Properties(r)
            r.other = r.source if r.target.id == id else r.target
            relations.append(r)

        data = {
            'schema': schemata.by_name(schema.get('name')),
            'count': count,
            'pager': pager,
            'relations': relations
        }

        relation_sections.append(data)

    return sorted(relation_sections,
                  key=lambda r: r['schema'].label)



def get_degree(entity, relations, relations_schema=None):
    degree_in = 0
    degree_out = 0
    for relation in relations:
        if relation.get("source").get('id') == entity.get("id"):
            degree_in += 1
        if relation.get("target").get('id') == entity.get("id"):
            degree_out += 1
    degree = degree_in + degree_out
    return { "degree_in": degree_in, "degree_out": degree_out, "degree": degree}


def select_entities(schema=None):
    if schema :
        q = grano.entities.query().filter('schema', schema)
    else: 
        q = grano.entities.query()
    total = q.total
    offset = 0
    limit = 500
    entities = []
    while (offset <= total):
        if schema:
            q = grano.entities.query().filter('schema', schema).limit(limit).offset(offset)
        else:
            q = grano.entities.query().limit(limit).offset(offset)
        for e in q.data.get("results"): entities.append(e)
        offset += limit
    return entities


def select_relations(schema=None):
    if schema : 
        q = grano.relations.query().filter('schema', schema)
    else : 
        q = grano.relations.query()
    total = q.total
    offset = 0
    limit = 500
    relations = []
    while (offset <= total):
        if schema : 
            q = grano.relations.query().filter('schema', schema).limit(limit).offset(offset)
        else:
            q = grano.relations.query().limit(limit).offset(offset)
        for e in q.data.get("results"): relations.append(e)
        offset += limit
    return relations


def set_degrees(entities, csv):
    i = 0
    relations = select_relations()
    for ent in entities:
        i +=1
        entity = grano.entities.by_id(ent.get('id'))
        p = {
            "id": ent.get('id'),
            "degree_in": get_degree(entity, relations).get("degree_in"),
            "degree_out": get_degree(entity, relations).get("degree_out"),
            "degree": get_degree(entity, relations).get("degree")
        }
        print("\n\n\n\n################################## i = " + str(i) + " ###################")
        print (p)
        csv.write('degrees/degrees.csv', p)
    entities = sorted(entities, key=lambda k: k['degree'], reverse=True)
    return entities

#  function that gets country name from country code
def get_country_name(country_code):
    if (country_code=="GHA"): country_name = "Ghana"
    elif  (country_code=="BFA"): country_name = "Burkina Faso"
    elif  (country_code=="NIG"): country_name = "Niger"
    elif  (country_code=="NGR"): country_name = "Nigeria"
    elif  (country_code=="MAL"): country_name = "Mali"
    elif  (country_code=="SEN"): country_name = "Senegal"
    elif  (country_code=="RCI"): country_name = "Cote d'Ivoire"
    elif  (country_code=="BEN"): country_name = "Benin"
    elif  (country_code=="TOG"): country_name = "Togo"
    elif  (country_code=="LIB"): country_name = "Liberia"
    elif  (country_code=="SLE"): country_name = "Sierra Leone"
    elif  (country_code=="GUI"): country_name = "Guinea"
    elif  (country_code=="MAU"): country_name = "Mauritania"
    else: country_name = ""
    return country_name

