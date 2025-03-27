import os
import re
import ast

import pandas as pd

from urllib.parse import urlparse

import nczip2geojson as nc

from ncgzip2losses import calculateLosses
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

# Online dir for 30as
url_subfolder_list_30as = [
    #TODO: missing 30as data <= 2021, historical
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2022_JTWC/30as/', # 2022
    'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/taos_swio30s_ofcl_windwater_nc/', # 2023, 2024, 2025
    ]

# Local storage
root_root = os.path.abspath(os.getcwd())
os.chdir('mpres_data/postevent/ofcl_30as_nc')
dir_root = os.path.abspath(os.getcwd())
impact_dir = os.path.join(root_root, 'impact_30as')

# Number of files to handle at a time
N = 5

# extension
ext = '.nc'

####################
# files to exclude #
####################

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

#################
# Exclude files #
#################

##########################################
# 1. Exclude files present in impact_dir #
list_files_impact = os.listdir(impact_dir)

# List all files in the directory
files_to_exclude = get_files_pattern(list_files_impact, ext='.csv')

######################################################################################################################
# 2. Exclude files whose atcfid (SHiiyyyy) are present in url_subfolder_list_30as but not in url_subfolder_list_15as #

# Initializing files_list
files_list_30as = []
files_list_15as = []

for url_subfolder in url_subfolder_list_30as:
    files_list_30as += listFilesUrl(url_subfolder, username, password, ext=ext)

for url_subfolder in url_subfolder_list_15as:
    files_list_15as += listFilesUrl(url_subfolder, username, password, ext=ext)

files_pattern = get_files_pattern(files_list_15as, ext='.nc')

# update files_list_30as with files whose pattern is already in files_list_15as
files_list_30as_updated = [filename for filename in files_list_30as if any(pattern in filename for pattern in files_pattern)]

# Filter out URLs that contain any of the files in files_to_exclude
updated_files_list = [file for file in files_list_30as_updated if not any(exclude in file for exclude in set(files_to_exclude))]

# Print the values to capture in the GitHub Actions workflow
print(f"files_to_process={len(files_list_30as)}")
print(f"files_processed={len(files_list_30as)-len(updated_files_list)+N}")

for url_file in updated_files_list[:N]:
    filename = os.path.basename(urlparse(url_file).path)

    downloaded = fetchUrl(url_file, username, password)

    if downloaded:
        nc.nc2geojson(filename)
        # running loss generation
        calculateLosses(
            storm_file=filename,
            exp_file=os.path.join(root_root, 'arc_exposure.gzip'),
            adm_file=os.path.join(root_root, 'adm2_full_precision.json'),
            mapping_file=os.path.join(root_root, 'mapping_new.gzip'),
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
    if isinstance(wind_dict, dict):
        return [wind_dict.get(i, 0) for i in range(6)]
    else:
        return [0 for i in range(6)]

# Loop through all the files in the directory
for file_name in os.listdir(impact_dir):
    if file_name.endswith('.csv') and any(f'adm{i}' in file_name for i in range(3)) and file_name not in aggregated_files_list:
        # Determine the 'adm' level (0, 1, or 2) from the file name
        for i in range(3):
            if f'adm{i}' in file_name:
                file_path = os.path.join(impact_dir, file_name)
                # Read the CSV file into a DataFrame and append to the corresponding list
                df = pd.read_csv(file_path).fillna(0)
                df['loss'] = df['loss'].apply(lambda x: round(x, 2)) # rounding loss column to 2 decimals

                # Apply parsing to handle both string and dictionary cases
                df['wind_cat'] = df['wind_cat'].apply(parse_wind_cat)

                # Apply the unfold function to the 'wind_cat' column and convert the result into separate columns
                df_wind = pd.DataFrame(df['wind_cat'].apply(unfold_wind_cat).tolist(),
                                       columns=[f'wind_cat_{i}' for i in range(6)])

                # Turn 'wind_cat' into string, so that it is hashable for drop_duplicates()
                df['wind_cat'] = df['wind_cat'].apply(lambda x: str(x))

                # Check if the columns wind_cat_i for i in range(6) are already present
                # Subset the DataFrame to only include these columns
                columns = [f'wind_cat_{i}' for i in range(6)]

                # Check if all columns are present in the DataFrame
                missing_columns = [col for col in columns if col not in df.columns]

                if len(missing_columns) != 0:
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
    impact_total_adm.to_csv(os.path.join(impact_dir, aggregated_files_list[i]), index=False)
