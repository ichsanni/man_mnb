import json
import csv
import re

temp = []

with open("test_firstmedia.json", encoding="utf8") as json_obj:
    data = json.load(json_obj)
    for x in data:
        temp.append(x)

with open("firstmedia_tweets.csv", "w", encoding="utf8", newline='') as csv_obj:
    kolom = ['text', 'author_id', 'id', 'source', 'lang', 'created_at']
    writer = csv.DictWriter(csv_obj, fieldnames=kolom)

    writer.writeheader()
    for x in temp:
        text = re.sub('\\n', '', x['text'])
        writer.writerow({'text': text, 
                        'author_id': x['author_id'],
                        'id' : x['id'],
                        'source' : x['source'],
                        'lang' : x['lang'],
                        'created_at' : x['created_at']
        })
