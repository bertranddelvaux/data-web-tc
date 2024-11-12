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


# a few constants
HISTORICAL_START_YEAR = 1980


def generateHeatMap(
        start,
        end,
        alg,
        res = 'high',
):

    exit()


if __name__ == '__main__':

    current_year = datetime.datetime.now().year

    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-res', '--resolution', type=str, default='high', dest='res', help="Set the resolution of the data: 'low' or 'high'.")
    parser.add_argument('-start', type=int, default=HISTORICAL_START_YEAR, dest='start', help="Starting year to be processed.")
    parser.add_argument('-end', type=int, default=current_year, dest='end', help="Ending year to be processed.")
    parser.add_argument('-alg', type=str, required=True, dest='alg', help="Algorithm to process the data")
    args = parser.parse_args()

    def year_out_of_range(year):
        current_year = datetime.datetime.now().year
        if year < HISTORICAL_START_YEAR or year > current_year:
            raise argparse.ArgumentTypeError(f'Year {year} is out of the allowed range {HISTORICAL_START_YEAR}-{current_year}')

    # handling res arg exception
    if args.res not in ['low', 'high']:
        raise argparse.ArgumentTypeError('Resolution must be either "low" or "high"')

    # handling start and end args exceptions
    year_out_of_range(args.start)
    year_out_of_range(args.end)
    if args.end < args.start:
        raise argparse.ArgumentTypeError(
            f'Ending year {args.end} must be later than {args.start}  is out of the allowed range {HISTORICAL_START_YEAR}-{current_year}')

    # handling algorithm choice exception
    if args.alg not in ['max_wind_speed', 'number_of_hits', 'median_wind_speed', 'degree_of_severity']:
        raise argparse.ArgumentTypeError('Algorithm must be either "max_wind_speed", "number_of_hits", "median_wind_speed" or "degree_of_severity"')

    generateHeatMap(
        start=args.start,
        end=args.end,
        alg=args.alg,
        res=args.res,
    )