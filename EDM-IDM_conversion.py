import os
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON, XML, TURTLE, N3, RDF, RDFXML, CSV, TSV, JSONLD, DIGEST
import requests
from urllib import parse, error
import re

from rdflib import Graph, RDF, URIRef, Literal, BNode, Namespace
from rdflib.namespace import NamespaceManager,CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, VOID, XMLNS, XSD

# Local modules
import package.module_RDF_SPARQL as RDF_SPARQL
import package.module_list_files_folder as list_files_folder

format = 'turtle'
query_content = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX edm: <http://www.europeana.eu/schemas/edm/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX idm: <https://www.intavia.org/idm/>
PREFIX idmrole: <https://www.intavia.org/idm/role/>
PREFIX bioc: <http://ldf.fi/schema/bioc/>
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>
PREFIX schema: <http://schema.org/>
PREFIX psn: <http://www.wikidata.org/prop/statement/value-normalized/>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
CONSTRUCT {
    ?europeana_proxy 
        a crm:E24_Physical_Human_Made_Thing,
        idm:CHO_Proxy;
        # Note: according to Europeana, edm:Event has not implemented
        bioc:bearer_of ?choProductionEventRole;
        crm:P2_has_type ?dc_type;
        # There are several options, the most general node is mapped below. How to map dc:identifier? (there is potentially issues for the distinction between ID of digital (URI) and ID of pyhsical CHO (e.g. museum object number)) In case of Wikidata, how was the mapping done? Are there CHO proxies?
        crm:P1_is_identified_by ?dc_identifier;
        # What to map here (title or Description are mandatory and used for labels for ?item
        rdfs:label ?dc_title;
        # pasPart may not be URI
        crm:P45_consists_of ?dcterms_medium;
        crm:P62_depicts ?dc_subject;
        crm:P3_has_note ?dc_description;
        crm:P53_has_former_or_current_location ?edm_currentLocation;
        # isPartOf may not be URI (collection name etc)
        crm:P46_is_composed_of ?dcterms_isPartOf;
        crm:P128_carries ?cho_inscription .
    
    # the following would be needed for mapping
    # how to map dc:coverage and ?dc_coverage_uri ? Is it different from crm:P62:depicts? (dc:subject is more towards classifications)
    # how to map dc:format ?
    # how to map dc:source ?
    # how to map ?edm_webResource ?
    # how to map ?edm_object ?
    # how to map ?edm_isShownAt ?
    # how to map ?edm_isShownBy ?
    
    # What kind of image is this? (?item ?WebResource ?)
    ?edm_object crm:P70_documents ?europeana_proxy ;
        a crm:E31_Document.
    #How to map dc:identifier? 
    ?item rdfs:label ?dc_title;
        a crm:E35_Title .
    ?item_id rdfs:label ?dc_identifier;
        a crm:E42_Identifier .
    # pasPart may not be URI
    ?dcterms_hasPart crm:P46_is_composed_of ?europeana_proxy  .
    # pasPart may not be URI. Also not sure if label is always given
    ?edm_currentLocation a crm:E53_Place.
    ?edm_currentLocation rdfs:label ?locationLabel.
    # To include dc:language
    ?cho_inscription crm:P190_has_symbolic_content ?inscription.
    ?cho_inscription a crm:E90_Symbolic_Object.
    # Something like Linguistic Object might be needed to include dc:language?
    ?cho_linguistic_object a crm:E33_Linguistic_Object. 
    ?cho_linguistic_object crm:P72_has_language ?cho_language.
    ?cho_language a crm:E56_Language; rdfs:label ?dc_language.
    # How to map when there are sometimes several types for type labels (as well as "normalised" controlled vocabukary in URIs). 
    # Note that such URIs are optional and "normalised" controlled vocabukary in URIs are not always 100% corresponding to labels (e.g. could be different language)
    ?dc_type_uri
        rdfs:label ?dc_type.

    # Note: according to Europeana, edm:Event has not implemented (where comes creators and contributors in Production Event?)
    ?choProductionEventRole a bioc:Thing_Role .
    ?choProductionEvent bioc:occured_in_the_presence_of_in_role ?choProductionEventRole.
    ?choProductionEvent a crm:E12_Production.
    ?choProductionEvent crm:P4_has_time-span ?choProductionTimespan.
    ?choProductionTimespan rdfs:label ?dc_date.
    # Location would be implicit in Europeana data
    ?choProductionEvent crm:P7_took_place_at ?locationofcreation.
    ?locationofcreation a crm:E53_Place;
        rdfs:label ?locationofcreationLabel.
    ?choProductionEvent bioc:had_participant_in_role ?producingArtistRole .
    ?artist bioc:bearer_of ?producingArtistRole .
    ?producingArtistRole a idmrole:producing_artist,
        idmrole:producing_artist ; 
        rdfs:label "producing artist"@en .
    # medium would not have URI
    ?dcterms_medium rdfs:label ?dcterms_medium.
    ?depictedSubject rdfs:label ?dsubjectLabel;
        crm:P2_has_type ?dsubjectclass.
    # According to Europeana, edm:Event has not implemented
    ?cho_measurement_event a crm:E16_Measurement.
    ?cho_measurement_event crm:P39_measured ?europeana_proxy ;
        crm:P40_observed_dimension ?dcterms_extent .

    # It would not be easy to map, as dimensions are often strings including unit
    ?cho_dimension_height a crm:E54_Dimension;
        crm:P91_has_unit ?qunit;
        rdfs:label ?heightvalue;
        crm:P2_has_type wd:Q208826.
    ?cho_dimension_width a crm:E54_Dimension;
        crm:P91_has_unit ?qunit;
        crm:P2_has_type wd:Q35059;
        rdfs:label ?widthtvalue.
    ?qunit a crm:E58_Measurement_Unit.

    # It is possible to try to use digital collection, ("collection" from the viewpoint of Europeana i.e. aggregation), but the physical collection (of museums) would be normally in encoded in dcterms:isPartOf
    ?collection a crm:E78_Curated_Holding;
        crm:P46_is_composed_of ?europeana_proxy ;
        rdfs:label ?collectionLabel.

}
{
            #?artist owl:sameAs ?artistUri .
        ?dc_creator_uri owl:sameAs ?artistUri .
        ?europeana_proxy dc:creator ?dc_creator_uri .
        OPTIONAL {?europeana_proxy dc:coverage ?dc_coverage_uri}
        OPTIONAL {?europeana_proxy dc:type ?dc_type_uri }
        # Shortcut technique to avoid hopping many nodes (for the 2 subqueries below and )
                        BIND(IRI(REPLACE(str(?europeana_proxy), "http://data.europeana.eu/proxy/europeana/", "http://data.europeana.eu/proxy/provider/")) AS ?provider_proxy)
                        BIND(IRI(REPLACE(str(?europeana_proxy), "http://data.europeana.eu/proxy/europeana/", "http://data.europeana.eu/aggregation/provider/")) AS ?provider_agg)
                        BIND(IRI(REPLACE(str(?europeana_proxy), "http://data.europeana.eu/proxy/europeana/", "http://data.europeana.eu/item/")) AS ?item)
                            {select DISTINCT ?provider_proxy ?dc_creator ?dc_contributor ?dc_coverage ?dc_date ?dc_description ?dc_format ?dcterms_hasPart ?dc_identifier ?dcterms_isPartOf ?dc_language ?dc_source ?dc_subject ?dc_title ?dc_type ?dcterms_extent ?dcterms_medium ?edm_currentLocation ?edm_type
                        where {
                            ?provider_proxy edm:type ?edm_type
                            OPTIONAL {?provider_proxy dc:creator ?dc_creator}
                            OPTIONAL {?provider_proxy dc:contributor ?dc_contributor}
                            OPTIONAL {?provider_proxy dc:coverage ?dc_coverage}
                            OPTIONAL {?provider_proxy dc:date ?dc_date}
                            OPTIONAL {?provider_proxy dc:description ?dc_description}
                            OPTIONAL {?provider_proxy dc:format ?dc_format}
                            OPTIONAL {?provider_proxy dcterms:hasPart ?dcterms_hasPart}
                            OPTIONAL {?provider_proxy dc:identifier ?dc_identifier}
                            OPTIONAL {?provider_proxy dcterms:isPartOf ?dcterms_isPartOf}
                            OPTIONAL {?provider_proxy dc:language ?dc_language}
                            OPTIONAL {?provider_proxy dc:source ?dc_source}
                            OPTIONAL {?provider_proxy dc:subject ?dc_subject}
                            OPTIONAL {?provider_proxy dc:title ?dc_title}
                            OPTIONAL {?provider_proxy dc:type ?dc_type}
                            OPTIONAL {?provider_proxy dcterms:extent ?dcterms_extent}
                            OPTIONAL {?provider_proxy dcterms:medium ?dcterms_medium}
                            OPTIONAL {?provider_proxy edm:currentLocation ?edm_currentLocation}
                            }
                        }
{select DISTINCT ?provider_agg ?edm_rights ?edm_webResource ?edm_object ?edm_isShownAt ?edm_isShownBy
                        where {
                            ?provider_agg edm:rights ?edm_rights
                            OPTIONAL {?provider_agg edm:hasView ?edm_webResource}
                            OPTIONAL {?provider_agg edm:object ?edm_object}
                            OPTIONAL {?provider_agg edm:isShownAt ?edm_isShownAt}
                            OPTIONAL {?provider_agg edm:isShownBy ?edm_isShownBy}
                        }
                    }
}
"""

# Load InTaVia data which contains persons with Wikidata URI
i_file = 'InTaVia_all_persons_with_WikidataURI_query_results.ttl'

# Load Europeana data from a specific folder
dir_path = 'EuropeanaObjectTurtle/test/Creator/OnlyInTaVia_at_nl_fi_si_URI_list_df_WikidataCreator_60000.csv/'
include_files_regex = ''
exclude_files_regex = ''
targetfiles = list_files_folder.list_files_in_folder(dir_path, include_files_regex, exclude_files_regex)
#targetfiles = targetfiles[0:4]
#targetfiles = ['EuropeanaObjectTurtle/test/Creator/OnlyInTaVia_at_nl_fi_si_URI_list_df_WikidataCreator_0.csv/http:__data.europeana.eu_proxy_europeana_04202_BibliographicResource_3000135649715.ttl']
print(targetfiles)

for e_file in targetfiles:
    # One graph (g) for loading all graphs, one graph (g2) for query result (output graph)
    g = Graph()
    g2 = Graph()
    # Define custom namespaces for output graph
    edm = Namespace('http://www.europeana.eu/schemas/edm/')
    g2.bind('edm',edm)
    crm = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
    g2.bind('crm',crm)
    wdt = Namespace('http://www.wikidata.org/prop/direct/')
    g2.bind('wdt',wdt)
    p = Namespace('http://www.wikidata.org/prop/')
    g2.bind('p',p)
    wikibase = Namespace('http://wikiba.se/ontology#')
    g2.bind('wikibase',wikibase)
    bd = Namespace('http://www.bigdata.com/rdf#')
    g2.bind('bd',bd)
    idm = Namespace('https://www.intavia.org/idm/')
    g2.bind('idm',idm)
    idmrole = Namespace('https://www.intavia.org/idm/role/')
    g2.bind('idmrole',idmrole)
    bioc = Namespace('http://ldf.fi/schema/bioc/')
    g2.bind('bioc',bioc)
    psv = Namespace('http://www.wikidata.org/prop/statement/value/')
    g2.bind('psv',psv)
    schema = Namespace('http://schema.org/')
    g2.bind('schema',schema)
    psn = Namespace('http://www.wikidata.org/prop/statement/value-normalized/')
    g2.bind('psn',psn)
    wds = Namespace('http://www.wikidata.org/entity/statement/')
    g2.bind('wds',wds)
    pq = Namespace('http://www.wikidata.org/prop/qualifier/')
    g2.bind('pq',pq)

    # Load InTaVia data which contains persons with Wikidata URI
    RDF_SPARQL.load_graph(g, i_file, format)
    #RDF_SPARQL.serialize_graph(g, format)
    print(f'STARTED: {e_file}')
    #outputfile = f'{dir_path}{item}_converted.ttl'
    outputfile = f'{dir_path}{e_file}_converted.ttl'
    try:
        RDF_SPARQL.load_graph(g, f'{dir_path}{e_file}', format)
        RDF_SPARQL.serialize_graph(g, format)
        try:
            RDF_SPARQL.query_graph(g, g2, query_content)   
            try:
                RDF_SPARQL.save_graph(g2, outputfile, format)
            except:
                print('ERROR for saving graph')
        except:
            print('ERROR for querying graph')
        # Clear all graphs (just in case) before starting
        RDF_SPARQL.remove_graph(g)
        RDF_SPARQL.remove_graph(g2)        
    except:
        print('ERROR for loading graphs')