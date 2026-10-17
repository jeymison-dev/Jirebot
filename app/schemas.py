from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime
from decimal import Decimal


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2)
    email: EmailStr
    whatsapp: str = field(..., min_lenght=10, max_lenght=20)
    senha: str = Field(..., min_length=8)


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class RespostaUsuarios(BaseModel):
    id: int
    nome: str
    email: EmailStr
    tentativas_erradas: int
    bloqueado_ate: Optional[datetime]
    status_login: str

    class Config:
        from_attributes = True


class AssinanteCreate(BaseModel):

    plano: str = "trial"
    fuso_horario: str = "America/Sao_Paulo"


class AssinanteResponse(BaseModel):
    id: int
    tenant_id: int
    usuario_id: int
    plano: str
    data_adesao: datetime
    fuso_horario: str
    vencimento: datetime
    status_pagamento: str

    class Config:
        from_attributes = True


class ProdutoCreate(BaseModel):
    nome_produto: str = Field(..., min_length=2, max_length=50)
    preco: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    descricao_produto: str = Field(..., min_length=20, max_length=250)
    link_video: HttpUrl | None = None
    link_checkout: HttpUrl
    forma_pagamento: str
    palavra_gatilho: str

    class Config:
        from_attributes = True


class ConfigRoboCreate(BaseModel):

    instancia_zap: Optional[str] = None
    numero_robo: Optional[str] = None
    token_api: Optional[str] = None
    prompt_ia: str = Field(..., max_length=500)
    tempo_resposta: int = 5  # Valor padru00e3o se o cara nu00e3o mexer


class ConfigRoboResponse(BaseModel):
    id: int
    tenant_id: int
    instancia_zap: Optional[str]
    numero_robo: Optional[str]
    token_api: Optional[str]
    prompt_ia: str
    tempo_resposta: int
    prompt_sistema: str  # Retorna o prompt escondido caso o bot precise ler

    class Config:
        from_attributes = True
