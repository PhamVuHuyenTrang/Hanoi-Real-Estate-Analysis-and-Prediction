import random
#import re
from datetime import date
#from urllib.request import urlretrieve
from IPython.display import clear_output
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
#from selenium.webdriver.common.by import By
from lxml import etree
import json
import time
import traceback
import os
from tqdm import tqdm


class crawling:
    
    def __init__(self,):
        self.home_page = "https://batdongsan.com.vn/nha-dat-ban-ha-noi"
        self.root = "https://batdongsan.com.vn"
        self.page = 1
    
    def get_pages(self, page_source):
        bs = BeautifulSoup(page_source)
        page = etree.HTML(str(bs))
        links = [i.getchildren()[0].get("href") for i in page.xpath("""//*[@id="product-lists-web"]/div""")]
        links = [link for link in links if link != None]
        return [self.root+link for link in links]
    
    def next_page(self):
        self.page += 1
        return self.home_page + f"/p{self.page}"
    
    def gather(self, page_source):
        data = {}
        bs = BeautifulSoup(page_source)
        page = etree.HTML(str(bs))
        
        #get address
        address = page.xpath("""//*[@id="product-detail-web"]/span""")[0].text
        address = [i.strip() for i in address.split(",")[::-1]]
        data["address"] = address
        
        #get general description
        descrip = "".join(page.xpath("""//*[@id="product-detail-web"]/div[2]""")[0].getchildren()[1].itertext())
        data["gen_descrip"] = descrip
        
        #get detailed description
        des_elements = page.xpath("""//*[@id="product-detail-web"]/div[3]/div/div""")[0].getchildren()
        for feature in des_elements:
            key = feature.getchildren()[1].text
            value = feature.getchildren()[2].text
            data[key] = value
            
        #other insformation
        oelements = bs.find_all("div", {"class": "re__pr-short-info-item js__pr-config-item"})
        try:
            for feature in oelements:
                feature = feature.find_all("span")
                key = feature[0].text
                value = feature[1].text
                data[key] = value
            if "Mã tin" in data:
                data["id"] = "batdongsan_com_vn_" + str(data["Mã tin"])
            else:
                data["id"] = "batdongsan_com_vn_" + str(time.time())
        except Exception as e:
            print(e)
            import pdb
            pdb.set_trace()
        return data
    
    def run(self, start, num_of_pages):
        service = webdriver.edge.service.Service("edgedriver_win64\msedgedriver.exe")
        driver = webdriver.Edge(service=service)
        url = self.home_page
        self.page = 1
        if start != 1:
            self.page = start
            url = self.home_page+f"/p{self.page}"
        if os.path.exists("data/index.json"):
            with open("data/index.json") as f:
                index = set(json.load(f))
        else:
            index = set()
            
        with open("log.txt", "w") as f:
            pass
        
        dataset = []
        for i in range(num_of_pages):
            num = 10
            pages = []
            while num > 0:
                try:
                    driver.get(url)
                    time.sleep(0.05)
                    pages = self.get_pages(driver.page_source)
                    driver.delete_all_cookies()
                    break
                except:
                    num -= 1
            if num <= 0:
                url = self.next_page()
                continue
            #driver.close()
            #service = webdriver.edge.service.Service("edgedriver_win64\msedgedriver.exe")
            #driver = webdriver.Edge(service=service)
            for page in tqdm(pages):
                num = 10
                while num > 0:
                    try:
                        driver.get(page)
                        time.sleep(0.05)
                        data = self.gather(driver.page_source)
                        if data["id"] not in index:
                            dataset.append(data)
                            index.add(data["id"])
                        with open("log.txt", "a") as f:
                            f.write("Success:" + page +"\n")
                        driver.delete_all_cookies()
                        break
                    except Exception as e:
                        print(e)
                        with open("log.txt", "a") as f:
                            f.write(f"Excution{10-num}: {page}"+"\n") 
                            f.write(traceback.format_exc()+"\n")
                        driver.delete_all_cookies()
                        num -= 1
            url = self.next_page()
        if len(dataset) != 0:
            df = pd.DataFrame(dataset)
            df.to_csv(f"data/{start}_{start+num_of_pages}_{time.time()}.csv", index=False)
        with open("data/index.json", "w") as f:
            json.dump(list(index), f)
        driver.close()
        

if __name__ == "__main__":
    craw = crawling()
    for i in tqdm(range(1039, 2670)):
        craw.run(i, 1)
        clear_output()