from fastapi import FastAPI, HTTPException
from joblib import load
from pydantic import BaseModel
import pandas as pd
import xgboost as XGB
from geopy.geocoders import Nominatim

class parameters(BaseModel):
    Model: str
    House_Direction: str
    Balcony_Direction: str
    Toilets: int
    Bedrooms: int
    Floors: int
    Legits: str
    Facade: float
    Entrance: float
    Area: float
    Ward:str
    District:str
    
def get_inputs(features):
    inputs = {
            "House Direction": features.House_Direction,
            "Balcony Direction": features.Balcony_Direction,
            "Toilets":int(features.Toilets),
            "Bedrooms":int(features.Bedrooms),
            "Legits":features.Legits,
            "Floors": int(features.Floors),
            "Facade":float(features.Facade),
            "Entrance":float(features.Entrance),
            "Area": float(features.Area)
        }
    inputs["Toilets"] = "10+" if inputs["Toilets"] > 10 else str(inputs["Toilets"])
    inputs["Bedrooms"] = "10+" if inputs["Bedrooms"] > 10 else str(inputs["Bedrooms"])
    inputs["Floors"] = "10+" if inputs["Floors"] > 10 else str(inputs["Floors"])
    
    legits = ""
    if "đỏ" in inputs["Legits"]:
        legits +="+đỏ"
    if "hồng" in inputs["Legits"]:
        legits += "+hồng"
    inputs["Legits"] = legits if len(legits) > 0 else "None"
    loc = Nominatim(user_agent="GetLoc")
    getLoc = loc.geocode(features.Ward+" "+features.District)
    if getLoc is None:
        raise HTTPException(status_code=400, 
                            detail = "Invalid Address")
    inputs["X"] = getLoc[-1][0]
    inputs["Y"] = getLoc[-1][1]
    data = pd.DataFrame({i:[inputs[i]] for i in inputs})
    data = data[['House Direction', 'Balcony Direction', 'Toilets','Bedrooms', 
           'Legits', 'Floors', 'Facade', 'Entrance', "Area",'X', 'Y'
            ]]
    cates = ["House Direction", "Balcony Direction",  "Toilets", "Legits", "Floors", "Bedrooms"]
    for f in cates:
         data[f] = data[f].astype("category")
            
    scaler = load("models/scaler1.pkl")
    features_ = ['Facade', 'Entrance', "Area"]
    data[features_] = scaler.transform(data[features_])
    
    scaler = load("models/scaler2.pkl")
    features_ = ['X', 'Y']
    data[features_] = scaler.transform(data[features_])
    return data
    
    
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Hanoi Estate Prediction"}

@app.post("/predict_price")
def predict_price(features: parameters):
    name_models = ["XGBoost", "ANN", "LinearRegression", "KNNs"]
    if(features.Model not in name_models):
        raise HTTPException(status_code=400, 
                            detail = "Invalid input")
    inputs = get_inputs(features)
    results = {}
    if features.Model == "XGBoost":
        xgb = load("models/best_tree.pkl")
        results["Price"] = str(xgb.predict(inputs)[0])
    return results
