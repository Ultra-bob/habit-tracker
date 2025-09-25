from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"]
)
counter = 0

@app.post("/increment")
def increment_counter():
    global counter
    counter += 1
    return {"counter": counter}

@app.get("/counter")
def get_counter():
    return {"counter": counter}