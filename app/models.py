from sqlalchemy import ForeignKey, Numeric, String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from decimal import Decimal
from datetime import datetime
from sqlalchemy import func
import pytz
from database import Base


class Usuarios(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    whatsapp: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status_acesso: Mapped[str] = mapped_column(String(30), default='ativo')
    contador_erro: Mapped[int] = mapped_column(Integer, default=0)
    bloqueado_ate: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=None, nullable=True
    )
    fuso_horario: Mapped[str] = mapped_column(
        String(50), default='America/Sao_Paulo')
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    assinantes: Mapped["Assinantes"] = relationship(
        back_populates="usuarios",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    produtos: Mapped[list["Produtos"]] = relationship(
        back_populates="usuarios",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    config_robo: Mapped["ConfigRobo"] = relationship(
        back_populates="usuarios",
        cascade="all, delete-orphan", lazy="selectin")
    estado_conversas: Mapped["EstadoConversas"] = relationship(
        back_populates="usuarios",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class Assinantes(Base):
    __tablename__ = "assinantes"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False)
    plano: Mapped[str] = mapped_column(String(20), default='trial')
    data_adesao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    fuso_horario: Mapped[str] = mapped_column(
        String(50), default='America/Sao_Paulo')
    vencimento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    status_pagamento: Mapped[str] = mapped_column(String(20), default='ativo')
    ja_usou_trial: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)

    usuarios: Mapped["Usuarios"] = relationship(back_populates="assinantes")


class Produtos(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False)
    nome_produto: Mapped[str] = mapped_column(String(20), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    descricao: Mapped[str] = mapped_column(String(500), nullable=True)
    link_checkout: Mapped[str] = mapped_column(String(255), nullable=False)
    link_video: Mapped[str] = mapped_column(String(255), nullable=True)
    forma_pagamento: Mapped[str] = mapped_column(nullable=False)
    palavra_gatilho: Mapped[str] = mapped_column(String(50), nullable=False)
    usuarios: Mapped["Usuarios"] = relationship(back_populates="produtos")


class ConfigRobo(Base):
    __tablename__ = "config_robo"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False)
    instancia_zap: Mapped[str] = mapped_column(nullable=True)
    numero_robo: Mapped[str] = mapped_column(unique=True, nullable=True)
    token_whatsapp: Mapped[str | None] = mapped_column(
        String(100), nullable=True)
    token_site: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_ia: Mapped[str] = mapped_column(String(500), nullable=False)
    tempo_min: Mapped[int | None] = mapped_column(
        Integer, default=5, nullable=False)
    tempo_max: Mapped[int | None] = mapped_column(
        Integer, default=5, nullable=False)
    prompt_sistema: Mapped[str] = mapped_column(Text, nullable=True)

    usuarios: Mapped["Usuarios"] = relationship(back_populates="config_robo")


class EstadoConversas(Base):
    __tablename__ = "estado_conversas"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False)
    status_conversa: Mapped[str] = mapped_column(
        String(20), default="saudacao", nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    numero_cliente: Mapped[str] = mapped_column(String(20), nullable=False)

    usuarios: Mapped["Usuarios"] = relationship(
        back_populates="estado_conversas")
