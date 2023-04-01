import argparse
import shutil
 
parser = argparse.ArgumentParser()
parser.add_argument('--infile', type=str, required=True)
#parser.add_argument('--outfile', type=str, required=True)
args = parser.parse_args()
name = str(args.infile).replace('.csv', '')
 
# Copy the file with new name
shutil.copyfile(args.infile, name + '_new.csv')


