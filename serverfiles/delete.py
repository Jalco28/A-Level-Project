import sys
import json
import os

os.chdir(os.path.dirname(__file__))

banned_username=sys.argv[1]

with open('record.json', 'r', encoding='utf-8') as f:
    records = json.load(f)

records = [record for record in records if record['username'] != banned_username]

with open('record.json', 'w', encoding='utf-8') as f:
    json.dump(records, f)
