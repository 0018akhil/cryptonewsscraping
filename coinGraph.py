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

# https://coingape.com/category/ethereum-news/
# https://coingape.com/category/news/altcoin-news/
# https://coingape.com/category/news/bitcoin-news/

class BlogSpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://coingape.com/category/ethereum-news/']
    data = {}

    def parse(self, response):
        news_list = response.css('div.Lispdat > div > div').getall()

        soup_one = BeautifulSoup(news_list[0], "html.parser")

        imageUrl = soup_one.find('a').find('img').get('data-lazy-src')
        redirected_url = soup_one.find('a').get('href')
        heading = soup_one.find('div', class_="listbgdata").text
        time = soup_one.find('span', class_="newstimes").text
        author = soup_one.find('span', class_="NewsCats").find('a').text

        yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "imageUrl": imageUrl, 'author': author, 'time': time})

        soup_two = BeautifulSoup(news_list[1], "html.parser")
        news_list = soup_two.find_all('div', class_="Newslists")

        for news in news_list:
            heading = news.find('h5').find('a').text
            redirected_url = news.find('div', class_="newsHomeImg").find('a').get('href')
            time = news.find('span', class_="newstimes").text
            author = news.find('span', class_="NewsCats").find('a').text
            imageUrl = news.find('div', class_="newsHomeImg").find('a').find('img').get('data-lazy-src')

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "imageUrl": imageUrl, 'author': author, 'time': time})

        news_list = response.css("div.newscoverga").getall()

        for news in news_list:
            soup = BeautifulSoup(news, "html.parser")
            heading = soup.find('div', class_="covertitle_edu").text
            time = soup.find('span', class_="newstimes").text
            author = soup.find('span', class_="NewsCats").find('a').text
            imageUrl = soup.find('div', class_="covergimg").find('img').get('data-lazy-src')
            redirected_url = soup.find('div', class_="covergadata").find('a').get('href')

            yield scrapy.Request(redirected_url, callback=self.parse_redirected, meta={"heading": heading, "imageUrl": imageUrl, 'author': author, 'time': time})
   
    def parse_redirected(self, response):
        main = response.css('div.main > p::text').getall()
        content = "".join(main)
        
        n = random.random()
        
        scrapted_content = {
            'imageUrls': [response.meta['imageUrl']],
            'headline': response.meta['heading'],
            'category_id': "6528eb0f97a0b6af8b874857", 
            'category': "Ethereum News",
            'summary': content[:100],
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