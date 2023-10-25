import json
import os

os.chdir(os.path.dirname(__file__))

with open('record.json', 'r', encoding='utf-8') as f:
    text = f.read()

print(text)