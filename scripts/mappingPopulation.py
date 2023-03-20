import argparse
import json
import pandas as pd
import geopandas as gpd

def csv2json(csvFile, mappingFile):

    df = pd.read_csv(csvFile, header=None)
    mapping = dict(zip(df[0],df[13]))

    with open(mappingFile, 'w') as f:
        f.write(json.dumps(mapping, separators=(',', ':')))



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-c', '--csv', type=str, help='Path to csv file', default='arc_consolidated_expo.csv', dest='csvFile')
    parser.add_argument('-m', '--mapping', type=str, help='mapping JSON file', default='mappingPopulation.json', dest='mappingFile')
    args = parser.parse_args()

    csv2json(csvFile=args.csvFile, mappingFile=args.mappingFile)

