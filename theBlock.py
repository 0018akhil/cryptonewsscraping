import json
import time
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
    start_urls = ['https://www.theblock.co/latest']
    data = {}

    def parse(self, response):
        news_list = response.css(".collectionLatest > article").getall()

        for item in news_list:
            soup = BeautifulSoup(item, "html.parser")
            imageUrl = soup.find('div', class_="imageContainer").find('img').get('src')
            heading = soup.find('div', class_="headline").text           
            time = soup.find('div', class_="pubDate").text
            href = soup.find('div', class_="headline").find('a').get('href')
            redirected_url = "".join(["https://www.theblock.co", href])

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "time": time, "imageUrl": imageUrl})

    def parse_redirected(self, response):
        detail_data = response.css('div#articleContent > span > p').extract()
        author = response.css('.articleByline > label > a::text').get()

        n = random.random()
        content = ""
        for p in detail_data:
            soup = BeautifulSoup(p, "html.parser")
            content += soup.find('p').text

        scrapted_content = {
            'imageUrls': [response.meta['imageUrl']],
            'headline': response.meta['heading'],
            'category_id': "650d45276bb89616f4e084a0", 
            'category': "Bitcoin News",
            'summary': content[:100],
            'content': content  ,
            'time': response.meta['time'],
            'author': author,
            'tags': random.sample(tags, 2),
            'views': 0
        }

        output = lang_trans(scrapted_content)
        self.data[n] = output

        mycol.insert_one(output)


    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file)         
