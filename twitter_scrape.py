import requests
import json,csv
from json import JSONDecodeError
 
class TwitterScrape():
    def create_url(self, next_cursor = 0):
        query = "indihome"
        # Tweet fields are adjustable.
        # Options include:
        # attachments, author_id, context_annotations,
        # conversation_id, created_at, entities, geo, id,
        # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
        # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
        # source, text, and withheld
        tweet_fields = "tweet.fields=text,id,created_at,author_id,source,lang"
        max_res = "max_results=100"
        if next_cursor:
          next = "next_token={}".format(next_cursor)
        else:
          next = ""
        url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&{}&{}".format(
          query, tweet_fields, max_res, next
        )
        return url
    
    def create_headers(self):
        headers = {"Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAABfzIQEAAAAAul%2FSyDdWJMyCJRV5c92icslcKOg%3DUIgR4YXVqH0n0juwPKv1lC6JMMCpjV6AgKfmDkqnzYBjB4ZzBg"}
        return headers
    
    def connect_to_endpoint(self, url, headers):
        response = requests.request("GET", url, headers=headers)
        print("status: {}".format(response.status_code))
        try:
          return response.json()
        except JSONDecodeError:
          print("no resp")

    def manual_scrape(self):
        import re
        import datetime 

        data = []
        url = self.create_url()
        headers = self.create_headers()
        json_response = self.connect_to_endpoint(url, headers)
        for x in json_response['data']:
            z = re.sub('Z', '', x['created_at'])
            wkt = datetime.datetime.fromisoformat(z)
            tanggal = wkt.strftime('%Y-%m-%d')
            j = int(wkt.strftime('%H'))
            jam = (j+7) if j <= 16 else (j-17)
            menit = wkt.strftime('%M')
            temp = [x['text'], 
                    x['id'],
                    '{} {}:{}'.format(tanggal, str(jam), menit),
                    x['author_id'],
                    x['source'],
                    x['lang']]
            data.append(temp)
        with open("data/live_tweet.csv", "w", newline="", encoding='utf8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    
    def main(self, next_cursor=0):
        data = []
        url = self.create_url(next_cursor)
        headers = self.create_headers()
        json_response = self.connect_to_endpoint(url, headers)
        for x in json_response['data']:
            data.append(x)
        with open("test_indihome.json", "a+") as f:
            json.dumps(data, f, indent=4, sort_keys=True)
        # print(json.dumps(json_response['data'], indent=4, sort_keys=True))
        is_next = json_response['meta']['next_token']
        if is_next:
            self.main(is_next)
