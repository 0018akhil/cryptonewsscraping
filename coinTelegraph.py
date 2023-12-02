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

# https://cointelegraph.com/tags/bitcoin
# https://cointelegraph.com/tags/ethereum
# https://cointelegraph.com/tags/altcoin

class BlogSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://cointelegraph.com/tags/altcoin']
    data = {}

    def parse(self, response):
        grids = response.css('ul.posts-listing__list')
        lis = grids.css('li')
        for items in lis:
            heading = items.xpath('article/div/div[1]/a/span/text()').get()
            time = items.xpath('article/div/div[1]/div/time/text()').get()
            author = items.xpath('article/div/div[1]/div/p/a/text()').get()
            summary = items.xpath('article/div/p/text()').get()
            href = items.xpath('article/div/div[1]/a/@href').extract()[0]
            redirected_url = "".join(["https://cointelegraph.com", href])

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "time": time, "author": author, "summary": summary})

    def parse_redirected(self, response):
        img_srcset = response.css('.post-cover__image > picture > source::attr(srcset)').get()
        detail_data = response.css('div.post-content > p::text').getall()
        content = " ".join(detail_data)

        n = random.random()
        
        scrapted_content = {
            'imageUrls': img_srcset.split(", "),
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
        mycol.insert_one(output)
        self.data[n] = output

    def closed(self, reason):
        with open('output.json', 'w') as json_file:
            json.dump(self.data, json_file)