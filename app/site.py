from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router_site = APIRouter(tags=["Telas do Site"])


@router_site.get("/", response_class=HTMLResponse)
async def home():
    # pagina inicial do site
    return "<h1>Pagina Inicial do JireBot</h1>"
