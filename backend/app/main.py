from fastapi import FastAPI
#Tá a importando a porra da classe pra criar a aplicação web
app = FastAPI(title = "Recomendador semântico de Livros")

@app.get("/health")

def health():
    return {"status":"ok"}