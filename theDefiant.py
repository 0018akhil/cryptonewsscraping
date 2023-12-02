import datetime
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
    start_urls = ['https://thedefiant.io/news']
    data = {}

    def parse(self, response):
        site_url = "https://thedefiant.io"
        news_list = response.xpath('/html/body/div[1]/main/div/div').getall()

        for news in news_list:
            soup = BeautifulSoup(news, "html.parser")
            if soup.find('div').find('div') != None:
                redirected_url = site_url + soup.find('a', class_="hover:text-primary-hover").get('href')
                imageUrl = site_url + soup.find('div').find('div').find('img').get('src')
                heading = soup.find('h3').text
                summary = soup.find('div', class_="font-body").text
                author = soup.find('p', class_="font-body").find('a').text
                # time = soup.find('span', class_="font-body").find('template')
                # Presently giving todays time and date
                time = str(datetime.datetime.now())

                yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "summary": summary, "imageUrl": imageUrl, 'author': author, 'time': time})
            
    def parse_redirected(self, response):
        font_heading = response.css('div.font-heading').get()
        soup = BeautifulSoup(font_heading, "html.parser")
        content = soup.find('div', class_="font-heading").text

        n = random.random()
        
        scrapted_content = {
            'imageUrls': [response.meta['imageUrl']],
            'headline': response.meta['heading'],
            'category_id': "650d45276bb89616f4e084a0", 
            'category': "Bitcoin News",
            'summary': response.meta['summary'],
            'content': content,
            'time': response.meta['time'],
            'author': response.meta['author'],
            'tags': random.sample(tags, 2),
            'views': 0
        }

        output = lang_trans(scrapted_content)
        self.data[n] = output

        mycol.insert_one(output)

    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file )