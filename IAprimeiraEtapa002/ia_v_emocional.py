import json
import os
import random
from datetime import datetime
import unicodedata

CAMINHO_MEMORIA = "memoria.json"
CAMINHO_APRENDIZADOS = "aprendizados.json"

def carregar_memoria():
    if os.path.exists(CAMINHO_MEMORIA):
        with open(CAMINHO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "nome_usuario": "",
            "preferencias": [],
            "personalidade": "gentil",
            "historico": []
        }

def salvar_memoria(memoria):
    with open(CAMINHO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=4)

def carregar_aprendizados():
    if os.path.exists(CAMINHO_APRENDIZADOS):
        with open(CAMINHO_APRENDIZADOS, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, dict):
                return dados
            else:
                print("Aviso: Arquivo de aprendizados não está no formato correto. Reiniciando aprendizados.")
                return {}
    else:
        return {}

def salvar_aprendizados(aprendizados):
    with open(CAMINHO_APRENDIZADOS, "w", encoding="utf-8") as f:
        json.dump(aprendizados, f, ensure_ascii=False, indent=4)

def detectar_emocao(texto):
    texto = texto.lower()
    if any(p in texto for p in ["triste", "chateado", "deprimido", "infeliz", "mal"]):
        return "triste"
    elif any(p in texto for p in ["feliz", "alegre", "animado", "contente", "bom"]):
        return "feliz"
    elif any(p in texto for p in ["raiva", "irritado", "bravo", "chateado"]):
        return "irritado"
    else:
        return "neutra"

def atualizar_preferencias(entrada, memoria):
    entrada_lower = entrada.lower()
    prefs = memoria.get("preferencias", [])
    if "gosto de" in entrada_lower:
        item = entrada_lower.split("gosto de")[-1].strip()
        if item and item not in prefs:
            prefs.append(item)
            memoria["preferencias"] = prefs
            return f"Que legal saber que você gosta de {item}!"
    elif "não gosto de" in entrada_lower:
        item = entrada_lower.split("não gosto de")[-1].strip()
        if item and item not in prefs:
            prefs.append(f"não {item}")
            memoria["preferencias"] = prefs
            return f"Entendi, vou lembrar que você não gosta de {item}."
    return None

def remover_acentos(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', txt)
                   if unicodedata.category(c) != 'Mn').lower()

def responder_data(entrada):
    entrada_sem_acentos = remover_acentos(entrada)
    # Se contém "dia" e "hoje" ou palavras tipo "qual" e "data", responde data
    if ( "dia" in entrada_sem_acentos and "hoje" in entrada_sem_acentos ) or \
       ("qual" in entrada_sem_acentos or "data" in entrada_sem_acentos):
        dias_semana = [
            "segunda-feira", "terça-feira", "quarta-feira",
            "quinta-feira", "sexta-feira", "sábado", "domingo"
        ]
        hoje = datetime.now()
        dia_semana = dias_semana[hoje.weekday()]
        return f"Hoje é {dia_semana}, {hoje.strftime('%d/%m/%Y')}."
    return None

def gerar_resposta(entrada, aprendizados, memoria):
    entrada_lower = entrada.lower()
    nome = memoria.get("nome_usuario", "")
    personalidade = memoria.get("personalidade", "gentil")
    emocao = detectar_emocao(entrada)

    resposta_pref = atualizar_preferencias(entrada, memoria)
    if resposta_pref:
        return resposta_pref

    resposta_data = responder_data(entrada)
    if resposta_data:
        return resposta_data

    # Busca resposta aprendida
    for chave in aprendizados:
        if chave.lower() == entrada_lower:
            resposta = aprendizados[chave]
            break
    else:
        respostas_padrao = [
            "Desculpa, ainda não sei responder isso.",
            "Pode me ensinar a responder essa pergunta?",
            "Interessante, me fale mais!",
            "Não entendi muito bem, pode explicar?"
        ]
        resposta = random.choice(respostas_padrao)

    if emocao == "triste":
        resposta = "Poxa, sinto muito que você esteja assim. " + resposta
    elif emocao == "feliz":
        resposta = "Que bom ouvir isso! " + resposta
    elif emocao == "irritado":
        resposta = "Calma, vamos tentar resolver isso juntos. " + resposta

    if personalidade == "gentil":
        resposta = resposta + " Estou aqui para ajudar!"
    elif personalidade == "animada":
        resposta = "😄 " + resposta + " Que legal!"
    elif personalidade == "curiosa":
        resposta = "Hmm, que curioso... " + resposta

    return resposta

def iniciar_conversa():
    memoria = carregar_memoria()
    aprendizados = carregar_aprendizados()

    if not memoria.get("nome_usuario"):
        memoria["nome_usuario"] = input("Qual o seu nome? ").strip()
        salvar_memoria(memoria)

    nome = memoria["nome_usuario"]
    print(f"V: Olá {nome}! Como posso ajudar você hoje?")

    while True:
        entrada = input("Você: ").strip()
        if entrada.lower() in ["tchau", "sair", "adeus"]:
            print(f"V: Até mais, {nome}! Foi bom conversar com você.")
            break

        if entrada.lower().startswith("aprenda:"):
            aprendizado = entrada[len("aprenda:"):].strip()
            if aprendizado:
                if "|" in aprendizado:
                    chave, valor = aprendizado.split("|", 1)
                    chave = chave.strip()
                    valor = valor.strip()
                    aprendizados[chave] = valor
                    salvar_aprendizados(aprendizados)
                    print("V: Aprendi isso, obrigado!")
                else:
                    print("V: Para ensinar, use o formato: aprenda: pergunta | resposta")
            else:
                print("V: O que você quer que eu aprenda? Use: aprenda: pergunta | resposta")
            continue

        resposta = gerar_resposta(entrada, aprendizados, memoria)
        print("V:", resposta)

        feedback = input("Essa resposta está boa? (s/n): ").strip().lower()
        if feedback == "n":
            nova_resposta = input("Como você gostaria que eu respondesse? ").strip()
            aprendizados[entrada] = nova_resposta
            salvar_aprendizados(aprendizados)
            print("V: Obrigada! Vou lembrar disso.")

        memoria.setdefault("historico", []).append({
            "pergunta": entrada,
            "resposta": resposta,
            "data": datetime.now().isoformat()
        })
        salvar_memoria(memoria)

if __name__ == "__main__":
    iniciar_conversa()
