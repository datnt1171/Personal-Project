import pandas as pd

import datetime
from time import sleep
import random

from selenium import webdriver
from selenium.webdriver.common.by import By


# Declare browser
driver = webdriver.Chrome()
# Open URL
driver.get("https://courses.uit.edu.vn/login/index.php")
sleep(5)

username = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="username"]')
password = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="current-password"]')
sign_in = driver.find_element(By.CSS_SELECTOR, 'button[id="loginbtn"]')

account = "20521171"
pw = "lkjhgnhI1@"
username.send_keys(account)
password.send_keys(pw)
sign_in.click()
sleep(3)
name_list = []
email_list = []
class_list = []
ID_list = []
blank = "blank"
for i in range (7000, 8000): #16800
    driver.get(f"https://courses.uit.edu.vn/user/profile.php?id={i}")
    sleep(random.randint(5,15))
    
    #Id
    ID_list.append(i)
    #Get name
    try:
        get_name = driver.find_element(By.CLASS_NAME, "page-header-headings")
        name=get_name.text
        name_list.append(name)
    except:
        name_list.append(blank)
    
    #Get Email
    try:
        get_email = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div[1]/section/div/div/div/section[1]/div/ul/li[1]/dl/dd/a")
        email=get_email.text
        email_list.append(email)
    except:
        email_list.append(blank)
    #Get Class
    try:
        get_class = driver.find_element("xpath", "/html/body/div[1]/div[2]/div/div[1]/section/div/div/div/section[2]/div/ul/li/dl")
        class1=get_class.text
        class_list.append(class1)
    except:
        class_list.append(blank)
    
    if (i/20==0):
        sleep(30)

print(len(ID_list))
print(len(name_list))
print(len(email_list))
print(len(class_list))

now = datetime.datetime.now()
print('Crawl Job completed:', now.strftime('%Y-%m-%d %H:%M:%S'))
df_map = {"ID" : ID_list,
          "name" : name_list,
          "email": email_list,
          "class": class_list }
df=pd.DataFrame(df_map)
df.to_csv("SinhVien7k_8k.csv",index=False, encoding="utf-8-sig")