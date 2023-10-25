import sys
import json
import os

os.chdir(os.path.dirname(__file__))

if len(sys.argv) == 1:
    username = 'James'
    score = '12'
    difficulty = 'A-Level'
    date = '25-10-23'
else:
    username, score, difficulty, date = sys.argv[1:]

with open('record.json', 'r', encoding='utf-8') as f:
    records = json.load(f)

records.append({'username': username,
                'score': int(score),
                'difficulty': difficulty,
                'date': date})

with open('record.json', 'w', encoding='utf-8') as f:
    json.dump(records, f)
