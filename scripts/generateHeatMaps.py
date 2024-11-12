#TODO:
# 1. Access KAC portal
#   a. https://www.kacportal.com/portal/kacs3/arc/arc_proj22/historical_data/
#   b. flag (argparse) to choose between high res (15as?) and low res (30as?)
# 2. Argparse
#   a. resolution low, high
#   b. years span
#      i. if None, the whole history since 1980 season
#      ii. if only one year mentioned, the whole history since that year
#   c. type of algorithm
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