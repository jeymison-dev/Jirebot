from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from datetime import datetime, timedelta
import schemas
import models
import pytz
# cria  a tabela usuarios e tambem a assinantes


async def novo_usuario(db: AsyncSession, usuario: schemas.UsuarioCreate):
    """ 1. cria o usuario no banco"""
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    """faz o sistema olhar para a hora do brasil"""
    hora_brasil = datetime.now(fuso_brasil)

    # 2. Preparamos a ficha do usuu00e1rio na memu00f3ria do Python
    usuario_db = models.Usuarios(
        tenant_id=usuario.tenant_id,
        nome=usuario.nome,
        email=usuario.email,
        whatsapp=usuario.whatsapp,
        senha_hash=usuario.senha_hash,
        contador_erro=0,
        bloqueado_ate=None
    )
    db.add(usuario_db)

    await db.flush()
    # 4. Calculamos o fim do peru00edodo trial (hoje + 7 dias)
    vencimento_trial = hora_brasil + timedelta(days=7)

    # 5. Cria a assinatura amarrada no ID que veio do flush
    db_assinatura = models.Assinantes(
        tenant_id=usuario.tenant_id,
        usuario_id=usuario_db.id,
        data_adesao=hora_brasil,
        vencimento=vencimento_trial,
        plano="trial"
    )
    db.add(db_assinatura)

    # 6. Uma u00fanica viagem ao banco que grava as duas tabelas juntas
    await db.commit()

    # Atualizamos os dados na memu00f3ria
    await db.refresh(usuario_db)
    return usuario_db


async def periodo_trial(db: AsyncSession, assinante: schemas.AssinanteCreate, usuario_id: int, tenant_id: int):

    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    hora_brasil = datetime.now(fuso_brasil)

    query = select(models.Assinantes).where(
        models.Assinantes.usuario_id == usuario_id,
        models.Assinantes.tenant_id == tenant_id
    )

    resultado = await db.execute(query)
    assinante_banco = resultado.scalar_one_or_none()

    if not assinante_banco:
        return "Nenhum registro de assinatura encontrado para este usuario."

    if assinante_banco.ja_usou_trial:
        return "Acesso negado: Seu periodo de testes acabou."

    if hora_brasil < assinante_banco.vencimento:
        assinante_banco.ja_usou_trial = True
        assinante_banco.plano = "bloqueado"
        assinante_banco.status_pagamento = "bloqueado"
        await db.commit()
        return "Acabou o periodo trial"

    return "Acesso liberado"


async def mensal_30(db: AsyncSession, assinante: schemas.AssinanteCreate, usuario_id: int, tenant_id: int):

    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    hora_brasil = datetime.now(fuso_brasil)

    query = select(models.Assinantes).where(
        models.Assinantes.usuario_id == usuario_id,
        models.Assinantes.tenant_id == tenant_id
    )
    resultado = await db.execute(query)
    assinante_banco = resultado.scalar_one_or_none()

    if not assinante_banco:
        return "Nenhum plano mensal encontrado para este usuu00e1rio"

    if hora_brasil < assinante_banco.vencimento:
        assinante_banco.ja_usou_trial = True
        assinante_banco.plano = "bloqueado"
        assinante_banco.status_pagamento = "bloqueado"
        await db.commit()
        return "A assinatura mensal expirou"

    return "Acesso liberado"


async def assinar_plano_30(db: AsyncSession, usuario_id: int, tenant_id: int):
    """Atualiza o plano do usuario para 30 dias apos o fim do trial."""
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    hora_brasil = datetime.now(fuso_brasil)
    plano_mensal = hora_brasil + timedelta(days=30)

    query = select(models.assinantes).where(
        models.Assinantes.usuario_id == usuario_id,
        models.Assinantes.tenant_id == tenant_id
    )
    resultado = await db.execute(query)
    assinatura_banco = resultado.scalar_one_or_none()

    if not assinatura_banco:
        return "Assinantura nu00e3o encontrada"

    assinatura_banco.tenant_id = tenant_id
    assinatura_banco.usuario_id = usuario_id
    assinatura_banco.data_adesao = hora_brasil
    assinatura_banco.vencimento = plano_mensal
    assinatura_banco.plano = "assinante"
    assinatura_banco.status_pagamento = "ativo"

    await db.commit()
    return "Assinatura criada com sucesso"


async def add_produto(db: AsyncSession,
                      produto: schemas.ProdutoCreate,
                      usuario_id: int, tenant_id: int
                      ):
    """onde adiciona o produto no site"""
    db.add(models.Produto(
        tenant_id=produto.tenant_id,
        usuario_id=produto.usuario_id,
        nome_produto=produto.nome_produto,
        preco=produto.preco,
        descricao=produto.descricao,
        link_video=produto.link_video,
        link_checkout=produto.link_checkout,
        palavra_gatilho=produto.palavra_gatilho
    ))

    await db.commit()
    return "Produto adicionado com sucesso"


async def listar_produto(db: AsyncSession,
                         listar: schemas.ProdutoCreate,
                         usuario_id: int,
                         tenant_id: int):
    """aqui lista os produtos no site"""
    query = select(models.Produtos).where(
        models.Produtos.usuario_id == usuario_id,
        models.Produtos.tenant_id == tenant_id
    )

    resultado = await db.execute(query)
    return resultado.scalars().all()


async def excluir_produto(db: AsyncSession,
                          produto_id: int,
                          usuario_id: int,
                          tenant_id: int):
    """aqui e onde excluir os produtos do site"""
    query = delete(models.Produtos).where(
        models.Produtos.produto_id == produto_id,
        models.Produtos.usuario_id == usuario_id,
        models.Produtos.tenant_id == tenant_id
    )

    await db.execute(query)
    await db.commit()
    return "Produto excluido com sucesso"


async def editar_produto(db: AsyncSession,
                         produto_id: int,
                         produto: schemas.ProdutoCreate,
                         usuario_id: int,
                         tenant_id: int):
    # def para editar produtos cadastrados no site
    dados_atualizar = produto.model_dump(exclude_unset=True)

    # 1. Monta a query com o cerco de seguranu00e7a e o values automu00e1tico
    query = (
        update(models.Produtos)
        .where(
            models.Produtos.produto_id == produto_id,
            models.Produtos.usuario_id == usuario_id,
            models.Produtos.tenant_id == tenant_id
        )
        .values(**dados_atualizar)  # <--- Injeta tudo automaticamente aqui!
    )

    # 2. Executa a au00e7u00e3o no banco de dados
    await db.execute(query)
    await db.commit()


async def salvar_ou_editar_config_robo(db: AsyncSession,
                                       config_dados: schemas.ConfigRoboCreate,
                                       usuario_id: int,
                                       tenant_id: int):
    # 1. O 'model_dump()' rasga a caixa do site e transforma em dicionu00e1rio do Python
    dados = config_dados.model_dump(exclude_unset=True)

    # 2. SELECT: O sistema vai lu00e1 na lacuna do banco ver se ju00e1 existe esse tenant_id
    query_busca = select(models.ConfigRobo).where(
        models.ConfigRobo.tenant_id == tenant_id)
    resultado = await db.execute(query_busca)
    config_existente = resultado.scalar_one_or_none()

    # 3. A Lu00d3GICA REVERSu00cdVEL (GRAVAR OU EDITAR):
    if config_existente is None:
        # SE Nu00c3O EXISTE: u00c9 a primeira vez do cara. Pega o prompt/tempos e roda o db.add() para GRAVAR
        nova_config = models.ConfigRobo(
            **dados,
            usuario_id=usuario_id,
            tenant_id=tenant_id
        )
        db.add(nova_config)  # Adiciona na lacuna do banco
    else:
        # SE Ju00c1 EXISTE: O cara estu00e1 editando ou melhorando o prompt. Roda o update() para EDITAR
        query_update = (
            update(models.ConfigRobo)
            .where(
                models.ConfigRobo.tenant_id == tenant_id,
                models.ConfigRobo.usuario_id == usuario_id
            )
            .values(**dados)  # Atualiza as lacunas com o prompt/tempos novos
        )
        await db.execute(query_update)

    # 4. Tranca o cadeado e salva de verdade no banco
    await db.commit()
    return {"status": "Configurau00e7u00e3o do robu00f4 salva/atualizada"}
