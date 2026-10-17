import time
import random



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
