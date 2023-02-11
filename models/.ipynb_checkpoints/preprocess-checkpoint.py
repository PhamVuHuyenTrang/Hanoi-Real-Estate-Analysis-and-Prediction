import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
import joblib

class EstateData:
    
    def __init__(self, path:str):
        self.path = path
        self.data = pd.read_csv(path)
        self.districts = self.data["District"][self.data.Area.notna()]
        self.data = self.data[self.data.Area.notna()]
        self.data["PricePerM2"] = self.data["Price"]/self.data["Area"]
        self.data = self.data[['House Direction', 'Balcony Direction', 'Toilets','Bedrooms', 
           'Legits', 'Floors', 'Facade', 'Entrance', "Area", 'X', 'Y',
            "PricePerM2"]]
        
        cates = ["House Direction", "Balcony Direction",  "Toilets", "Legits", "Floors", "Bedrooms"]
        for f in cates:
             self.data[f] = self.data[f].astype("category")
        
        self.train = None
        self.test = None
        
    def split_data(self, test_size:int=0.2, random_state:int=0, stratify=True):
        if stratify:
            train, test = train_test_split(self.data, test_size = test_size, stratify=self.districts, random_state=random_state)
        else:
            train, test = train_test_split(self.data, test_size = test_size, random_state=random_state)
        self.train = train
        self.test = test
        
    def tukey_fence(self, series, target=None):
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        mask = ~((series < (Q1 - 1.5 * IQR)) |(series > (Q3 + 1.5 * IQR)))
        if target is not None:
            mask = ~((target < (Q1 - 1.5 * IQR)) |(target > (Q3 + 1.5 * IQR)))
        return mask
    
    def hard_fence(self, series):
        mask = (series> series.quantile(0.05)) & (series < series.quantile(0.95))
        return mask
    
    def preprocess(self, tukey=True):
        data = self.train
        #fill missing values
        #amean = data["Area"].mean()
        old_entrance = data["Entrance"][data["Entrance"].notna()]
        old_facade = data["Facade"][data["Facade"].notna()]
        print("Start Process!")
        fmean = data["Facade"][data["Facade"].notna()].mean()
        emean = data["Entrance"][data["Entrance"].notna()].mean()
        #data["Area"].fillna(value=data["Area"].mean(), inplace=True)
        data["Facade"].fillna(value=fmean, inplace=True)
        data["Entrance"].fillna(value=emean, inplace=True)
        
        #self.test["Area"].fillna(value=amean, inplace=True)
        self.test["Facade"].fillna(value=fmean, inplace=True)
        self.test["Entrance"].fillna(value=emean, inplace=True)
        
        print("Fill missing values: Done")
        
        #data["PricePerM2"] = data["Price"]/data["Area"]
        data = data[data["PricePerM2"] <= 5000]
        data = data[data["PricePerM2"] >= 10]
        #self.test["PricePerM2"] = self.test["Price"]/self.test["Area"]
        self.test = self.test[self.test["PricePerM2"]<=5000]
        self.test = self.test[self.test["PricePerM2"]>=10]
        #remove outlier
        if tukey:
            mask = self.tukey_fence(data["Area"])
            mask = mask & self.tukey_fence(data["PricePerM2"])
            #mask = mask & self.tukey_fence(old_entrance, data["Entrance"])
            mask = mask & self.tukey_fence(old_facade, data["Facade"])
            data = data[mask]
        else:
            mask = self.hard_fence(data["Area"])
            mask = mask & self.hard_fence(data["PricePerM2"])
            #mask = mask & self.hard_fence(old_entrance, data["Entrance"])
            mask = mask & self.hard_fence(old_facade, data["Facade"])
            data = data[mask]
        print("Remove outlier: Done")
        #scale features
        scaler = RobustScaler()
        features_ = ['Facade', 'Entrance', "Area"]
        data[features_] = scaler.fit_transform(data[features_])
        self.test[features_] = scaler.transform(self.test[features_])
        joblib.dump(scaler, "log/scaler1.pkl") 
        
        scaler = StandardScaler()
        features_ = ['X', 'Y']
        data[features_] = scaler.fit_transform(data[features_])
        self.test[features_] = scaler.transform(self.test[features_])
        joblib.dump(scaler, "log/scaler2.pkl") 
        print("Scale features: Done")
        
        self.train = data
        