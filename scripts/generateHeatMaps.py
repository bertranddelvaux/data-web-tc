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

from utils import listFilesUrl, fetchUrl



###################
# a few constants #
###################

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

#TODO: suggestion for coverage area:
COVERAGE_AREA = {
        'lat': [-51, 3],
        'lon': [20, 150]
}

# resolutions
RESOLUTION = {
    'low': 120,
    'high': 60 #TODO: correct that number!
}

# Wind variable
WIND_VARIABLE = 'swath_peak_wind'

# Tolerance when reindexing
TOL = 1e-5

# Wind speed to consider for Cyclone hit
WIND_SPEED_THRESHOLD = 17.5 # 17.5 m/s = 63 km/h


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

class HeatMap(xr.DataArray):
    __slots__ = ()  # No additional attributes, so use an empty tuple to prevent creation of __dict__

    def __init__(self, *args, **kwargs):
        # Call the parent class constructor, which initializes the xarray.DataArray
        super().__init__(*args, **kwargs)

    def _reindex_like(self, other):
        """Helper function to reindex 'other' to align with self."""
        if not isinstance(other, xr.DataArray):
            raise TypeError(f'{other} not of {xr.DataArray.__name__} type')
        return other.reindex_like(self, fill_value=0., method='nearest', tolerance=TOL).to_numpy()

    def max_wind_speed(self, other):
        other_reindexed = self._reindex_like(other)
        self.data = np.maximum(self.data, other_reindexed)
        return self

    def number_of_hits(self, other, threshold=WIND_SPEED_THRESHOLD):
        other_reindexed = self._reindex_like(other)
        self.data = self.data + (other_reindexed >= threshold).astype(float)
        return self

    def mean_wind_speed_when_hit(self, other, n, threshold=WIND_SPEED_THRESHOLD):
        other_reindexed = self._reindex_like(other)
        other_reindexed[other_reindexed < threshold] = 0  # Set values below threshold to zero
        self.data = (n * self.data + other_reindexed.astype(float)) / (n + 1)
        return self



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
    lats = hazard_da['latitude'].values # hazard_ds.variables['latitude'][:].values
    lons = hazard_da['longitude'].values # hazard_ds.variables['longitude'][:].values
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

    # Define the latitude and longitude ranges from COVERAGE_AREA
    lat_min, lat_max = COVERAGE_AREA['lat']
    lon_min, lon_max = COVERAGE_AREA['lon']

    # Create the grid for the xarray with the specified resolution
    dxdy = RESOLUTION[res] / 3600.
    latitudes = np.arange(lat_min - dxdy / 2., lat_max + dxdy / 2., dxdy)
    longitudes = np.arange(lon_min - dxdy / 2., lon_max + dxdy / 2., dxdy)

    # Initialize an empty xarray with NaN values
    heatmap = HeatMap(
        xr.DataArray(
            np.full((len(latitudes), len(longitudes)), 0.),
            dims=['latitude', 'longitude'],
            coords={'latitude': latitudes, 'longitude': longitudes},
            name='heatmap'
        )
    )

    # Loop through the urls
    for i, url in enumerate(list_urls):

        #TODO:
        # 1. Download
        #   a. Get the resolution, save it, print when different
        # 2. Open the wind part
        # 3. Update the datset
        # 4. Remove the file

        # hazard file
        hazard_nc_file = os.path.basename(urlparse(url).path)

        # Calculate the width based on the length of the list
        width = len(str(len(list_urls)))

        # Print with leading zeros and proper alignment
        print(f'{GREEN}{i + 1:0{width}d}/{len(list_urls)}{RESET}', end='')

        # Download file
        downloaded = fetchUrl(url, USERNAME, PASSWORD, filename=hazard_nc_file)

        if downloaded:
            hazard_da, lats, lons, dx, dy, resolution = getHazardDataArray(hazard_nc_file)

            if resolution != RESOLUTION[res]:
                raise RuntimeError(f'res: {resolution} != resolution {RESOLUTION[res]}')

            #TODO: REMOVE
            print(f'max BEFORE : {np.max(heatmap.to_numpy())}')
            #TODO: REMOVE

            if alg == 'max_wind_speed':
                heatmap = heatmap.max_wind_speed(hazard_da)
            elif alg == 'number_of_hits':
                heatmap = heatmap.number_of_hits(hazard_da)
            elif alg == 'mean_wind_speed_when_hit':
                heatmap = heatmap.mean_wind_speed_when_hit(hazard_da, i)
            else:
                raise NotImplemented(f'algorithm {alg} not implemented')

            #TODO: REMOVE
            print(f'max AFTER : {np.max(heatmap.to_numpy())}')
            #TODO: REMOVE

            #TODO: generate intermediate heatmaps?

        else:
            print(f"Failed to download {hazard_nc_file}")

        # removing hazard file
        os.remove(hazard_nc_file)

    # Now save the heatmap as a GeoTIFF
    output_filename = f'heatmap_{alg}_{start}_{end}.tif'
    transform = from_origin(lon_min - dxdy / 2., lat_max + dxdy / 2., dxdy, dxdy)  # top-left corner and pixel size

    # Define metadata for the GeoTIFF
    metadata = {
        'driver': 'GTiff',
        'count': 1,  # One band of data
        'dtype': 'float64',  # Data type of the array
        'crs': 'EPSG:4326',  # Coordinate reference system (WGS 84)
        'width': heatmap.values.shape[1],
        'height': heatmap.values.shape[0],
        'transform': transform
    }

    with rasterio.open(output_filename, 'w', **metadata) as dst:
        dst.write(heatmap.values, 1)  # Write the data to band 1

    print(f'GeoTIFF saved as {output_filename}')


if __name__ == '__main__':

    year_current = datetime.datetime.now().year

    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-res', '--resolution', type=str, default='high', dest='res', help="Set the resolution of the data: 'low' or 'high'.")
    parser.add_argument('-start', type=int, default=YEAR_HISTORICAL_START, dest='start', help="Starting year to be processed.")
    parser.add_argument('-end', type=int, default=year_current, dest='end', help="Ending year to be processed.")
    parser.add_argument('-alg', type=str, default='max_wind_speed', dest='alg', help="Algorithm to process the data")
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

    # handling algorithm choice exception
    if args.alg not in ['max_wind_speed', 'number_of_hits', 'mean_wind_speed_when_hit', 'degree_of_severity']:
        raise argparse.ArgumentTypeError('Algorithm must be either "max_wind_speed", "number_of_hits", "mean_wind_speed_when_hit" or "degree_of_severity"')

    generateHeatMap(
        start=args.start,
        end=args.end,
        alg=args.alg,
        res=args.res,
    )
