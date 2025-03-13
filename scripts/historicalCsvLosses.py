#TODO:
# !!! USE SH011980_shp.geojson instead of SH021980_BEST_SLOSH_losses_adm0.json, it will give you:
# - the right numbers
# - ecursive approach
# - wind categories
# !!! DON'T FORGET TO REIMPLEMENT THE WIND CATEGORIES!!!


import os
import json
import re
import glob
import ast

import pandas as pd
import numpy as np

from utils import listFilesUrl, fetchUrl



#############
# Constants #
#############

# Connexion credentials
username = os.environ['KAC_USERNAME']
password = os.environ['KAC_PASSWORD']

# Online dir for 15as
url_subfolder_list_15as = [
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/historical_data/jtwc_high_resolution_hazard/', # <= 2021, historical
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2022_JTWC/15as/', # 2022, 6 storms
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2023_JTWC/15as/', # 2023, 2 storms
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2024_provisional/15as/', # 2024, 7 storms
    'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/ofcl_15as_nc/', # 2025, 5 storms (2025-02-03)
    ]

# Online dir for JTWC historical data
dir_JTWC_historical = 'jtwc_history'

# Impact dir
impact_dir = 'impact_30as'

# Reference dir
reference_dir = 'impact_15as'

# Reference files
reference_files_list = [
    f'{reference_dir}/impact_total_adm{i}_15as.csv' for i in range(3)
]

# Local storage
root_root = os.path.abspath(os.getcwd())
impact_dir = os.path.join(root_root, 'impact_30as')

#####################
# Normalize strings #
#####################

def standardize_country_name(country):
    replacements = {
        "Réunion": "Reunion",
        "United Republic of Tanzania": "Tanzania"
    }

    # Loop through the dictionary and perform replacements
    for old_name, new_name in replacements.items():
        country = country.replace(old_name, new_name)

    return country

######################
# files with pattern #
######################

def get_files_pattern(list_files, ext, pattern = r'SH\d{6}'):
    # Regular expression pattern to match 'SH' followed by 6 digits

    # Initialize an empty list to store the matches
    files_pattern = []

    # Iterate through the files
    for filename in list_files:
        # Process only CSV files
        if filename.endswith(ext):
            match = re.search(pattern, filename)
            if match:
                files_pattern.append(match.group(0))  # Append the matched string to the list

    return files_pattern


#####################
# Process json data #
#####################

def process_json_data(file_path):
    # Open and read the JSON file
    with open(file_path, 'r') as fp:
        data = json.load(fp)['records']

    # DataFrame for adm0 (dropping 'adm1')
    df_adm0 = pd.DataFrame(data).drop(columns=['adm1'])

    # Initialize empty DataFrames for adm1 and adm2
    df_adm1 = pd.DataFrame()
    df_adm2 = pd.DataFrame()

    # Loop through each record in data
    for adm0 in data:
        # Process DataFrame for adm1 (dropping 'adm2')
        df_adm1_temp = pd.DataFrame(adm0['adm1']).drop(columns=['adm2'])
        df_adm1_temp.insert(0, 'adm0_name', adm0['adm0_name'])  # Insert 'adm0_name' at the beginning
        df_adm1_temp.insert(1, 'adm0_code', adm0['adm0_code'])  # Insert 'adm0_code' after 'adm0_name'
        df_adm1 = pd.concat([df_adm1, df_adm1_temp], ignore_index=True)

        # Process DataFrame for adm2
        for adm1 in adm0['adm1']:
            df_adm2_temp = pd.DataFrame(adm1['adm2'])
            df_adm2_temp.insert(0, 'adm0_name', adm0['adm0_name'])  # Insert 'adm0_name'
            df_adm2_temp.insert(1, 'adm0_code', adm0['adm0_code'])  # Insert 'adm0_code'
            df_adm2_temp.insert(2, 'adm1_name', adm1['adm1_name'])  # Insert 'adm1_name'
            df_adm2_temp.insert(3, 'adm1_code', adm1['adm1_code'])  # Insert 'adm1_code'
            df_adm2 = pd.concat([df_adm2, df_adm2_temp], ignore_index=True)

    return [df_adm0, df_adm1, df_adm2]

####################
# Historical files #
####################

# Use glob to find all the matching files
file_patterns_historical = [
    os.path.join(dir_JTWC_historical, '**', '*losses_adm.json'),
    # os.path.join(dir_JTWC_historical, '**', '*losses_adm0.json'),
    # os.path.join(dir_JTWC_historical, '**', '*losses_adm1.json'),
    # os.path.join(dir_JTWC_historical, '**', '*losses_adm2.json')
]

# Initialize an empty list to store the files
historical_files = []

# Iterate through the patterns and get matching files
for pattern in file_patterns_historical:
    historical_files.extend(glob.glob(pattern, recursive=True))


#################################################################################
# Exclude files whose atcfid (SHiiyyyy) are not present url_subfolder_list_15as #
#################################################################################

# Initializing files_list
files_list_15as = []

for url_subfolder in url_subfolder_list_15as:
    files_list_15as += listFilesUrl(url_subfolder, username, password, ext='.nc')

files_pattern = get_files_pattern(files_list_15as, ext='.nc')

# update files_list_30as with files whose pattern is already in files_list_15as
historical_files_updated = [filename for filename in historical_files if any(pattern in filename for pattern in files_pattern)]


#########################
# Save Total Impact CSV #
#########################

# aggregated files
aggregated_files_list = [f'impact_total_adm{i}_30as.csv' for i in range(3)]

# List to store the dataframes for each 'adm'
dfs = {0: [], 1: [], 2: []}

# Function to safely evaluate the string or handle the dictionary
def parse_wind_cat(value):
    if isinstance(value, str):
        # If the value is a string, safely evaluate it as a dictionary
        value = ast.literal_eval(value)
    return value

# Function to unfold the wind_cat column into separate columns
def unfold_wind_cat(wind_dict):
    # Create a list with wind categories from 0 to 5, defaulting to 0 if the category is missing
    return [wind_dict.get(i, 0) for i in range(6)]

# Loop through all the files in the directory
for file_path in historical_files_updated:
    if file_path.endswith('.json'): # and any(f'adm{i}' in file_path for i in range(3)) and file_path not in aggregated_files_list:

        # process json data
        try:
            df_adm_list = process_json_data(file_path)
        except:
            print(file_path)
            continue

        # Determine the 'adm' level (0, 1, or 2) from the file name
        for i in range(3):

            ref_df = pd.read_csv(reference_files_list[i])

            # Create an empty DataFrame to store the results
            df = pd.DataFrame()

            # atcf_id
            atcf_id = get_files_pattern([file_path], '.json')[0]

            # check if atcf_id in ref_df
            if atcf_id not in ref_df['atcf_id'].unique():
                continue

            # Iterate through all rows in df_json
            for _, row in df_adm_list[i].iterrows():
                df_temp = ref_df[ref_df['atcf_id'] == atcf_id].iloc[0:1] # pick up the first entry
                for j in range(i+1):

                    row_adm_name = standardize_country_name(row[f'adm{j}_name'])

                    df_equiv = ref_df[ref_df[f'adm{j}_name'] == row_adm_name]
                    if df_equiv.empty:
                        if row_adm_name == 'Administrative unit not available':
                            row_adm_name = ''
                            row_adm_code = f'No Adm{j}'
                    else:
                        row_adm_code = df_equiv.iloc[0][f'adm{j}_code'] # pick up the country code

                    df_temp[f'adm{j}_name'] = row_adm_name
                    df_temp[f'adm{j}_code'] = row_adm_code

                # updating loss and population
                df_temp['loss'] = np.round(row['loss'], decimals=2) # rounding loss column to 2 decimals
                df_temp['population'] = int(row['population'])

                try:
                    df_temp['wind_cat'] = [{int(key): value for key, value in row['wind_cat'].items()}]
                except:
                    print(f'Issue with file {file_path}')
                df_temp.drop(columns=[f'wind_cat_{c}' for c in range(6)], inplace=True)

                # Apply parsing to handle both string and dictionary cases
                df_temp['wind_cat'] = df_temp['wind_cat'].apply(parse_wind_cat)

                df_wind = pd.DataFrame(df_temp['wind_cat'].apply(unfold_wind_cat).tolist(),
                                       columns=[f'wind_cat_{i}' for i in range(6)])

                # Reset index to avoid misalignment
                df_temp.reset_index(drop=True, inplace=True)
                df_wind.reset_index(drop=True, inplace=True)

                # Concatenate the new columns to df_temp
                df_temp = pd.concat([df_temp, df_wind], axis=1)

                # Turn 'wind_cat' into string, so that it is hashable for drop_duplicates()
                df_temp['wind_cat'] = df_temp['wind_cat'].apply(lambda x: str(x) if isinstance(x, dict) else x)

                # Check if there are any NaN values in the 'tc_season' column
                has_nan = df_temp['tc_season'].isna().any()

                df = pd.concat([df, df_temp])

            # Replace the value in the column tech by SLOSH if SLOSH in filepath
            if 'SLOSH' in file_path:
                df['tech'] = 'SLOSH'

            # Save the CSV
            csv_path = f'{impact_dir}/impact_{atcf_id[-4:]}_{atcf_id}_losses_adm{i}.csv'
            df.to_csv(csv_path, index=False)

            # Concatenate the original DataFrame with the unfolded columns
            dfs[i].append(df)
            #break

# Loop through each 'adm' level and create a merged file for each
for i in range(3):

    # Sort columns for each level as specified
    if i == 0:
        columns_order = ['tc_season', 'atcf_id', 'adm0_code']
    elif i == 1:
        columns_order = ['tc_season', 'atcf_id', 'adm0_code', 'adm1_code']
    elif i == 2:
        columns_order = ['tc_season', 'atcf_id', 'adm0_code', 'adm1_code', 'adm2_code']

    # Concatenate all DataFrames for this 'adm' level
    impact_total_adm = pd.concat(dfs[i], ignore_index=True).sort_values(by=columns_order).drop_duplicates()

    # Save the merged dataframe to a new CSV file
    impact_total_adm.to_csv(os.path.join(impact_dir, aggregated_files_list[i]), index=False)
