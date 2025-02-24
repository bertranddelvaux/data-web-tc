import os
import re

import pandas as pd

from urllib.parse import urlparse

import nczip2geojson as nc

from ncgzip2losses_15as import calculateLosses_15as
from utils import listFilesUrl, fetchUrl

#############
# Constants #
#############

# Connexion credentials
url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/'
username = os.environ['KAC_USERNAME']
password = os.environ['KAC_PASSWORD']

# Online dir
url_subfolder_list = [
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/historical_data/jtwc_high_resolution_hazard/', # < 2021, historical
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2022_JTWC/15as/', # 2022
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2023_JTWC/15as/', # 2023
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2024_provisional/15as/', # 2024
    'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/ofcl_15as_nc/', # 2025
    ]

# Local storage
root_root = os.path.abspath(os.getcwd())
os.chdir('mpres_data/postevent/ofcl_15as_nc')
dir_root = os.path.abspath(os.getcwd())
impact_dir = os.path.join(root_root, 'impact_15as')

# Number of files to handle at a time
N = 1

# extension
ext = '.nc'

####################
# files to exclude #
####################

# List all files in the directory
files = os.listdir(impact_dir)

# Regular expression pattern to match 'SH' followed by 6 digits
pattern = r'SH\d{6}'

# Initialize an empty list to store the matches
files_to_exclude = []

# Iterate through the files
for filename in files:
    # Process only CSV files
    if filename.endswith('.csv'):
        match = re.search(pattern, filename)
        if match:
            files_to_exclude.append(match.group(0))  # Append the matched string to the list


# initializing files_list
files_list = []

for url_subfolder in url_subfolder_list:

    os.chdir(dir_root)

    files_list += listFilesUrl(url_subfolder, username, password, ext=ext)

# Filter out URLs that contain any of the files in files_to_exclude
updated_files_list = [file for file in files_list if not any(exclude in file for exclude in set(files_to_exclude))]

# Print the values to capture in the GitHub Actions workflow
print(f"files_to_process={len(files_list)}")
print(f"files_processed={len(files_list)-len(updated_files_list)}")

for url_file in updated_files_list[:N]:
    filename = os.path.basename(urlparse(url_file).path)

    downloaded = fetchUrl(url_file, username, password)

    if downloaded:
        nc.nc2geojson(filename)
        # running loss generation
        calculateLosses_15as(
            storm_file=filename,
            exp_file=os.path.join(root_root, 'arc_consolidated_expo_15as_gdp.gzip'),
            adm_file=os.path.join(root_root, 'adm2_full_precision.json'),
            mapping_file=os.path.join(root_root, 'mapping_15as.gzip'),
            split=False,
            geojson=False,
            gadm_file=os.path.join(root_root, 'gadm_adm2.json'),
            impact_dir=impact_dir
        )

    # removing nc file
    os.remove(filename)

#########################
# Save Total Impact CSV #
#########################

# List to store the dataframes for each 'adm'
dfs = {0: [], 1: [], 2: []}

# Function to unfold the wind_cat column into separate columns
def unfold_wind_cat(wind_dict):
    # Create a list with wind categories from 0 to 5, defaulting to 0 if the category is missing
    return [wind_dict.get(i, 0) for i in range(6)]

# Loop through all the files in the directory
for file_name in os.listdir(impact_dir):
    if file_name.endswith('.csv') and any(f'adm{i}' in file_name for i in range(3)):
        # Determine the 'adm' level (0, 1, or 2) from the file name
        for i in range(3):
            if f'adm{i}' in file_name:
                file_path = os.path.join(impact_dir, file_name)
                # Read the CSV file into a DataFrame and append to the corresponding list
                df = pd.read_csv(file_path)
                df['loss'] = df['loss'].apply(lambda x: round(x, 2)) # rounding loss column to 2 decimals
                # Apply the function to the 'wind_cat' column and convert the result into separate columns
                df_wind = pd.DataFrame(df['wind_cat'].apply(unfold_wind_cat).tolist(),
                                       columns=[f'wind_cat_{i}' for i in range(6)])
                # Concatenate the original DataFrame with the unfolded columns
                df = pd.concat([df, df_wind], axis=1)
                dfs[i].append(df)
                break

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
    impact_total_csv = f'impact_total_adm{i}_15as.csv'
    impact_total_adm.to_csv(os.path.join(impact_dir, impact_total_csv), index=False)
