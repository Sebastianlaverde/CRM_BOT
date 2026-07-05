from fastapi import FastAPI

app = FastAPI(
    title="LeadFlow CRM",
    version="1.0"
)

@app.get("/")
def inicio():
    return {
        "mensaje": "LeadFlow funcionando"
    }