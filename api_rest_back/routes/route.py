from fastapi import FastAPI

app = FastAPI(title="Teste")

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
