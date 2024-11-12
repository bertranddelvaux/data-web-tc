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
import argparse
import datetime

from utils import listFilesUrl, fetchUrl


# a few constants
YEAR_HISTORICAL_START = 1980 # latest year with historical data
URL_HISTORICAL_DATA = 'https://www.kacportal.com/portal/kacs3/arc/arc_proj22/historical_data/' # URL to fetch data from
# KAC portal login credentials
USERNAME = os.environ['KAC_USERNAME']
PASSWORD = os.environ['KAC_PASSWORD']


def getListFiles(
        start,
        end,
        res
):
    '''Get list of eligible files'''

    def filter_files_by_year(list_files, start, end):
        filtered_files = []

        for file in list_files:
            # Split the string at '_OFCL' and take the part before it
            base_name = file.split('_OFCL')[0]

            # Extract the year, which is the last 4 digits before '_OFCL'
            year_str = base_name[-4:]

            # Check if the extracted year is within the range
            if start <= int(year_str) <= end:
                filtered_files.append(file)

        return filtered_files

    url = f'{URL_HISTORICAL_DATA}jtwc_{res}_resolution_hazard'

    list_files_historical = filter_files_by_year(
        listFilesUrl(url, USERNAME, PASSWORD, ext='.nc'),
        start=start,
        end=end
    )

    #TODO: implement list_files_recent

    return None

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