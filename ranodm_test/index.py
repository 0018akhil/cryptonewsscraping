""" from bs4 import BeautifulSoup
import urllib3

n = 100000000000

for i in range(n):
    http = urllib3.PoolManager()
    url = 'https://www.myaltpay.com/'
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data)
    print(soup) """
import requests

def visit_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Visited website:", url)

# Configure the bot to visit the following websites:
websites = ["https://www.google.com", "https://www.amazon.com", "https://www.facebook.com"]

# Launch the bot:
for website in websites:
    visit_website(website)