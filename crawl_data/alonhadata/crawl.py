from bs4 import BeautifulSoup
from tqdm import tqdm
from IPython.display import clear_output
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import json
import os
import time
import traceback
from lxml import etree


class crawling:
    def __init__(self,):
        self.root = "https://alonhadat.com.vn"
        self.home_page = "https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/ha-noi.html"
        self.page = 1

    def get_pages(self, page_source):
        bs = BeautifulSoup(page_source)
        page = etree.HTML(str(bs))
        elements = bs.find_all("div", {"class": "ct_title"})
        data = []
        try:
            for feature in elements:
                feature = feature.find_all('a', href=True)
                data.append(feature[0]['href'])
        except Exception as e:
            print(e)
        return data

    def next_page(self):
        self.page += 1
        return self.home_page[:-5] + f"/trang--{self.page}.html"

    def gather(self, page_source):
        data = {}
        return data

    def run(self, start, num_of_pages):
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        url = self.home_page
        self.page = 1
        if start != 1:
            self.page = start
            url = self.home_page[:-5] + f"/trang--{self.page}.html"
            print(url)

        """if os.path.exists("data/index.json"):
            with open("data/index.json") as f:
                index = set(json.load(f))
        else:
            index = set()"""
        
        dataset = []
        for i in range(num_of_pages):
            num = 20
            pages = []
            while num > 0:
                try:
                    driver.get(url)
                    time.sleep(0.05)
                    pages = self.get_pages(driver.page_source)
                    print("Number of page:", len(pages))
                    driver.delete_all_cookies()
                    break
                except Exception as e:
                    print(e)
                    num -= 1
                    print("decreased")
            if num <= 0:
                url = self.next_page()
                continue
            for page in tqdm(pages):
                try:
                    driver.get(self.home_page)   
                    driver.implicitly_wait(0.5) 
                    data = self.gather(driver.page_source)
                    """if data['id'] not in index:
                        dataset.append(data)
                        index.add(data['id'])"""
                    with open("log.txt", "a") as f:
                        f.write("Success: " + page + "\n")
                    driver.delete_all_cookies()
                    break

                    """text_box = driver.find_element(by=By.NAME, value="my-text")
                    submit_button =driver.find_element(by=By.CSS_SELECTOR, value="button") 
                    text_box.send_keys("Selenium")
                    submit_button.click()
                    value = message.text"""
                    
                except Exception as e:
                    print(e)
                    with open("log.txt", 'a') as f:
                        f.write(f"Execution{10-num}: {page}" + "\n")
                        f.write(traceback.format_exc()+"\n")
                    driver.delete_all_cookies()
                    num -= 1
            url = self.next_page()

        """with open("data/index.json", "w") as f:
            json.dump(list(index), f)"""
        driver.quit()


craw = crawling()
for i in tqdm(range(4,5)):
    craw.run(i, 1)
    clear_output()
