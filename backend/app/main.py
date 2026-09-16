from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Pricey backend is running"}