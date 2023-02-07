import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler

class EstateData:
    
    def __init__(self, path:str):
        self.path = path
        self.data = pd.read_csv(path)
        self.districts = self.data["District"]
        self.data = self.data[['House Direction', 'Balcony Direction', 'Toilets','Bedrooms', 
           'Legits', 'Floors', 'Facade', 'Entrance', "Area", 'X', 'Y',
            'Price']]
        
        cates = ["House Direction", "Balcony Direction",  "Toilets", "Legits", "Floors", "Bedrooms"]
        for f in cates:
             self.data[f] = self.data[f].astype("category")
        self.train = None
        self.test = None
        
    def split_data(self, test_size:int=0.2, random_state:int=0):
        train, test = train_test_split(self.data, test_size = test_size, stratify=self.districts)
        self.train = train
        self.test = test
        
    def tukey_fence(self, series):
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        mask = ~((series < (Q1 - 1.5 * IQR)) |(series > (Q3 + 1.5 * IQR)))
        return mask
    
    def hard_fence(self, series):
        mask = (series> series.quantile(0.05)) & (series < series.quantile(0.95))
        return mask
    
    def preprocess(self, tukey=True):
        data = self.train
        #fill missing values
        amean = data["Area"].mean()
        fmean = data["Facade"].mean()
        emean = data["Entrance"].mean()
        data["Area"].fillna(value=data["Area"].mean(), inplace=True)
        data["Facade"].fillna(value=data["Facade"].mean(), inplace=True)
        data["Entrance"].fillna(value=emean, inplace=True)
        
        
        self.test["Area"].fillna(value=amean, inplace=True)
        self.test["Facade"].fillna(value=fmean, inplace=True)
        self.test["Entrance"].fillna(value=emean, inplace=True)
        
        data["PricePerM2"] = data["Price"]/data["Area"]
        data = data[data["PricePerM2"] <= 5000]
        data = data[data["PricePerM2"] >= 10]
        self.test["PricePerM2"] = self.test["Price"]/self.test["Area"]
        self.test = self.test[self.test["PricePerM2"]<=5000]
        self.test = self.test[self.test["PricePerM2"]>=10]
        
        #remove outlier
        if tukey:
            mask = self.tukey_fence(data["Area"])
            mask = mask & self.tukey_fence(data["Price"])
            #mask = mask & self.tukey_fence(data["Entrance"])
            mask = mask & self.tukey_fence(data["Area"])
            data = data[mask]
        else:
            mask = self.hard_fence(data["Area"])
            mask = mask & self.hard_fence(data["Price"])
            #mask = mask & self.hard_fence(data["Entrance"])
            mask = mask & self.hard_fence(data["Area"])
            data = data[mask]
        print(data.shape)
        #scale features
        scaler = RobustScaler()
        features_ = ['Facade', 'Entrance']
        data[features_] = scaler.fit_transform(data[features_])
        self.test[features_] = scaler.transform(self.test[features_])
        
        scaler = StandardScaler()
        features_ = ['X', 'Y', "Area"]
        data[features_] = scaler.fit_transform(data[features_])
        self.test[features_] = scaler.transform(self.test[features_])
        
        self.train = data
        