import math
from selenium import webdriver
from bs4 import BeautifulSoup
from googletrans import Translator
import time
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import os
import shopify
import re
from datetime import datetime
import shutil
class Product(object):

    def __init__(self, id,image,price,name,url_handle):
        self.id = id
        self.image = image
        self.price = price
        self.name = name
        self.url_handle = url_handle


def get_all_products():
    product_url = 'https://online.1kuji.com/view/item_list.html?list=release'
    browser.get(product_url)
    browser.execute_script("arguments[0].setAttribute('style','display:none')", browser.find_element(By.CSS_SELECTOR,'header'))

    time.sleep(0.5)
    browser.find_element(By.ID, 'onetrust-accept-btn-handler').click()
    future_checkbox()

    for x in range(page_counter()[0]):
        product_soup = BeautifulSoup(browser.page_source, features='html.parser')
        products = product_soup.find_all('div', class_='col-6 col-md-3 btm_30')
        for product in products:
            product_image_link = product.find('a', class_='thumb').img.get('src').replace('\n', '')
            product_id = product_image_link.replace('https://static.online.1kuji.com/storage/product/', '').replace(
                '_small.jpg', '')
            product_name = product.find('div', class_='t_title').text.replace('\n', '')
            product_url_handle = product_name.replace(' ', '-').replace('・', '-')
            product_price = product.find('div', class_='t_price').text.replace('\n', '')
            product_image = product_name + '.jpg'
            product_folder = product_name
            download_image(product_image_link,1,product_name)
            product_list.append(Product(product_id,product_image,product_price,product_name,product_url_handle))
            time.sleep(0.5)
        next_page()
        time.sleep(0.5)


def get_all_prizes():
    for product in product_list:
        prize_url = 'https://online.1kuji.com/view/item_about.html?pid='+str(product.id)
        browser.get(prize_url)
        time.sleep(1)
        prize_soup = BeautifulSoup(browser.page_source, features='html.parser')
        prizes = prize_soup.find_all('div', class_='col-md-4 col-sm-6 btm_30')
        i = 1
        x = 2
        product_html = ''
        product_date = re.sub(r'\（[^)]*\）', '', prize_soup.find('div',id='prize_date').p.text)
        print(product_date)
        for prize in prizes:

            prize_name = prize.find('div', class_='clearfix').span.text.split(' ', 1)[1].replace('\n', '').replace(' ','')
            prize_image_link = prize.find('a').get('href').replace('\n','')
            prize_id = prize_image_link.replace('https://static.online.1kuji.com/storage/prize/', '').replace(
                '.jpg', '')
            prize_type_size = browser.find_element(By.XPATH,'//*[@id="prize_list"]/div['+str(i)+']/div/div[2]').text.replace('\n','')
            prize_description = prize.find('div',class_='card card-body').p.text.replace('\n','')
            prize_tier = prize.find('div', class_='clearfix').span.text.split()[0].replace('\n', '')
            prize_html = """
            <div class="grid-item">
                <h3>{prize_tier}</h3>
                <h3>{prize_name}</h3>
                <h5>{prize_type_size}</h5>
                <img src={prize_image_link} alt="Image 1">
            </div>""".format(prize_image_link=prize_image_link,prize_tier=prize_tier,prize_name=prize_name,prize_type_size=prize_type_size)
            if prize_tier == 'ラストワン賞':
                prize_tier = 'last_one賞'
            elif prize_tier == 'ダブルチャンスキャンペーン':
                prize_tier = 'double_campaign賞'
            product_html += prize_html
            print(prize_name)
            #print(product_html)
            setattr(product,'prize_tier',prize_tier)
            setattr(product, prize_tier.replace('賞','')+'_id', prize_id)
            setattr(product, prize_tier.replace('賞','')+'_name', prize_name)
            setattr(product, prize_tier.replace('賞','')+'_type_size', prize_type_size)
            setattr(product, prize_tier.replace('賞','')+'_description', prize_description)
            setattr(product, prize_tier.replace('賞','')+'_image', prize_image_link)

            i=i+1
            download_image(prize_image_link, x, product.name)


            x=x+1
            time.sleep(0.5)
        setattr(product,'date',product_date)
        setattr(product, 'html', product_html)


        time.sleep(0.5)

def date_checker(date):
    current_datetime = datetime.now()
    datetime_obj = datetime.strptime(date, '%Y年%m月%d日%H:%M')
    # Extract individual components
    year = datetime_obj.year
    month = int(datetime_obj.strftime('%m'))
    day = datetime_obj.day
    hour = datetime_obj.hour
    minute = datetime_obj.minute
    # Compare a target date and time
    target_datetime = datetime(year, month, day, hour, minute)
    if target_datetime <= current_datetime:
        return 'past','on-sale',str(month)+'月発売'
    else :
        return 'future','pre-sale',str(month)+'月発売'
def next_page():
    wait = WebDriverWait(browser, 1)
    if page_counter()[0] >=2:
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '.fa-angle-right')))
        browser.find_element(By.CSS_SELECTOR,'.fa-angle-right').click()
    else:
        return 0


def page_counter():
    wait = WebDriverWait(browser, 1)
    wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="contents"]/div[2]/div/div[1]/div[1]/p/span[1]')))
    items_num = browser.find_element(By.XPATH, '//*[@id="contents"]/div[2]/div/div[1]/div[1]/p/span[1]').text
    button_clicks = (int(items_num)/20)
    return math.ceil(button_clicks),int(items_num)


def future_checkbox():
    wait = WebDriverWait(browser, 1)
    wait.until(ec.presence_of_element_located((By.ID, 'future')))
    browser.find_element(By.ID, 'future').click()
    time.sleep(3)


def download_image(image_url,name,folder_name):
    response = requests.get(image_url, stream=True)
    filename = str(name) + '.jpg'

    isFolderExist = os.path.exists(folder_name)and os.path.isdir(folder_name)

    if not isFolderExist:
        os.makedirs(folder_name)


    with open(os.path.join(folder_name, filename), 'wb') as f:
        f.write(response.content)


def shopify_product():

    # Authenticate with Shopify
    shopify.ShopifyResource.set_site(SHOP_URL)
    shopify.ShopifyResource.headers = {'X-Shopify-Access-Token': Admin_API_ACCESS_TOKEN}
    # Set the session for the Shopify API requests

    shopify_products = shopify.Product.find()
    delete_product_list = [shopify_product for shopify_product in shopify_products if
                           shopify_product.title not in ['['+date_checker(product.date)[2]+']'+product.name for product in product_list]]
    new_product_list = [product for product in product_list if
                        '[' + date_checker(product.date)[2] + ']' + product.name not in [shopify_product.title for
                                                                                         shopify_product in
                                                                                         shopify_products]]
    for product in delete_product_list:
        shopify.Product.delete(product.id)
    for product in new_product_list :
        images = []
        sorted_images_list = sorted(os.listdir(product.name), key=lambda x: int(x[:-4]))
        for file in sorted_images_list:
            with open(os.path.join(product.name, file), 'rb') as f:
                image = shopify.Image()
                encoded = f.read()
                image.attach_image(encoded, filename=file)

                images.append(image)
            time.sleep(0.5)
        new_product = shopify.Product()
        new_product.images = images
        # Create product variant
        variant = shopify.Variant()
        variant.price = product.price.split(' ')[1].replace('円', ' ')
        variant.metafields = [
            {
                "key": "date_of_selling",
                "value": product.date,
                "value_type": "string",
                "namespace": "date"
            }
        ]
        new_product.variants = [variant]
        new_product.handle = translator.translate(product.url_handle, src='ja', dest='en').text
        new_product.title = '['+date_checker(product.date)[2]+']'+product.name
        new_product.product_type = "figure"
        new_product.tags = date_checker(product.date)[1]
        new_product.body_html = """
            <html>
            <head>
            <style>
                .grid-container {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    grid-gap: 10px;
                }
                .grid-item {        
                    text-align: left;
                }

                .grid-item img {
                    width: 100%;
                    height: auto;
                    border: 0;
                }
                .grid-item h3,h5{
                    margin: 1% 0;
                }
                .grid-item h5{
                    color:gray ;
                }
            </style>
            <head>""" + """
            <body>
            <div class="grid-container">
                {product_html}
            </div>
            </body>
            </html>
        """.format(product_html=product.html)
        new_product.save()

    for product in delete_product_list + product_list:
        isFolderExist = os.path.exists(product.name)and os.path.isdir(product.name)
        if isFolderExist:
            # Delete the directory and its contents
            shutil.rmtree(product.name)

def main():
    get_all_products()
    get_all_prizes()
    shopify_product()

options = webdriver.ChromeOptions()
options.add_argument('headless')
#options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-gpu')
browser = webdriver.Chrome(options=options)

translator = Translator(service_urls=['translate.google.com'])
product_list = []

API_KEY = "01cfa8da6db49cd6a7988357e8922257"
API_SECRET = "9dd17e070c14c6a83005c4977fc25ccb"
Admin_API_ACCESS_TOKEN = "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"
SHOP_URL = "https://quickstart-d7f6d956.myshopify.com/admin/api/2023-07"
main()


