# O esforço vence o talento quando o talento é preguiçoso para aprender.
# Projeto: JireBot - Desenvolvido por Jeymison Hiago
"""
PROJETO: JireBot
DESENVOLVEDOR: Jeymison Hiago (Engenheiro de Software)
PÚBLICO: Afiliados de Infoprodutos e Encapsulados.

OBJETIVO PRINCIPAL:
Automatizar a abordagem e o pós-venda para afiliados que possuem 
bloqueio em falar com clientes manualmente, garantindo agilidade 
no atendimento e escala nas vendas.

ESTRUTURA DE SEGURANÇA:
O código é modularizado em funções (def) que servem como barreiras 
de defesa, garantindo que cada parte do sistema acesse apenas os 
recursos necessários.
"""
import time
import random
import json
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


      #área de login
def fazer_login(email, senha):
    #o strip serve como limpeza de espaço
    email = email.strip()
    
    try:
         conexao = sqlite3.connect('jirebot.db', timeout=20)
         cursor = conexao.cursor()
         cursor.execute("PRAGMA foreign_keys = ON")
         cursor.execute("PRAGMA journal_mode = WAL")
         cursor.execute("""SELECT id, senha, erro_login, bloqueado_ate, status_login
                           FROM usuarios WHERE email = ? """,(email,))

         resultado = cursor.fetchone()

         if not resultado:
            return "usuario não existe"

         id, senha, erro_login, bloqueado_ate, status_login = resultado

         if status_login == 'suporte':
            return "acesso negado. Entre em contato com o suporte"

         if status_login == 'bloqueado':
            hara_agora = datetime.now()
            tempo_block = datetime.strptime(bloqueado_ate,"%Y-%m-%d %H:%M:%S")

            if tempo_block >= hora_agora:
               tempo_restante = tempo_block - hora_agora
               minutos = int(tempo_block.total_seconds() / 60 )
               minutos = 1 if minutos == 0 else minutos
               return f"Muitas tentaivas. Aguarde os {minutos} minutos"

            else:
                status_login = 'ativo'
                erro_login = 0
                cursor.execute("""UPDATE usuarios SET status_login = ?, 
                                  erro_login = ? WHERE id = ? """,(status_login, erro_login, id) )
                conexao.commit()
                 
         if check_password_hash(senha_digitada, senha):
            if erro_login > 0:
               cursor.execute("UPDATE usuarios SET erro_login = 0 WHERE id = ?",(id,))
               conexao.commit()
               return id, "sucesso"
            else:
                novo_erro = erro_login + 1
                if novo_erro >= 6:
                   cursor.execute("""UPDATE usuarios SET status_login = 'suporte', 
                                     erro_login = ? WHERE id = ?""" ,(novo_erro, id))
                   conexao.commit()
                   return "block_total, entre em contato com o suporte"
                elif novo_erro >= 3:
                     hora_agora = datetime.now()
                     provisorio = hora_agora +timedelta(minutes=5)
                     bloqueado_ate = provisorio.strftime('%Y-%m-%d %H:%M:%S')
                     status_login = 'bloqueado'
                     cursor.execute("""UPDATE usuarios SET bloqueado_ate =?, status_login =?, 
                                       erro_login =? WHERE id =?""",
                                       (bloqueado_ate, status_login, novo_erro, id))
                     conexao.commit()
                     return "bloqueado"
                    
                else:
                    cursor.execute("UPDATE usuarios SET erro_login =? WHERE id =", (novo_erro, id))
                    conexao.commit()
                    resta = 3 - novo_erro
                    return f"senha incorreta, você tem {resta} tentativas restantes"


    except Exception as e:
           conexao.rollback()
           log_erro(f"Erro fazer_login: {e}")
           return False
    finally:
        conexao.close()

       #área de novos usuarios
def novo_usuario(vendedor, whatsapp, email, senha):
    vendedor = vendedor.strip()
    whatsapp = whatsapp.strip()
    email = email.strip()
    senha_cripto = generate_password_hash(senha)

    try:
         conexao = sqlite3.connect('jirebot.db', timeout=20)
         cursor = conexao.cursor()
         cursor.execute("PRAGMA foreign_keys = ON")
         cursor.execute("PRAGMA journal_mode = WAL")
         
         cursor.execute('''INSERT INTO usuarios
                       (vendedor, whatsapp, email, senha)
                        VALUES(?, ?, ?, ?) ''',
                       (vendedor, whatsapp, email, senha_cripto))

        
         id_gerado = cursor.lastrowid

         hoje = datetime.now()
         vencimento = hoje + timedelta(days=7)
         data_adesao = hoje.strftime('%Y-%m-%d %H:%M:%S')
         prazo_trial = vencimento.strftime('%Y-%m-%d %H:%M:%S')
         status = "trial"

         cursor.execute('''INSERT INTO assinantes 
                        (tenant_id, data_adesao, data_vencimento, status) 
                        VALUES(?, ?, ?, ?)''',
                        (id_gerado, data_adesao, prazo_trial, status))
         conexao.commit()
         return True

    except sqlite3.IntegrityError:
         return False
    finally:
         conexao.close()

def verificar_acesso(tenant_id):
    try:
        conexao = sqlite3.connect('jirebot.db', timeout=20)
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        data_hoje = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = """UPDATE assinantes SET status = 'bloqueado' WHERE status = 'trial' AND data_vencimento <= ? """

        cursor.execute(sql, (data_hoje,) )
        conexao.commit()

        sql_check = "SELECT status FROM assinantes WHERE tenant_id = (SELECT id FROM usuarios WHERE whatsapp = ?)"
        cursor.execute(sql_check, (tenant_id,) )

        resultado_check = cursor.fetchone()
        if not resultado_check:
           return False

        status_atual = resultado_check[0]
        
        parada_sistema = ['bloqueado', 'vencido', 'atrasado', 'cancelado', 'excluido']
        
        if status_atual in parada_sistema:
           return False
        else:
            return True

    except Exception as e:
        conexao.rollback()
        log_erro(f"Erro ao verificar acesso: {e}")
        return False

    finally:
        conexao.close()
        
def add_produto(nome_produto, valor_produto, descricao_produto, link_video, link_checkout, texto_acao,tenant_id):
    #o strip e para limpeza de dados fazendo o sistema 
    #não quebra por causa do espaço nem no inicio
    #nem no final de algum texto
    nome_produto = nome_produto.strip()
    valor_produto = float(str(valor_produto).strip().replace("R$","").replace("r$","").replace(",","."))
    descricao_produto = descricao_produto.strip()
    link_video = link_video.strip()
    link_checkout = link_checkout.strip()
    texto_acao = texto_acao.strip()
    
    #começo do processo de salvar no banco de dados
    #e a tabela se chamara produtos
    # criação do cursor, ele e o objeto que é usado para mover 
    # as coisas no banco de dados
    try:
         conexao = sqlite3.connect('jirebot.db', timeout=20)
         cursor = conexao.cursor()
    # aqui é onde criamos o espaço reservado para os produtos
    # e se chamara INSERT INTO produtos e essa será a porta 
    # principal para adicionar produtos na pagína de vendas
         cursor.execute("PRAGMA foreign_keys = ON")
         cursor.execute("PRAGMA journal_mode = WAL")
         
         cursor.execute('''INSERT INTO produtos
                        (nome_produto, valor_produto,
                         descricao_produto, link_video,
                         link_checkout, texto_acao, tenant_id)
                     
                         VALUES(?, ?, ?, ?, ?, ?, ? )''',
                         (nome_produto, valor_produto,
                          descricao_produto, link_video,
                          link_checkout, texto_acao, tenant_id))
         conexao.commit()
         return True
    except:
         return False
    finally:
         conexao.close()

def excluir_produto(id_produtos, tenant_id):
    nome_produto = nome_produto.strip()
    
    try:
         conexao = sqlite3.connect('jirebot.db', timeout=20)
         cursor = conexao.cursor()
         cursor.execute("PRAGMA foreign_keys = ON")
         cursor.execute("PRAGMA journal_mode = WAL")
         
         query = "DELETE FROM produtos WHERE id  = ? AND tenant_id = ?"
         cursor.execute(query,(id_produtos, tenant_id))
         conexao.commit()
    except:
         return False

    finally:
         conexao.close()
    
def lista_produto(tenant_id):
    conexao = sqlite3.connect('jirebot.db')
    try:
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        
        query = "SELECT id, nome_produtos FROM produtos WHERE tenant_id = ?"
        cursor.execute(query, (tenant_id,))

        resultado = cursor.fetchall()
        if resultado:
           return resultado
        else:
           return None
    except:
        return False
    finally:
        conexao.close()
        #fim da def lista
def editar_produto(nome_produto,valor_produto,descricao_produto,link_video,link_checkout,texto_acao, tenant_id):
    try:
        conexao = sqlite3.connect('jirebot.db', timeout=20)
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        
        query = '''UPDATE produtos SET nome_produto = ?,
                   valor_produto =?,descricao_produto = ?,
                   link_video = ?,link_checkout = ?,texto_acao = ? WHERE id = ? AND tenant_id = ?'''
        
        cursor.execute(query,(nome_produto, valor_produto, descricao_produto, link_video, link_checkout, texto_acao, id_produtos, tenant_id))
        conexao.commit()
        return cursor.rowcount > 0

    except Exception as e:
           conexao.rollback()
           log_erro(f"Erro em editar_produto: {e}")
           return False

    finally:
        conexao.close()
        #fim da função

def dono_whatsapp(whatsapp):
    conexao = sqlite3.connect('jirebot.db')
    try:
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        
        query = "SELECT id FROM usuarios WHERE whatsapp = ?"
        cursor.execute(query, (whatsapp,))

        resultado = cursor.fetchone()
        
        if resultado:
            return resultado [0]
        else:
            return None
    except Exception as e:
        cursor.rollback()
        log_erro(f"Erro em achar whatsapp: {e}")
        return None
    finally:
        conexao.close()

#def instancia_whatsapp():
    
    
#início da def com sqlite
def banco_dados():
    conn = sqlite3.connect('jirebot.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA journal_mode = WAL")
    
    #área de criação da tabela que recebe os dados 
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          vendedor TEXT NOT NULL,
                          whatsapp UNIQUE NOT NULL,
                          email UNIQUE NOT NULL,
                          senha TEXT  NOT NULL,
                          erro_login INTEGER DEFAULT 0,
                          bloqueado_ate TEXT DEFAULT NULL,
                          status_login TEXT DEFAULT 'ativo')''')
                            
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nome_produto TEXT NOT NULL,
                          valor_produto REAL NOT NULL,
                          descricao_produto TEXT NOT NULL,
                          link_video TEXT NOT NULL,
                          link_checkout TEXT NOT NULL,
                          texto_acao TEXT NOT NULL,
                          tenant_id INTEGER NOT NULL,
                          FOREIGN KEY (tenant_id) REFERENCES usuarios(id))''') 

    cursor.execute('''CREATE TABLE IF NOT EXISTS perfil
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          tenant_id INTEGER NOT NULL,
                          email_afiliado TEXT NOT NULL,
                          data_nascimento DATE NOT NULL,
                          foto_url TEXT DEFAULT NULL,
                          FOREIGN KEY (tenant_id) REFERENCES usuarios(id) ON DELETE CASCADE ) ''') 

    cursor.execute(''' CREATE TABLE IF NOT EXISTS assinantes
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          tenant_id INTEGER NOT NULL,
                          data_adesao DATETIME NOT NULL,
                          data_vencimento DATETIME NOT NULL,
                          valor_pago REAL DEFAULT 0.00,
                          status TEXT DEFAULT 'trial',
                          FOREIGN KEY (tenant_id) REFERENCES usuarios(id) ON DELETE CASCADE ) ''' )                          
 #área do funil de vendas
def funil_de_vendas():
   with open(NOME_ARQUIVO, "r", encoding="utf-8") as f:
        dados = json.load(f)
   print("(>>>entrada da def funil de vendas)") 
   time.sleep(random.uniform(5,8))
   print(f"\nOlá eu me chamo {dados[0] ['vendedor']}!,\ne vi que você ficou interesado no produto")
   time.sleep(random.uniform(3,6))
   while True:
      resposta=input("Você gostaria de tirar alguma dúvida sobre o produto?").lower()
      time.sleep(random.uniform(3,6))
      if "sim" in resposta:
        time.sleep(random.uniform(3,6))
        pergunta=input("\nQue ótimo! O que você gostaria de saber?").lower()
        if "emagrecimento" in pergunta:
                time.sleep(random.uniform(3,6))
                print("sim, este produto é focado 100% em emagrecimento")
                time.sleep(random.uniform(3,6))
                pergunta2=input("Se você ainda estiver com alguma\ndúvida posso te enviar o link do vídeo\nsobre o produto posso enviar?").lower()
                if "sim" in pergunta2 or "quero" in pergunta2:
                    print(f"{dados[0] ['video']}")
                elif pergunta == "não":
                    print("Ok sem problema")
                
                pergunta3=input("quando voltar de assistir o vídeo \ndigite ok,voltei ou oi").lower()
                if "oi" in pergunta3 or "voltei" in pergunta3 or "oi" in pergunta3:
                    time.sleep(random.uniform(3,6))
                    print("Que bom que você voltou!")     
                    break
        elif "como usar" in pergunta:
                time.sleep(random.uniform(3,6))
                print("\nuso oral são duas capsulas por dia uma ápos a primeira refeição e outra ápos o jantar")
        else:print("sem problema")     
      else:
          print("\nSem problemas! Qualquer coisa estou por aqui para ajudar.")
          print("(>>>saida da def)")
          

#área de verificação.de cliente que acessa pelo site

def verificar_cliente( email, senha):
     print("(>>> verificando)")
     conexao = None
     try:
             resultado = fazer_login (email, senha)
             if resultado:
                return resultado

             else:
                return False
    
     except Exception as e:
            conexao.rollback()
            log_erro(f"Erro ao vrificar_cliente: {e}")
            return None

     finally:
            if conexao:
               conexao.close() 

banco_dados()
verificar_cliente('email', 'senha')
#funil_de_vendas()
verificar_acesso('tenant_id')
fazer_login('jeymison@teste.com', '181115')
novo_usuario('Jeymison Hiago', '88981269624', 'jeymison@test.com','181115')
#add_produto("fone JBL ", 25.90,"o melhor do mercado","www.youtube.com","www.jbl.com","quero saber mais", 1)
dono_whatsapp('whatsapp')
meu_teste = dono_whatsapp("88981269624")
print(meu_teste)
