# import argparse
# import glob
# import json
#
# import pandas as pd
#
# def getHistory(csv_impact, json_adm):
#
#     df = pd.read_csv(csv_impact)
#
#     # Creation of the dictionary:
#     dict_adm = {
#         'counter_total': len(df['atcf_id'].unique()),
#         'records': []
#     }
#     for adm0_i, adm0_code in enumerate(df['adm0_code'].unique()):
#         df_adm0 = df[df['adm0_code'] == adm0_code]
#         assert len(df_adm0['adm0_name'].unique()) == 1
#         dict_adm['records'].append(
#             {
#                 'adm0_code': adm0_code,
#                 'adm0_name': df_adm0['adm0_name'].fillna('').unique()[0], #df_adm0['adm0_name'].unique()[0],
#                 'counter_adm0': {},
#                 'counter_year': {},
#                 'loss': {},
#                 'storms': [],
#                 'adm1': []
#             }
#         )
#         for adm1_i, adm1_code in enumerate(df_adm0['adm1_code'].unique()):
#             df_adm1 = df[df['adm1_code'] == adm1_code]
#             assert len(df_adm1['adm1_name'].unique()) == 1
#             dict_adm['records'][adm0_i]['adm1'].append(
#                 {
#                     'adm1_code': adm1_code,
#                     'adm1_name': df_adm1['adm1_name'].fillna('').unique()[0], #df_adm1['adm1_name'].unique()[0],
#                     'counter_adm1': {},
#                     'counter_year': {},
#                     'loss': {},
#                     'storms': [],
#                     'adm2': []
#                 }
#             )
#             for adm2_i, adm2_code in enumerate(df_adm1['adm2_code'].unique()):
#                 df_adm2 = df[df['adm2_code'] == adm2_code]
#                 assert len(df_adm2['adm2_name'].unique()) == 1
#                 dict_adm['records'][adm0_i]['adm1'][adm1_i]['adm2'].append(
#                     {
#                         'adm2_code': adm2_code,
#                         'adm2_name': df_adm2['adm2_name'].fillna('').unique()[0], #df_adm2['adm2_name'].unique()[0],
#                         'counter_adm2': {},
#                         'counter_year': {},
#                         'loss': {},
#                         'storms': [],
#                     }
#                 )
#
#     # Constituting shape files' list
#     shp_files_list_jtwc_history = glob.glob('jtwc_history/**/*_shp.geojson', recursive=True)
#     shp_files_list_mpres_data = glob.glob('mpres_data/postevent/taos_swio30s_ofcl_windwater_shp/**/*.geojson', recursive=True)
#     shp_files_list = shp_files_list_jtwc_history + shp_files_list_mpres_data
#
#     for year in df['tc_season'].unique():
#
#         print(f'\nProcessing year {year}')
#
#         df_year = df[df['tc_season'] == year]
#
#         for adm0_i, adm0 in enumerate(dict_adm['records']):
#             df_adm0 = df_year[df_year['adm0_code'] == adm0['adm0_code']]
#
#             print(f'\tAdm0: {adm0["adm0_code"]}')
#
#             if not(df_adm0.empty):
#                 dict_adm['records'][adm0_i]['counter_adm0'][str(year)] = len(df_adm0['atcf_id'].unique())
#                 dict_adm['records'][adm0_i]['counter_year'][str(year)] = len(df_year['atcf_id'].unique())
#                 dict_adm['records'][adm0_i]['loss'][str(year)] = df_adm0['loss'].sum()
#                 if len(dict_adm['records'][adm0_i]['storms']) == 0:
#                     dict_adm['records'][adm0_i]['storms'] = [f for f in shp_files_list if any(uid in f for uid in set(df[df['adm0_code']==adm0['adm0_code']]['atcf_id'].unique().astype(str)))]
#
#             for adm1_i, adm1 in enumerate(dict_adm['records'][adm0_i]['adm1']):
#                 df_adm1 = df_year[(df_year['adm0_code'] == adm0['adm0_code']) & (df_year['adm1_code'] == adm1['adm1_code'])]
#
#                 print(f'\t\tAdm1: {adm1["adm1_code"]}')
#
#                 if not(df_adm1.empty):
#                     dict_adm['records'][adm0_i]['adm1'][adm1_i]['counter_adm1'][str(year)] = len(df_adm1['atcf_id'].unique())
#                     dict_adm['records'][adm0_i]['adm1'][adm1_i]['counter_year'][str(year)] = len(df_year['atcf_id'].unique())
#                     dict_adm['records'][adm0_i]['adm1'][adm1_i]['loss'][str(year)] = df_adm1['loss'].sum()
#                     if len(dict_adm['records'][adm0_i]['adm1'][adm1_i]['storms']) == 0:
#                         dict_adm['records'][adm0_i]['adm1'][adm1_i]['storms'] = [f for f in shp_files_list if any(uid in f for uid in set(df[(df['adm0_code']==adm0['adm0_code']) & (df['adm1_code']==adm1['adm1_code'])]['atcf_id'].unique().astype(str)))]
#
#                 for adm2_i, adm2 in enumerate(dict_adm['records'][adm0_i]['adm1'][adm1_i]['adm2']):
#                     df_adm2 = df_year[(df_year['adm0_code'] == adm0['adm0_code']) & (df_year['adm1_code'] == adm1['adm1_code']) & (df_year['adm2_code'] == adm2['adm2_code'])]
#
#                     print(f'\t\t\tAdm2: {adm2["adm2_code"]}')
#
#                     if not (df_adm2.empty):
#                         dict_adm['records'][adm0_i]['adm1'][adm1_i]['adm2'][adm2_i]['counter_adm2'][str(year)] = len(
#                             df_adm2['atcf_id'].unique())
#                         dict_adm['records'][adm0_i]['adm1'][adm1_i]['adm2'][adm2_i]['counter_year'][str(year)] = len(
#                             df_year['atcf_id'].unique())
#                         dict_adm['records'][adm0_i]['adm1'][adm1_i]['adm2'][adm2_i]['loss'][str(year)] = df_adm2['loss'].sum()
#                         if len(dict_adm['records'][adm0_i]['adm1'][adm1_i]['adm2'][adm2_i]['storms']) == 0:
#                             dict_adm['records'][adm0_i]['adm1'][adm1_i]['adm2'][adm2_i]['storms'] = [f for f in shp_files_list if any(uid in f for uid in set(df[(df['adm0_code']==adm0['adm0_code']) & (df['adm1_code']==adm1['adm1_code']) & (df['adm2_code']==adm2['adm2_code'])]['atcf_id'].unique().astype(str)))]
#
#     with open(json_adm, 'w') as f:
#         json.dump(dict_adm, f, sort_keys=True, indent=4)
#
#
#
#
# if __name__ == '__main__':
#
#     parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
#     # parser.add_argument('-s', '--storms', type=str, help='Path to json file', default='storms.json', dest='json_storms')
#     # parser.add_argument('-y', '--years', type=str, help='Path to json file', default='historyYears.json', dest='json_years')
#     parser.add_argument('-a', '--adm', type=str, help='Path to json file', default='historyAdmFromImpact.json', dest='json_adm') #TODO: switch back to historyAdm.json
#     parser.add_argument('-i', '--impact', type=str, help='Path to impact file', default='impact_15as/impact_total_adm2_15as.csv', dest='csv_impact')
#     args = parser.parse_args()
#
#     # getAllStorms(json_storms=args.json_storms)
#     getHistory(csv_impact=args.csv_impact, json_adm=args.json_adm)

import argparse
import glob
import json
import pandas as pd


def getHistory(csv_impact, json_adm):
    print("Loading data...")
    df = pd.read_csv(csv_impact)

    # --- OPTIMIZATION 1: Pre-calculate Shapefile Mappings ---
    # Doing string matching inside the deep loops is extremely slow.
    # We map Storm ID -> List of Files once.
    print("Indexing shapefiles...")
    shp_files_list_jtwc_history = glob.glob('jtwc_history/**/*_shp.geojson', recursive=True)
    shp_files_list_mpres_data = glob.glob('mpres_data/postevent/taos_swio30s_ofcl_windwater_shp/**/*.geojson',
                                          recursive=True)
    shp_files_list = shp_files_list_jtwc_history + shp_files_list_mpres_data

    # Create a lookup dict: { 'atcf_id': [file_path1, file_path2] }
    # This assumes the atcf_id is part of the filename string as per original logic
    unique_storm_ids = df['atcf_id'].unique().astype(str)
    storm_file_map = {uid: [] for uid in unique_storm_ids}

    # This is still heavy, but runs only once globally, not per admin unit
    for f in shp_files_list:
        for uid in unique_storm_ids:
            if uid in f:
                storm_file_map[uid].append(f)

    # --- OPTIMIZATION 2: Pre-calculate Global Year Counts ---
    # The 'counter_year' field is the same for every admin unit (it's the global total).
    # We calculate it once here.
    global_year_counts = df.groupby('tc_season')['atcf_id'].nunique().to_dict()
    # Ensure keys are strings to match original output format
    global_year_counts = {str(k): v for k, v in global_year_counts.items()}

    print("Processing administrative hierarchy...")

    dict_adm = {
        'counter_total': len(df['atcf_id'].unique()),
        'records': []
    }

    # --- LEVEL 0 Loop ---
    # We group by Adm0 first to avoid repeated filtering of the master DF
    for adm0_code, df_adm0 in df.groupby('adm0_code'):

        # 1. Calculate Adm0 Year Stats (The "Year Loop" is now here, inside the Adm loop)
        # groupby().agg() is much faster than iterating rows
        adm0_stats = df_adm0.groupby('tc_season').agg(
            count=('atcf_id', 'nunique'),
            loss=('loss', 'sum')
        )

        # 2. Get Storm Files for this Adm0
        # Get all unique IDs in this region
        adm0_storm_ids = df_adm0['atcf_id'].unique().astype(str)
        # Retrieve files from our pre-calculated map
        adm0_storm_files = []
        for uid in adm0_storm_ids:
            adm0_storm_files.extend(storm_file_map.get(uid, []))
        # Remove duplicates if a file matches multiple storms (rare but possible) or if logic requires set
        adm0_storm_files = list(set(adm0_storm_files))

        # 3. Build Adm0 Record
        adm0_record = {
            'adm0_code': adm0_code,
            'adm0_name': df_adm0['adm0_name'].fillna('').iloc[0],  # more efficient than unique()[0]
            'counter_adm0': {str(y): c for y, c in adm0_stats['count'].items()},
            'counter_year': global_year_counts,  # Use pre-calculated global stats
            'loss': {str(y): l for y, l in adm0_stats['loss'].items()},
            'storms': adm0_storm_files,
            'adm1': []
        }

        # --- LEVEL 1 Loop ---
        for adm1_code, df_adm1 in df_adm0.groupby('adm1_code'):

            # Calculate Adm1 Year Stats
            adm1_stats = df_adm1.groupby('tc_season').agg(
                count=('atcf_id', 'nunique'),
                loss=('loss', 'sum')
            )

            # Get Storm Files for this Adm1
            adm1_storm_ids = df_adm1['atcf_id'].unique().astype(str)
            adm1_storm_files = []
            for uid in adm1_storm_ids:
                adm1_storm_files.extend(storm_file_map.get(uid, []))
            adm1_storm_files = list(set(adm1_storm_files))

            adm1_record = {
                'adm1_code': adm1_code,
                'adm1_name': df_adm1['adm1_name'].fillna('').iloc[0],
                'counter_adm1': {str(y): c for y, c in adm1_stats['count'].items()},
                'counter_year': global_year_counts,
                'loss': {str(y): l for y, l in adm1_stats['loss'].items()},
                'storms': adm1_storm_files,
                'adm2': []
            }

            # --- LEVEL 2 Loop ---
            for adm2_code, df_adm2 in df_adm1.groupby('adm2_code'):

                # Calculate Adm2 Year Stats
                adm2_stats = df_adm2.groupby('tc_season').agg(
                    count=('atcf_id', 'nunique'),
                    loss=('loss', 'sum')
                )

                # Get Storm Files for this Adm2
                adm2_storm_ids = df_adm2['atcf_id'].unique().astype(str)
                adm2_storm_files = []
                for uid in adm2_storm_ids:
                    adm2_storm_files.extend(storm_file_map.get(uid, []))
                adm2_storm_files = list(set(adm2_storm_files))

                adm2_record = {
                    'adm2_code': adm2_code,
                    'adm2_name': df_adm2['adm2_name'].fillna('').iloc[0],
                    'counter_adm2': {str(y): c for y, c in adm2_stats['count'].items()},
                    'counter_year': global_year_counts,
                    'loss': {str(y): l for y, l in adm2_stats['loss'].items()},
                    'storms': adm2_storm_files,
                }

                adm1_record['adm2'].append(adm2_record)

            adm0_record['adm1'].append(adm1_record)

        dict_adm['records'].append(adm0_record)

    print("Saving JSON...")
    with open(json_adm, 'w') as f:
        json.dump(dict_adm, f, sort_keys=True, indent=4)
    print("Done.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments to be passed to the script')
    parser.add_argument('-a', '--adm', type=str, help='Path to json file', default='historyAdm.json',
                        dest='json_adm')
    parser.add_argument('-i', '--impact', type=str, help='Path to impact file',
                        default='impact_15as/impact_total_adm2_15as.csv', dest='csv_impact')
    args = parser.parse_args()

    getHistory(csv_impact=args.csv_impact, json_adm=args.json_adm)
