from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# 1. Configura a pasta de arquivos estu00e1ticos (CSS, imagens)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Configura a pasta onde estu00e1 o seu index.html (ex: pasta 'templates')
templates = Jinja2Templates(directory="templates")

# 3. Rota principal para renderizar a pu00e1gina


@app.get("/", response_class=HTMLResponse)
async def ler_pagina(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    
@app.get("/cadastro", response_class=HTMLResponse)
async def ler_cadastro(request: Request):
    return templates.TemplateResponse("cadastro.html", {"request": request})

@app.get("/recuperar", response_class=HTMLResponse)
async def ler_recuperar(request: Request):
    return templates.TemplateResponse("recuperar.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
