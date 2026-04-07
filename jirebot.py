# O esforço vence o talento quando o talento é preguiçoso para aprender.
# Projeto: JireBot - Desenvolvido por Jeymison Hiago
import time
import random
import json
import os

#área de cadastro
def cadastro():
    print("(>>>entrando na área de cadastro)")
    nome_vendedor = input("Digite seu nome")
    print("Nome salvo com sucesso ✅")
    nome_produto = input("Nome do produto")
    print("Produto salvo com sucesso ✅")
    valor_produto = input("Digite o valor")
    print("Preço salvo com sucesso ✅")
    descricao_produto = input("Coloque a descriçáo do produto")
    print("Descriçáo salvo com sucesso ✅")
    link_video = input("link do video do produto")
    print("Link salvo com sucesso ✅")
    link_checkout = input("Link da página de venda")
    print("Link salvo com sucesso ✅")
    texto_acao = input("Coloque a mensagem de automatica do whatsapp")
    print("Mensagem salvo com sucesso ✅")

    #aqui fica o dicionário de dados onde
    # as informações acima são recebidas e tratadas
    dados=[
           {
            "vendedor" : nome_vendedor,
            "produto" : nome_produto,
            "valor" : valor_produto,
            "descricao" : descricao_produto,
            "video" : link_video,
            "checkout" : link_checkout,
            "gatilho" : texto_acao
          }    
        ]
    #aqui é a área que salva as informações de cima
    with open("cadastro.json", "w", encoding="utf-8") as arquivo:
         json.dump(dados, arquivo, indent = 4, ensure_ascii=False )


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
                elif("Ok sem problema")
                    break
                pergunta3=input("quando voltar de assistir o vídeo\n digite ok,voltei ou oi").lowe()
                if "oi" in pergunta3 or "voltei" in pergunta3 or "oi" in pergunta3:
                    time.sleep(random.uniform(3,6))
                    print("Que bom que você voltou!")     
                
        elif "como usar" in pergunta:
                time.sleep(random.uniform(3,6))
                print("\nuso oral são duas capsulas por dia uma ápos a primeira refeição e outra ápos o jantar")
        else:print("sem problema")     
      else:
          print("\nSem problemas! Qualquer coisa estou por aqui para ajudar.")
          print("(>>>saida da def)")
          

#área de verificação.de cadastro
NOME_ARQUIVO ="cadastro.json" #isso e uma constante

def verificar_cadastro():
     print("(>>> verificando)")
     try:
         with open(NOME_ARQUIVO, "r", encoding="utf-8") as f: 
              dados = json.load(f)
              time.sleep(random.uniform(3,5))
              print(f"Olá {dados[0] ["vendedor"]}! \no Robô esta ativo")
              time.sleep(random.uniform(5,6))
              return dados
              time.sleep(random.uniform(3,5))
     except FileNotFoundError:       
            time.sleep(random.uniform(3,5))     
            print(f"cadastro não encontrado no sistem \n você será direcionado(a) para\n á área de cadastro")           
            time.sleep(random.uniform(5,6))
            return cadastro()
            time.sleep(random.uniform(3,5))
verificar_cadastro()
funil_de_vendas()
