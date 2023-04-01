# %% [markdown]
# # Python scripts to generate metadata for Europeana objects which are created by persons (dc:creator, DBpedia URIs)

# %%
%pip install SPARQLWrapper
%pip install pandas
%pip install numpy
%pip install fsspec
%pip install rdfpandas

# %%
import os
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON, XML, TURTLE, N3, RDF, RDFXML, CSV, TSV, JSONLD, DIGEST
import pandas as pd
from random import randint
import numpy as np
import requests
from urllib import parse, error
import fsspec
from rdfpandas.graph import to_graph, to_dataframe
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import NamespaceManager,CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, VOID, XMLNS, XSD

# For multithreading
#import concurrent.futures
from concurrent import futures
import threading
# For time recording
import time
import datetime
from datetime import timedelta


# Specify file location (Google Colab and local)
filelocation_google = '/content/drive/MyDrive/Colab Notebooks/InTaVia/'
filelocation_local = 'WikidataObjectTurtle/'


def second_query4(europeanaURI):
  headers = {
    'Accept': 'text/turtle',
    'Content-type': 'text/turtle'
  }
  r = requests.get(europeanaURI, headers=headers)
  try:
    print(r.raise_for_status())
    return(r.text)
  except requests.exceptions.HTTPError as e: 
    print(e)
    return

# %%
# folder path to CSV files
dir_path = filelocation_google + 'EuropeanaObjectURIlist/Creator'
# Create an empty list
list_file = []
# Iterate in the folder
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        list_file.append(path)
list_file.sort()
print(list_file)


# %% [markdown]
# **MULTI-THREADING New way with HTTP request: 2nd Queries to fetch CH object metadata (Caution long processing time!)**

# %%
# Test with 1 iteration
#n4 = np.array([770000])
#n4 = np.array(list_file[-2:])
#print(n4)
list_file = list_file[0:2]
print(list_file)

def multiple_files_download(list_file):
  i = 0
  for n in list_file:
    print(f'Processing {str(n)} started as no {str(i)}')
    URI_list_df  = pd.read_csv(f'{filelocation_google}/EuropeanaObjectURIlist/Creator/{n}')
    list_Europeana_proxy = (URI_list_df['Europeana_proxy']).to_list()
    #list_Wikidata_URI = (URI_list_df['Wikidata_URI']).to_list()
    list_Europeana_proxy = list_Europeana_proxy[0:10]
    #list_Wikidata_URI = list_Wikidata_URI[0:10]
    print(list_Europeana_proxy)
    # Create directory for each iterated file
    folder_path = os.path.join(f'{filelocation_google}/EuropeanaObjectTurtle/test/', str(n))
    os.mkdir(folder_path)

    def singlefile_download(item):
      print(f'Processing {str(item)} started')
      #print(var2)
      #print(list_DBpedia_URI[i])
      turtle_europeana = second_query4(item)
      # Check if turtle file was fetched
      if turtle_europeana != None:
        filename = item.replace('/', '_')
        print(f'{filename} is fetched')
        path_to_file = f'{folder_path}/{str(filename)}.ttl'
        path = Path(path_to_file)
        # Check if the (same) turtle file was already saved 
        if path.is_file():
          print(f'The file {path_to_file} already exists, thus no need to save and download to local')
        else:
          # Download ttl to GoogleDrive
          with open(path_to_file, 'w') as f:
            f.write(turtle_europeana)
          # Download ttl to local machine
          #files.download(filelocation_google + 'EuropeanaObjectTurtle/test/' + str(filename) + '.ttl')
          print(f'The file {path_to_file} does not exist, thus saved and download to local')
      else:
        pass
        print(f'No Turtle can be fetched from {str(item)}')
      print(f'Processing {str(item)} completed')
      #Time interval for a next query/iteration
      #time.sleep(2)
      print('-----------------')

    #### Multithreading below
    t1 = time.perf_counter()
    now1 = datetime.datetime.now()
    #Initiate max 40 threads (i.e. workers) 
    #ex = futures.ThreadPoolExecutor(max_workers=40)
    ex = futures.ThreadPoolExecutor()
    print('{}: is starting work'.format(threading.current_thread().getName()))
    #Start the threads with the map method
    results = ex.map(singlefile_download, list_Europeana_proxy)
    #print('{}: is waiting for the results'.format(threading.current_thread().getName()))
    real_results = list(results)
    print('main: results: {}'.format(real_results))
    t2 = time.perf_counter()
    now2 = datetime.datetime.now()
    duration_seconds = round(t2 - t1, 3)
    duration = str(timedelta(seconds=duration_seconds))
    nl = '\n'
    # Save the time recording log
    with open(f'{folder_path}/log_threading.txt', 'w') as f:
        f.write(f'THREADING: {nl} Start time  {now1.strftime("%Y-%m-%d %H:%M:%S")} {nl} Finish time {now2.strftime("%Y-%m-%d %H:%M:%S")} {nl} Duration: {duration} = {duration_seconds} seconds')
    print(f'========================================================')
    print(f'THREADING {nl} Start time  {now1.strftime("%Y-%m-%d %H:%M:%S")} {nl} Finish time {now2.strftime("%Y-%m-%d %H:%M:%S")} {nl} Duration: {duration} = {duration_seconds} seconds')
    print(f'========================================================')

    i = i + 1

multiple_files_download(list_file)