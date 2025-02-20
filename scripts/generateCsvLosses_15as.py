import os

from urllib.parse import urlparse

from scripts.ncgzip2losses_15as import calculateLosses_15as
from scripts.utils import listFilesUrl, fetchUrl

#############
# Constants #
#############

# Connexion credentials
url = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/'
username = os.environ['KAC_USERNAME']
password = os.environ['KAC_PASSWORD']

# Online dir
url_subfolder_list = [
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2022_JTWC/15as/', # 2022
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2023_JTWC/15as/', # 2023
    'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2024_provisional/15as/', # 2024
    'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/ofcl_15as_nc/', # 2025
    ]

# Local storage
root_root = os.path.abspath(os.getcwd())
os.chdir('mpres_data/postevent/ofcl_15as_nc')
dir_root = os.path.abspath(os.getcwd())

# extension
ext = '.nc'

# files to exclude
files_to_exclude = [
]

for url_subfolder in url_subfolder_list:

    os.chdir(dir_root)

    files_list = listFilesUrl(url_subfolder, username, password, ext=ext)

    # Filter out URLs that contain any of the files in files_to_exclude
    updated_files_list = [file for file in files_list if not any(exclude in file for exclude in files_to_exclude)]

    for url_file in updated_files_list:
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
                gadm_file=os.path.join(root_root, 'gadm_adm2.json')
            )

        # removing nc file
        os.remove(filename)