import os
from pathlib import Path
#from SPARQLWrapper import SPARQLWrapper, JSON, XML, TURTLE, N3, RDF, RDFXML, CSV, TSV, JSONLD, DIGEST
#import pandas as pd
import requests
from urllib import parse, error
#from rdfpandas.graph import to_graph, to_dataframe
from rdflib import Graph, RDF, URIRef, Literal, BNode, Namespace
from rdflib.namespace import NamespaceManager,CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, VOID, XMLNS, XSD

# Define Prefix for SPARQL query
namesapce_prefix = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX schema: <http://schema.org/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX dbc: <http://dbpedia.org/resource/Category:>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbt: <http://dbpedia.org/resource/Template:>
    PREFIX dbyago: <http://dbpedia.org/class/yago/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX gnd: <http://d-nb.info/gnd/>
    PREFIX gold: <http://purl.org/linguistics/gold/>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX umbelrc: <http://umbel.org/umbel/rc/>
    PREFIX viaf: <http://viaf.org/viaf/>
    PREFIX ore: <http://www.openarchives.org/ore/terms/>
    PREFIX edm: <http://www.europeana.eu/schemas/edm/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdata: <http://www.wikidata.org/wiki/Special:EntityData/>
    PREFIX wdno: <http://www.wikidata.org/prop/novalue/>
    PREFIX wdref: <http://www.wikidata.org/reference/>
    PREFIX wds: <http://www.wikidata.org/entity/statement/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX wdtn: <http://www.wikidata.org/prop/direct-normalized/>
    PREFIX wdv: <http://www.wikidata.org/value/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX eventKG-s: <http://eventKG.l3s.uni-hannover.de/schema/>
    PREFIX eventKG-e: <http://eventKG.l3s.uni-hannover.de/resource/>
"""

def add_namespaces(graph, prefix, var, url):
    prefix = Namespace(url)
    graph.bind(var, prefix)

def load_graph(graph, inputfile, format):
    with open(inputfile, 'r', encoding='utf8') as f:
        graph.load(f, format=format)

def remove_graph(graph):
    for triple in graph:
        graph.remove(triple)

def serialize_graph(graph, format):
    #print(g.serialize(format=format).decode('utf-8'))
    print(graph.serialize(format=format))

def save_graph(graph, outputfile, format):
    #query_result
    graph.serialize(destination=outputfile, format=format)

def query_graph(inputgraph, outputgraph, query_content):
    query_result = inputgraph.query(f'{namesapce_prefix}{query_content}')
    for row in query_result:
        print(row)
        outputgraph.add(row)
    print(query_result)
    return(query_result)

def sparqlwrapper_set_endpoint(endpointurl):
    sparql = SPARQLWrapper(endpointurl)
    return sparql

def rdfpandas_make_df(graph, inputfile, format):
    graph.parse(inputfile, format=format)
    df = to_dataframe(graph)
    print(df)
    return df
