import os
import json
import re

dict_storms = {}
mapping_storms = {}
dirs = ['mpres_data']

def extract_id(file_path):
    # Regular expression to match 'SH' followed by 6 digits
    match = re.search(r"SH\d{6}", file_path)
    if match:
        return match.group(0)  # Extract and return the matched string
    return None

with open('index.json', 'r') as f:
    dict_files = json.load(f)

for dir in dirs:
    for file in dict_files[dir]:
        if dir == 'mpres_data':
            dict_storms.setdefault(dir, [])
            if 'ofcl_15as_nc' in file and not(file.endswith('.json')) and not(file.endswith('.csv')):
                storm_id = extract_id(file) #f'SH{file.split("/SH")[1].split("_")[0].split(".")[0]}'
                loss_file = f'mpres_data/postevent/ofcl_15as_nc/{storm_id}_losses_adm.json'
                shp_file = f'mpres_data/postevent/taos_swio30s_ofcl_windwater_shp/taos_swio30s_ofcl_windwater_shp_{storm_id}.geojson'

                if loss_file in dict_files[dir]:

                    # Step 1: Check if the shp_file exists
                    if not os.path.exists(shp_file):
                        print(f"{shp_file} not found. Searching in jtwc_history directory...")

                        # Step 2: Search for .geojson files with {storm_id} in their name in the jtwc_history directory and subdirectories
                        jtwc_history_dir = 'jtwc_history'
                        found_file = None
                        for root, dirs, files in os.walk(jtwc_history_dir):
                            for f in files:
                                if f'{storm_id}' in f and f.endswith('.geojson'):
                                    found_file = os.path.join(root, f)

                        # Step 3: Update shp_file if a match is found
                        if found_file:
                            shp_file = found_file
                        else:
                            print(f"No file found containing {storm_id} in the name.")

                    if shp_file in dict_files[dir] or os.path.exists(shp_file):
                        if storm_id not in [s['id'] for s in dict_storms[dir]]:
                            rec = {'id': storm_id}
                            dict_storms[dir].append(rec)
                        i = [i for i, s in enumerate(dict_storms[dir]) if s['id'] == storm_id][0]
                        dict_storms[dir][i]['nc'] = file
                        dict_storms[dir][i]['losses'] = loss_file
                        dict_storms[dir][i]['shp'] = shp_file
                        with open(file, 'r') as f:
                            data = json.load(f)
                        dict_storms[dir][i]['storm_name'] = data['storm']['name']
                        dict_storms[dir][i]['bbox'] = data['bbox']
                        with open(shp_file, 'r') as f_shp:
                            data_shp = json.load(f_shp)
                        try:
                            date = re.search(r'\d{4}-\d{2}-\d{2}', data_shp['features'][0]['properties']['DTG']).group()
                        except:
                            date = None
                        dict_storms[dir][i]['date'] = date

with open('latestStorms_15as.json', 'w') as f:
    json.dump(dict_storms, f, sort_keys=True, indent=4)
