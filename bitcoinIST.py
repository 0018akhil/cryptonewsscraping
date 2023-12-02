import json
import scrapy
import random
from bs4 import BeautifulSoup
import pymongo
from deep_translator import GoogleTranslator

def lang_trans(content_obj):

    output = {}
    translator_german = GoogleTranslator(source='english', target='german')
    translator_japanese = GoogleTranslator(source='english', target='japanese')
    translator_italian = GoogleTranslator(source='english', target='italian')
    translator_portuguese = GoogleTranslator(source='english', target='portuguese')
    translator_french = GoogleTranslator(source='english', target='french')
    translator_spanish = GoogleTranslator(source='english', target='spanish')

    main_transulator = {"DE":translator_german, "JP":translator_japanese, "IT":translator_italian, "PT":translator_portuguese, "FR":translator_french, "ES":translator_spanish}

    for key in main_transulator:
        headline = main_transulator[key].translate(content_obj['headline'])
        summary = main_transulator[key].translate(content_obj['summary'])
        content = main_transulator[key].translate(content_obj['content'])
        output[key] = {
            "headline": headline,
            "summary": summary,
            "content": content
        }
    
    content_obj['languages'] = output

    return content_obj


uri = "mongodb+srv://newsappDBuser:W7itrf9uJqatKBjp@cluster0.2x3kk.mongodb.net/"

myclient = pymongo.MongoClient(uri)
mydb = myclient["news_db"]
mycol = mydb["news"]

tags = ["featurednews", "trendingnews", "breakingnews", "latestnews"]


class BlogSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://bitcoinist.com/category/bitcoin/']
    
    data = {}

    def parse(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        news_list = response.css("div.archive-posts > article").getall()

        for news in news_list:
            soup = BeautifulSoup(news, "html.parser")
            imageUrl = soup.find('img', class_="wp-post-image").get("data-src")
            redirected_url = soup.find('div', class_="jeg_thumb").find('a').get("href")
            heading = soup.find('h3', class_="jeg_post_title").find('a').text
            time = soup.find('div', class_="jeg_meta_date").find('a').text
            author = soup.find('div', class_="jeg_meta_author").find('a').text
            summary = soup.find('div', class_="jeg_post_excerpt").find('p').text
            
            yield scrapy.Request(redirected_url, headers=headers, callback=self.parse_redirected, meta={"heading": heading, "time": time, "imageUrl": imageUrl, "author": author, "summary": summary})

    def parse_redirected(self, response):
        detail_data = response.css('div.entry-content > div:nth-child(2) > p').getall()
        content = ""
        for p in detail_data:
            soup = BeautifulSoup(p, "html.parser")
            content += soup.text
      
        scrapted_content = {
            'imageUrls': [response.meta['imageUrl']],
            'headline': response.meta['heading'],
            'category_id': "650d45276bb89616f4e084a0", 
            'category': "Bitcoin News",
            'summary': response.meta['summary'],
            'content': content,
            'time': response.meta['time'],
            'author': None,
            'tags': random.sample(tags, 2),
            'views': 0
        }
        n = random.random()

        output = lang_trans(scrapted_content)
        self.data[n] = output
        mycol.insert_one(output)
  

    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file)  