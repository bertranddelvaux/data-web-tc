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

from utils import listFilesUrl, fetchUrl


# a few constants
YEAR_HISTORICAL_START = 1980 # latest year with historical data
YEAR_2022 = 2022 # year which is in the old KAC project arc_proj22 but not anymore in the historical data
YEAR_2023_NOW = 2023 # year which is in the latest KAC project
URL_1980_2021 = 'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/historical_data/' # URL to fetch data from 1980 to 2021
URL_2022 = 'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/2022_JTWC/' # URL to fetch data from 2022
URL_2023_NOW = 'https://www.kacportal.com/portal/kacs3/arc/mpres_data/postevent/' # URL to fetch data from 2023 until now
# KAC portal login credentials
USERNAME = os.environ['KAC_USERNAME']
PASSWORD = os.environ['KAC_PASSWORD']


def getListFiles(
        start,
        end,
        res
):
    '''Get list of eligible files'''

    def sort_filter_files_by_year(list_files, start, end):

        # Regular expression to extract the year from the file name
        year_pattern = re.compile(r'_SH(\d{6})_')

        # Filter files that are between the start_year and end_year
        filtered_files = [
            file for file in list_files
            if (match := year_pattern.search(file)) and start <= int(match.group(1)[-4:]) <= end
        ]

        sorted_filtered_files = sorted(filtered_files, key=extract_year_from_url)

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

def generateHeatMap(
        start,
        end,
        alg,
        res,
):

    list_files = getListFiles(start, end, res)

    exit()


if __name__ == '__main__':

    current_year = datetime.datetime.now().year

    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-res', '--resolution', type=str, default='high', dest='res', help="Set the resolution of the data: 'low' or 'high'.")
    parser.add_argument('-start', type=int, default=YEAR_HISTORICAL_START, dest='start', help="Starting year to be processed.")
    parser.add_argument('-end', type=int, default=current_year, dest='end', help="Ending year to be processed.")
    parser.add_argument('-alg', type=str, required=True, dest='alg', help="Algorithm to process the data")
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
            f'Ending year {args.end} must be later than {args.start}  is out of the allowed range {YEAR_HISTORICAL_START}-{current_year}')

    # handling algorithm choice exception
    if args.alg not in ['max_wind_speed', 'number_of_hits', 'median_wind_speed', 'degree_of_severity']:
        raise argparse.ArgumentTypeError('Algorithm must be either "max_wind_speed", "number_of_hits", "median_wind_speed" or "degree_of_severity"')

    generateHeatMap(
        start=args.start,
        end=args.end,
        alg=args.alg,
        res=args.res,
    )