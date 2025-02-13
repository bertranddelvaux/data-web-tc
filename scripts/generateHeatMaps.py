#TODO:
# 1. Access KAC portal
#   a. https://www.kacportal.com/portal/kacs3/arc/arc_proj22/historical_data/
#   b. flag (argparse) to choose between high res (15as?) and low res (30as?)
# 2. Argparse
#   a. resolution low, high
#   b. years span
#      i. if None, the whole history since 1980 season
#      ii. if only one year mentioned, e.g. '1986', process only that year
#      iii. if only one year mentioned with a plus, e.g. '1986+', process the whole history since that year
#      iv. if a year span mentioned, e.g. '1986-2004', process the span
#   c. type of algorithm
#      i. max_wind_speed
#      ii. number_of_hits
#      iii. median_wind_speed
#      iv. degree_of_severity
# 3. Process
#   a. collect a list of files to go through, given the argparse
#   b. open the exposure dataset (depending on low or high resolution)
#   c. create an empty dataset based on the exposure dataset
#   d. loop through the list of files
#      i. read the hazard
#      ii. identify the corresponding exposure id
#      iii. update the dataset according to the chosen algorithm
#   e. write out the dataset to a geojson
# NOTE:
#   A. Don't forget to include the most recent years!!! (Historical data stop at 2021)


import os
import re
import argparse
import datetime

import numpy as np
import xarray as xr

import rasterio
from rasterio.transform import from_origin

from urllib.parse import urlparse
from enum import Enum

from utils import listFilesUrl, fetchUrl



###################
# a few constants #
###################

# eligible algorithms
class EligibleAlgorithms(Enum):
    MAX_WIND_SPEED = 'max_wind_speed'
    NUMBER_OF_HITS = 'number_of_hits'
    MEAN_WIND_SPEED_WHEN_HIT = 'mean_wind_speed_when_hit'
    MEDIAN_WIND_SPEED_WHEN_HIT = 'median_wind_speed_when_hit'
    DEGREE_OF_SEVERITY_MEDIAN = 'degree_of_severity_median'
    DEGREE_OF_SEVERITY_MEAN = 'degree_of_severity_mean'

YEAR_HISTORICAL_START = 1980 # latest year with historical data
YEAR_2022 = 2022 # year which is in the old KAC project arc_proj22 but not anymore in the historical data
YEAR_2023_NOW = 2023 # year which is in the latest KAC project
URL_1980_2021 = 'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/historical_data/' # URL to fetch data from 1980 to 2021
URL_2022 = 'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2022_JTWC/' # URL to fetch data from 2022
URL_2023_NOW = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/' # URL to fetch data from 2023 until now

# KAC portal login credentials
USERNAME = os.environ['KAC_USERNAME']
PASSWORD = os.environ['KAC_PASSWORD']

# Color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
PURPLE = '\033[95m'
RESET = '\033[0m'

# resolutions
RESOLUTION = {
    'low': 120,
    'high': 60 #TODO: correct that number!
}

# Wind variable
WIND_VARIABLE = 'swath_peak_wind'

# m/s to km/h
MS2KMH = 3.6

# Constants to reach a 100 on the severity scale (10 hits at 100 km/h)
N = 10 # number of hits per year
S = 100 / MS2KMH # 100 km/h in m/s

# Threshold to have damages
T = 63 / MS2KMH # 63 km/h in m/s


#######################
# Decorator functions #
#######################

def wrap_get_list_urls(func):
    def wrapper(start, end, res):
        # Print the message before calling the function
        print(f'{BLUE}Fetching files between {start} and {end}, {res} resolution ... {RESET}', end='')

        # Call the original function
        list_urls = func(start, end, res)

        # Print the message after the function completes
        print(f'{GREEN}found {len(list_urls)} files{RESET}')
        return list_urls
    return wrapper

def wrap_get_hazard_dataarray(func):
    def wrapper(hazard_nc_file):
        # Call the original function
        hazard_da, lats, lons, dx, dy, res = func(hazard_nc_file)

        # Print the message after the function completes
        print(f'\t\t\tres: {PURPLE}{res} arcseconds{RESET} (dx {dx:.6f} dy {dy:.6f})')
        print(f'\t\t\tlat: {PURPLE}{lats[0]} {lats[-1]}{RESET}')
        print(f'\t\t\tlon: {PURPLE}{lons[0]} {lons[-1]}{RESET}')
        return hazard_da, lats, lons, dx, dy, res
    return wrapper


#################
# Class HeatMap #
#################

class HeatMap():

    def __init__(self):
        self.list_data_arrays = []

    def add_data_array(self, da):
        self.list_data_arrays.append(da)

    def process_heatmap(self, T=T):
        self.list_data_arrays_aligned = xr.align(*self.list_data_arrays, join='outer', fill_value=0.0)
        self.list_data_arrays_aligned_boolean = [da >= T for da in self.list_data_arrays_aligned]
        self.number_of_hits = np.add.reduce(self.list_data_arrays_aligned_boolean)  # number of hits per pixel
        self.maximum_speed = np.maximum.reduce(self.list_data_arrays_aligned)  # maximum speed per pixel
        self.mean_speed = np.mean(self.list_data_arrays_aligned, axis=0)
        self.median_speed = np.median(self.list_data_arrays_aligned, axis=0)
        self.hits_median_speed = self.number_of_hits * self.median_speed
        self.severity_median = vectorized_severity(self.number_of_hits * self.median_speed)
        self.severity_mean = vectorized_severity(self.number_of_hits * self.mean_speed)
        self.latitudes = self.list_data_arrays_aligned[0].latitude.data
        self.longitudes = self.list_data_arrays_aligned[0].longitude.data

#####################
# Severity function #
#####################

def severity(hit_speed, N=N, S=S, T=T):
    # f(x) = 1 / a * ln(b * x + c)
    # a = ln (b * T)
    # b = [NS / T^100] ^ 1/99
    # c = 0

    # function parameters
    c = 0
    b = np.power((N * S) / (T**100), 1/99)
    a = np.log(b * T)

    # dependent variable
    x = hit_speed # formerly two variables: x = hits * speed

    # severity function
    f = 1 / a * np.log(b * x + c)

    return max(f, 0.0) #np.round(max(f, 0.0), decimals=0)

vectorized_severity = np.vectorize(severity)

######################
# Get URLs functions #
######################

@wrap_get_list_urls
def getListURLs(
        start,
        end,
        res
):
    '''Get list of eligible files'''

    def sort_filter_files_by_year(list_files, start, end):

        # Regular expression to extract the year from the file name
        year_pattern = re.compile(r'_SH(\d{6})_')

        sorted_filtered_files = sorted([file for file in list_files if start <= extract_year_from_url(file) <= end], key=extract_year_from_url)

        return sorted_filtered_files

    def extract_year_from_url(url):
        # Define a function to extract the year from the URL
        match = re.search(r'_SH(\d{6})_', url)
        if match:
            year = match.group(1)[-4:]  # Extract the last four digits as the year
            return int(year)
        else:
            return None

    # data from 1980 to 2021
    url_1980_2021 = f'{URL_1980_2021}jtwc_{res}_resolution_hazard'
    list_files_1980_2021 = listFilesUrl(url_1980_2021, USERNAME, PASSWORD, ext='.nc')

    # data from 2022
    url_2022 = f'{URL_2022}{"30as" if res == "low" else "15as"}'
    list_files_2022 = listFilesUrl(url_2022, USERNAME, PASSWORD, ext='.nc')

    # data from 2023 to now
    url_2023_now = f'{URL_2023_NOW}taos_swio{"30" if res == "low" else "15"}s_ofcl_windwater_nc'
    list_files_2023_now = listFilesUrl(url_2023_now, USERNAME, PASSWORD, ext='.nc')

    # Combine all lists into one
    list_files = list_files_1980_2021 + list_files_2022 + list_files_2023_now

    # Sort the list of files by the year extracted from the URL
    list_files_sorted = sort_filter_files_by_year(list_files, start, end)

    return list_files_sorted

############################
# Hazard Dataset functions #
############################

@wrap_get_hazard_dataarray
def getHazardDataArray(hazard_nc_file):
    hazard_ds = xr.open_dataset(hazard_nc_file, engine='netcdf4', decode_times=False)

    # Select only the variables you need
    hazard_da = hazard_ds[WIND_VARIABLE]

    # Resolution
    lats = hazard_da['latitude'].values
    lons = hazard_da['longitude'].values
    dy = (lats[-1] - lats[0]) / (len(lats) - 1)
    dx = (lons[-1] - lons[0]) / (len(lons) - 1)

    return hazard_da, lats, lons, dx, dy, round(3600.0 * dx)


###############################
# Generate Heat Map functions #
###############################

def generateHeatMap(
        start,
        end,
        alg,
        res,
):
    """
    Generates a heatmap from hazard data, saving the result as a GeoTIFF.

    Arguments:
    start: start date
    end: end date
    alg: algorithm to process the data
    res: resolution in degrees
    """

    # Get the list of eligible urls
    list_urls = getListURLs(start, end, res)

    # Initializing heatmap
    heatmap = HeatMap()

    # Loop through the urls
    for i, url in enumerate(list_urls):

        # hazard file
        hazard_nc_file = os.path.basename(urlparse(url).path)

        # Calculate the width based on the length of the list
        width = len(str(len(list_urls)))

        # Print with leading zeros and proper alignment
        print(f'{GREEN}{i + 1:0{width}d}/{len(list_urls)}{RESET}', end='')

        # Download file
        downloaded = fetchUrl(url, USERNAME, PASSWORD, filename=hazard_nc_file)

        if downloaded:
            hazard_da, lats, lons, dxdy, dy, resolution = getHazardDataArray(hazard_nc_file)

            if resolution != RESOLUTION[res]:
                raise RuntimeError(f'res: {resolution} != resolution {RESOLUTION[res]}')

            heatmap.add_data_array(hazard_da)

        else:
            print(f"Failed to download {hazard_nc_file}")

        # removing hazard file
        os.remove(hazard_nc_file)

    # process heatmap
    heatmap.process_heatmap(T=T)

    # Assuming latitudes and longitudes are lists or arrays
    longitudes = heatmap.longitudes
    latitudes = heatmap.latitudes
    lon_min, lon_max = min(longitudes), max(longitudes)
    lat_min, lat_max = min(latitudes), max(latitudes)

    # Calculate the pixel size based on the data resolution (in degrees or your desired unit)
    # For simplicity, let's assume your heatmap is square (same resolution in both lat and lon)
    dxdy = (lon_max - lon_min) / len(longitudes)  # or use any resolution for both axes

    # Now save the heatmap as a GeoTIFF
    transform = from_origin(lon_min - dxdy / 2., lat_max + dxdy / 2., dxdy, dxdy)  # top-left corner and pixel size

    # Define metadata for the GeoTIFF
    metadata = {
        'driver': 'GTiff',
        'count': 1,  # One band of data
        'dtype': 'float64',  # Data type of the array
        'crs': 'EPSG:4326',  # Coordinate reference system (WGS 84) #'crs': '+proj=latlong'
        'width': len(longitudes),
        'height': len(latitudes),
        'transform': transform
    }

    for alg in EligibleAlgorithms:
        output_filename = f'heatmap_{alg}_{start}_{end}.tif'

        if alg == EligibleAlgorithms.MAX_WIND_SPEED:
            data = heatmap.maximum_speed
        elif alg == EligibleAlgorithms.NUMBER_OF_HITS:
            data = heatmap.number_of_hits
        elif alg == EligibleAlgorithms.MEAN_WIND_SPEED_WHEN_HIT:
            data = heatmap.mean_speed
        elif alg == EligibleAlgorithms.MEDIAN_WIND_SPEED_WHEN_HIT:
            data = heatmap.median_speed
        elif alg == EligibleAlgorithms.DEGREE_OF_SEVERITY_MEDIAN:
            data = heatmap.severity_median
        elif alg == EligibleAlgorithms.DEGREE_OF_SEVERITY_MEAN:
            data = heatmap.severity_mean

        with rasterio.open(output_filename, 'w', **metadata) as dst:
            dst.write(data, 1)  # Write the data to band 1

        print(f'GeoTIFF saved as {output_filename}')


if __name__ == '__main__':

    year_current = datetime.datetime.now().year

    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-res', '--resolution', type=str, default='high', dest='res', help="Set the resolution of the data: 'low' or 'high'.")
    parser.add_argument('-start', type=int, default=YEAR_HISTORICAL_START, dest='start', help="Starting year to be processed.")
    parser.add_argument('-end', type=int, default=year_current, dest='end', help="Ending year to be processed.")
    parser.add_argument('-alg', type=str, default=None, dest='alg', help="Algorithm to process the data")
    args = parser.parse_args()

    def year_out_of_range(year):
        year_current = datetime.datetime.now().year
        if year < YEAR_HISTORICAL_START or year > year_current:
            raise argparse.ArgumentTypeError(f'Year {year} is out of the allowed range {YEAR_HISTORICAL_START}-{year_current}')

    # handling res arg exception
    if args.res not in ['low', 'high']:
        raise argparse.ArgumentTypeError('Resolution must be either "low" or "high"')

    # handling start and end args exceptions
    year_out_of_range(args.start)
    year_out_of_range(args.end)
    if args.end < args.start:
        raise argparse.ArgumentTypeError(
            f'Ending year {args.end} must be later than {args.start}  is out of the allowed range {YEAR_HISTORICAL_START}-{year_current}')

    # Handling algorithm choice exception using the Enum
    try:
        if args.alg is not None and not any(args.alg == alg.value for alg in EligibleAlgorithms):
            raise argparse.ArgumentTypeError(
                f'{RED}Algorithm must be one of: ' + ', '.join([alg.value for alg in EligibleAlgorithms]) + RESET
            )
    except argparse.ArgumentTypeError as e:
        print(e)

    # Generate HeatMap
    generateHeatMap(
        start=args.start,
        end=args.end,
        alg=args.alg,
        res=args.res,
    )
