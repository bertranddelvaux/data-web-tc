import json

###################################################################
# mapping exp_id -> (adm0,adm1,adm2)                              #
###################################################################
data = {}
for jsonFile in [f'mapping_{i}.json' for i in range(8)]:
    with open(jsonFile, 'r') as f:
        data.update(json.load(f))

with open('../mapping.json', 'w') as f:
    f.write(json.dumps(data, separators=(',', ':')))

print()