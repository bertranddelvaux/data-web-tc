#!/usr/bin/python3
#######################################################################
# Python3 based generation of unique mapping exp_id -> (adm0,adm1,adm2)
# Version 1.1
# Copyright (c) 2021, Bertrand Delvaux
#
# Parameters:
#       --csv: path to arc_consolidated_expo.csv
#       --adm2 : path to adm2.json
#
# Examples:
#       * generateMapping.py
#       * generateMapping.py --csv arc_consolidated_expo.csv
#

import argparse
import json
import geopandas as gpd

def zip2geojson(zip, adm2, mappingFile):

    # reading shapefile (zip), adm2 geojson
    expo_gdf = gpd.read_file(zip) #, rows=10000)
    adm2_gdf = gpd.read_file(adm2)

    # keep only a few columns
    expo_gdf.drop(columns = ['ADMIN_ID', 'CTRY_ID', 'EXP_CODE'], inplace=True)

    # loop through countries
    for i, country in enumerate(expo_gdf.COUNTRY.unique()):
        #if country == 'Comoros': # REMOVE!!!!

        # initiate mapping dictionary
        mapping = {}

        print(f'Dealing with {country}...')

        # filtering both GeoDataFrames based on country
        gdf_country = expo_gdf[expo_gdf.COUNTRY == country]
        gdf_adm2_country = adm2_gdf[adm2_gdf.ADM0_NAME == country]

        for index, row in gdf_country.iterrows():
            exp_id = row.EXPOSURE_I
            gdf_join = gpd.sjoin_nearest(gdf_country[gdf_country.EXPOSURE_I == exp_id], gdf_adm2_country)

            adm0_code = gdf_join.ADM0_CODE.iloc[0]
            adm1_code = gdf_join.ADM1_CODE.iloc[0]
            adm2_code = gdf_join.ADM2_CODE.iloc[0]

            # UNCOMMENT for debugging
            # if adm1_name != row.ADMIN_NAME and row.ADMIN_NAME is not None:
            #     print(f'{row.ADMIN_NAME} -> {adm1_name}')
            #     print(f'{index} | exp_id: {exp_id} | adm0: {adm0_name} | adm1: {adm1_name} | adm2: {adm2_name}')

            # UNCOMMENT for debugging
            #print(f'{index} | exp_id: {exp_id} | adm0: {adm0_name} | adm1: {adm1_name} | adm2: {adm2_name}')

            mapping[exp_id] = [str(adm0_code), str(adm1_code), str(adm2_code)]

            if index % 100 == 0:
                print(f'\tProcessed {index} rows')

        with open(f'{mappingFile}_{i}.json', 'w') as f:
            f.write(json.dumps(mapping, separators=(',', ':')))

        print(f'\t\tProcessed {country}\n')



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-z', '--zip', type=str, help='Path to shapefile (zip)', default='arc_consolidated_exposure.zip', dest='zip')
    parser.add_argument('-a2', '--adm2', type=str, help='Path to adm2 file', default='adm2.json', dest='adm2')
    parser.add_argument('-m', '--mapping', type=str, help='mapping JSON file', default='mapping', dest='mappingFile')
    args = parser.parse_args()

    zip2geojson(zip=args.zip, adm2=args.adm2, mappingFile=args.mappingFile)

