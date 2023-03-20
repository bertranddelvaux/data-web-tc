import os
import json
import pandas as pd
import argparse


def mappingPopulation2parquet(mapping_file, mapping_population_file, cols):

    with open(mapping_file, 'r') as f:
        mapping = json.load(f)

    with open(mapping_population_file, 'r') as f:
        mappingPopulation = json.load(f)

    [mapping[key].append(mappingPopulation[key]) for key in mapping.keys()]

    df = pd.DataFrame.from_dict({int(key): value for key, value in mapping.items()}, orient='index', columns=cols)
    df[cols[-1]]

    parquetFilePath = f'{os.path.splitext(os.path.basename(mapping_file))[0]}.gzip'

    df.to_parquet(parquetFilePath, index=True, compression='gzip')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-m', '--mappingfile', type=str, help='Path to mapping file', default='mapping.json', dest='mapping_file')
    parser.add_argument('-p', '--mappingpopulationfile', type=str, help='Path to mapping population file', default='mappingPopulation.json', dest='mapping_population_file')
    parser.add_argument('-c', '--cols', help='List of columns for csv', nargs='+', default=['adm0_code', 'adm1_code', 'adm2_code', 'population'], dest='cols')

    args = parser.parse_args()

    mappingPopulation2parquet(mapping_file=args.mapping_file, mapping_population_file=args.mapping_population_file, cols=args.cols)