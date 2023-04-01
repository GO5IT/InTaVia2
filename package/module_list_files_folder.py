# List files in a folder
# input regex for include and exclude files
# output: file list

import os
from pathlib import Path
from natsort import natsorted
import unicodedata
import re

def list_files_in_folder(dir_path, include_files_regex, exclude_files_regex):
    # folder path to CSV files
    allfiles = os.listdir(dir_path)
    allfiles.sort()
    allfiles = natsorted(allfiles)
    print(f'--- All files in folder: {len(allfiles)} ---')
    print(allfiles)

    # Exclude items
    regex_ex = re.compile(exclude_files_regex)
    rest1 = [i for i in allfiles if regex_ex.findall(i)]
    print(f'--- 1) Exclude filter: no of excluding files = {len(rest1)} ---')
    rest1.sort()
    rest1 = natsorted(rest1)
    print(f'Remaining: {rest1}')
    excluded = [i for i in allfiles if not regex_ex.findall(i)]
    excluded.sort()
    excluded = natsorted(excluded)
    print(f'Excluded: {excluded}')

    # Include items
    regex_in = re.compile(include_files_regex)
    rest2 = [item for item in rest1 if regex_in.findall(item)]
    print(f'--- 2) Include filter no of including files = {len(rest2)} ---')
    # Apply UTF-8 sorting
    rest2.sort()
    rest2 = natsorted(rest2)
    print(f'Included (final outcome): {rest2}')
    #rest = [ii.str.normalize('NFKC').argsort() for ii in rest]
    #df_aggregate = df_aggregate.iloc[df_aggregate['Person_agg'].str.normalize('NFKD').argsort()]
    # Apply natural sorting (numbering etc)
    #rest_sorted = natsorted(rest)
    return rest2