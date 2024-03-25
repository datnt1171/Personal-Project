import pandas as pd
from time import sleep
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import undetected_chromedriver as uc

# options = uc.ChromeOptions()
# options.add_argument('--blink-settings=imagesEnabled=false')

## Create Undetected Chromedriver
driver = uc.Chrome()
driver.maximize_window()
#driver.implicitly_wait(20)
driver.get('https://shopee.vn/')
sleep(5)
# Define driver


#Sign in
username = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="on"]')
password = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="current-password"]')
sign_in = driver.find_element(By.CSS_SELECTOR, 'button[class="wyhvVD _1EApiB hq6WM5 L-VL8Q cepDQ1 _7w24N1"]')
account = "0559801741"
pw = "lkjhgnhI1@"
username.send_keys(account)
sleep(3)
password.send_keys(pw)
sleep(4)
sign_in.click()
sleep(5)

WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[shopee-banner-popup-stateful]'))).click()
sleep(5)
driver.get('https://shopee.vn/')
sleep(5)



# =============================================================================
# Get Link
# =============================================================================

keyword_list = ['mi pham', 'polo', 'quan au','sneaker','mic thu am']
link_list = []

for keyword in keyword_list:
    #Insert keyword to search bar
    input_bar = driver.find_element(By.CSS_SELECTOR, 'input[class="shopee-searchbar-input__input"]')
    input_bar.send_keys(keyword)
    sleep(5)
    search_button = driver.find_element(By.CSS_SELECTOR, 'button[class="btn btn-solid-primary btn--s btn--inline shopee-searchbar__search-button"]')
    search_button.click()
    sleep(5)
    #Get max page
    max_page = driver.find_element(By.CSS_SELECTOR, 'span[class="shopee-mini-page-controller__total"]').text
    
    for page in range(0, int(max_page)-1):
        
        #Scroll down to bottom to deal with lazy loading
        sleep(random.randint(5,10))
        SCROLL_LEN = 500
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        current_height = 0
        # Scroll down to bottom
        while current_height <= (last_height + 300):
            driver.execute_script("window.scrollBy(0, "+str(SCROLL_LEN)+");")
            time.sleep(round(random.uniform(0.8, 1.2),1))
            current_height += SCROLL_LEN
            
        link_elements=driver.find_elements(By.CSS_SELECTOR, 'a[data-sqe="link"]')
        link_in_1_page=[temp.get_attribute('href') for temp in link_elements]
        link_list+= link_in_1_page
        sleep(3)
        
        next_button = driver.find_element(By.CSS_SELECTOR, 'a[class="shopee-icon-button shopee-icon-button--right"]')
        next_button.click()
    
    driver.get('https://shopee.vn/')
    sleep(5)

#Save
df_link = pd.DataFrame(link_list)

# =============================================================================
# Get Product Info
# =============================================================================

name_list = []
rating_list = []
num_rating_list = []
sold_list = []
price_list = []
discount_percent_list = []
voucher_list = []
instock_list = []
category_list = []
brand_list = []
product_description_list = []
store_list = []
cant_crawl = 'cant_crawl'
i=0
for url in link_list:
    sleep(2)
    driver.get(url)
    sleep(random.randint(5,10))
    check_point = url
    
        
    #Scroll down to bottom to deal with lazy loading
    sleep(random.randint(5,10))
    SCROLL_LEN = 750
    # Get scroll height
    last_height = 3000  #No need to scroll to the end
    current_height = 0
    # Scroll down to bottom
    while current_height <= (last_height + 300):
        driver.execute_script("window.scrollBy(0, "+str(SCROLL_LEN)+");")
        time.sleep(round(random.uniform(0.8, 1.2),1))
        current_height += SCROLL_LEN
    
    #Product Name
    try:
        get_name = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/section[1]/section[2]/div/div[1]/span')
        name = get_name.text
        name_list.append(name)
    except:
        name_list.append(cant_crawl)
        
    #Rating
    try:
        get_rating = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/section[1]/section[2]/div/div[2]/button[1]/div[1]')
        rating = get_rating.text
        rating_list.append(rating)
    except:
        rating_list.append(cant_crawl)
        
    #Number of Ratings
    try:
        get_num_rating = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/section[1]/section[2]/div/div[2]/button[2]/div[1]')
        num_rating = get_num_rating.text
        num_rating_list.append(num_rating)
    except:
        num_rating_list.append(cant_crawl)
    
    #Sold
    try:
        get_sold = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/section[1]/section[2]/div/div[2]/div/div[1]')
        sold = get_sold.text
        sold_list.append(sold)
    except:
        sold_list.append(cant_crawl)
    
    #Price
    try:
        get_price = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div/div/div/section[1]/section[2]/div/div[3]/div/div/section/div')
        price = get_price.text
        price_list.append(price)
    except:
        price_list.append(cant_crawl)
     
    #Discount Percent
    try:
        get_discount_percent = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/section[1]/section[2]/div/div[3]/div/div/section/div/div[2]/div[2]')
        discount_percent = get_discount_percent.text
        discount_percent_list.append(discount_percent)
    except:
        discount_percent_list.append(cant_crawl)
    
    #Voucher
    try:
        get_voucher = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/section[1]/section[2]/div/div[4]/div/div[1]/section/div/div/div[1]')
        voucher = get_voucher.text
        voucher_list.append(voucher)
    except:
        voucher_list.append(cant_crawl)
    
    
    #In Stock
    try:
        get_instock = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/section[1]/section[2]/div/div[4]/div/div[2]/div/section/div/div[2]')
        instock = get_instock.text
        instock_list.append(instock)
    except:
        instock_list.append(cant_crawl)
        
    #Category
    try:
        get_category = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/div[2]/div/div[1]/div[1]/section[1]/div/div[1]/div')
        category = get_category.text
        category_list.append(category)
    except:
        category_list.append(cant_crawl)
    
    #Brand
    try:
        get_brand = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/div[2]/div/div[1]/div[1]/section[1]/div/div[2]/a')
        brand = get_brand.text
        brand_list.append(brand)
    except:
        brand_list.append(cant_crawl)
        
    #Product Description
    try:
        get_product_description = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/div[2]/div/div[1]/div[1]/section[2]')
        product_description = get_product_description.text
        product_description_list.append(product_description)
    except:
        product_description_list.append(cant_crawl)
        
    #Store
    try:
        get_store = driver.find_element("xpath",'/html/body/div[1]/div/div[2]/div[1]/div[1]/div/div/div[2]/div/div[1]/div[1]/section[2]')
        store = get_store.text
        store_list.append(store)
    except:
        store_list.append(cant_crawl)
        
#To dataframe
mapping = {"product_name":name_list,
           "rating":rating_list,
           "num_rating":num_rating_list,
           "sold":sold_list,
           "price":price_list,
           "discount_percent":discount_percent_list,
           "voucher":voucher_list,
           "instock":instock_list,
           "category":category_list,
           "brand":brand_list,
           "product_description":product_description_list,
           "store":store_list}

df_product = pd.DataFrame(mapping)
#Save
df_product.to_csv("")



