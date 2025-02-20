import os
import re

import pandas as pd

from urllib.parse import urlparse

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

for url_file in updated_files_list[:N]:
    filename = os.path.basename(urlparse(url_file).path)

    downloaded = fetchUrl(url_file, username, password)

    if downloaded:

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

# List to store the dataframes
dfs = []

# total impact csv
impact_total_csv = 'impact_total_15as.csv'

# Loop through all the files in the directory
for file_name in os.listdir(impact_dir):
    if file_name.endswith('.csv') and impact_total_csv not in file_name:
        file_path = os.path.join(impact_dir, file_name)
        # Read the CSV file into a DataFrame and append to the list
        df = pd.read_csv(file_path)
        dfs.append(df)

# Concatenate all DataFrames into one
impact_total = pd.concat(dfs, ignore_index=True)

# Save the merged dataframe to a new CSV file
impact_total.to_csv(impact_total_csv, index=False)
