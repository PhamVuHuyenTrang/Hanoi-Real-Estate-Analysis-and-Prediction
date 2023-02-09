from fastapi import FastAPI, HTTPException
from joblib import load

app = FastAPI()
@app.get("/")
def root():
    return {"message": "Welcome to Your Sentiment Classification FastAPI"}

@app.post("/predict_sentiment")
def predict_sentiment(features):
    if(not(features)):
        raise HTTPException(status_code=400, 
                            detail = "Invalid input")

    return {
            "waiting": features, 
           }
