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

# Other URL links
# https://cryptomufasa.com/category/bitcoin-news/
# https://cryptomufasa.com/category/ethereum-news/


class BlogSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://cryptomufasa.com/category/altcoin-news/']
    data = {}

    def parse(self, response):
        news_list = response.css("div.jeg_heroblock_wrapper").get()
        soup = BeautifulSoup(news_list, "html.parser")
        articles = soup.find_all('article', class_="jeg_post")

        for article in articles:
            output = article.find('div', class_="thumbnail-container")
            if output != None:
                imageUrl = output.get('data-src')
                heading = article.find('h2', class_="jeg_post_title").find('a').text
                redirected_url = article.find('a').get('href')
                time = article.find('div', class_="jeg_meta_date").find('a').text

                yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "time": time, "imageUrl": imageUrl})
                
        news_list = response.css("div.jeg_posts > article").getall()
        
        for news in news_list:
            soup = BeautifulSoup(news, "html.parser")
            imageUrl = soup.find('div', class_="thumbnail-container").find('img').get("data-src")
            heading = soup.find('h3', class_="jeg_post_title").find('a').text
            time = soup.find('div', class_="jeg_meta_date").find('a').text
            redirected_url = soup.find('h3', class_="jeg_post_title").find('a').get("href")

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "time": time, "imageUrl": imageUrl})
  

    def parse_redirected(self, response):
        author = response.css('div.jeg_meta_author > a::text').get()
        detail_data = response.css('.entry-content > div.content-inner > p').getall()

        content = ""
        for data in detail_data:
            soup = BeautifulSoup(data, "html.parser")
            content += soup.text

        n = random.random()

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
