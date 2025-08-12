import json
import os
import random
from datetime import datetime, timezone
import unicodedata

CAMINHO_MEMORIA = "memoria.json"
CAMINHO_APRENDIZADOS = "aprendizados.json"

def carregar_json(caminho):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        if caminho == CAMINHO_MEMORIA:
            return {
                "nome_usuario": "",
                "preferencias": [],
                "personalidade": "gentil",
                "historico": []
            }
        else:
            return {}

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

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
    # Verifica se está perguntando especificamente pela data ou dia de hoje
    if ( ("dia" in entrada_sem_acentos and "hoje" in entrada_sem_acentos) or
         ("qual" in entrada_sem_acentos and ("data" in entrada_sem_acentos or "dia" in entrada_sem_acentos)) ):
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
    personalidade = memoria.get("personalidade", "gentil")
    emocao_usuario = detectar_emocao(entrada)

    resposta_pref = atualizar_preferencias(entrada, memoria)
    if resposta_pref:
        return resposta_pref

    # Primeiro responder data
    resposta_data = responder_data(entrada)
    if resposta_data:
        return resposta_data

    respostas = aprendizados.get("respostas", {})
    resposta_raw = respostas.get(entrada_lower)

    if resposta_raw:
        if isinstance(resposta_raw, dict):
            texto = resposta_raw.get("texto", "")
            emocao_resposta = resposta_raw.get("emocao", "neutra")
        else:
            texto = resposta_raw
            emocao_resposta = "neutra"
    else:
        respostas_padrao = [
            "Desculpa, ainda não sei responder isso.",
            "Pode me ensinar a responder essa pergunta?",
            "Interessante, me fale mais!",
            "Não entendi muito bem, pode explicar?"
        ]
        texto = random.choice(respostas_padrao)
        emocao_resposta = "neutra"

    # Modula resposta com base na emoção do usuário e da resposta aprendida
    if emocao_resposta == "triste" or emocao_usuario == "triste":
        texto = "Poxa, sinto muito que você esteja assim. " + texto
    elif emocao_resposta == "feliz" or emocao_usuario == "feliz":
        texto = "Que bom ouvir isso! " + texto
    elif emocao_resposta == "irritado" or emocao_usuario == "irritado":
        texto = "Calma, vamos tentar resolver isso juntos. " + texto

    if personalidade == "gentil":
        texto = texto + " Estou aqui para ajudar!"
    elif personalidade == "animada":
        texto = "😄 " + texto + " Que legal!"
    elif personalidade == "curiosa":
        texto = "Hmm, que curioso... " + texto

    return texto


# Dicionário de perguntas por tema preferido
perguntas_por_tema = {
    "futebol": [
        "Você assistiu ao jogo ontem?",
        "Qual seu time favorito?",
        "Quem você acha que vai ganhar o campeonato?"
    ],
    "cinema": [
        "Qual foi o último filme que você viu?",
        "Você prefere cinema ou séries?",
        "Tem algum filme que marcou sua vida?"
    ],
    "tecnologia": [
        "Qual gadget novo você acha mais interessante?",
        "Você gosta de acompanhar notícias de tecnologia?",
        "Tem alguma tecnologia que você acha que vai revolucionar o futuro?"
    ],
    # Adicione mais temas conforme quiser
}

def iniciar_conversa():
    memoria = carregar_json(CAMINHO_MEMORIA)
    aprendizados = carregar_json(CAMINHO_APRENDIZADOS)

    if not memoria.get("nome_usuario"):
        memoria["nome_usuario"] = input("Qual o seu nome? ").strip()
        salvar_json(CAMINHO_MEMORIA, memoria)

    nome = memoria["nome_usuario"]
    print(f"V: Olá {nome}! Como posso ajudar você hoje?")

    respostas_padrao = [
        "Desculpa, ainda não sei responder isso.",
        "Pode me ensinar a responder essa pergunta?",
        "Interessante, me fale mais!",
        "Não entendi muito bem, pode explicar?"
    ]

    contador_mensagens = 0  # Contador para interações

    while True:
        # Pergunta automática a cada 5 mensagens
        if contador_mensagens > 0 and contador_mensagens % 5 == 0:
            prefs = memoria.get("preferencias", [])
            if prefs:
                tema = random.choice(prefs)
                perguntas = perguntas_por_tema.get(tema.lower())
                if perguntas:
                    pergunta_auto = random.choice(perguntas)
                    print(f"V (pergunta automática sobre {tema}): {pergunta_auto}")

        entrada = input("Você: ").strip()
        if entrada.lower() in ["tchau", "sair", "adeus", "exit"]:
            print(f"V: Até mais, {nome}! Foi bom conversar com você.")
            break

        if entrada.lower().startswith("aprenda:"):
            aprendizado = entrada[len("aprenda:"):].strip()
            emocao_aprendida = detectar_emocao(entrada)
            if aprendizado:
                if "|" in aprendizado:
                    chave, valor = aprendizado.split("|", 1)
                    chave = chave.strip()
                    valor = valor.strip()
                    aprendizados.setdefault("respostas", {})[chave.lower()] = {
                        "texto": valor,
                        "emocao": emocao_aprendida
                    }
                    salvar_json(CAMINHO_APRENDIZADOS, aprendizados)
                    print("V: Aprendi isso, obrigado!")
                else:
                    print("V: Para ensinar, use o formato: aprenda: pergunta | resposta")
            else:
                print("V: O que você quer que eu aprenda? Use: aprenda: pergunta | resposta")
            continue

        resposta = gerar_resposta(entrada, aprendizados, memoria)
        print("V:", resposta)

        if not entrada.lower().startswith("aprenda:") and any(
            resposta.startswith(padrao) for padrao in respostas_padrao
        ):
            feedback = input("Essa resposta está boa? (s/n): ").strip().lower()
            if feedback == "n":
                nova_resposta = input("Como você gostaria que eu respondesse? ").strip()
                emocao_feedback = detectar_emocao(nova_resposta)
                aprendizados.setdefault("respostas", {})[entrada.lower()] = {
                    "texto": nova_resposta,
                    "emocao": emocao_feedback
                }
                salvar_json(CAMINHO_APRENDIZADOS, aprendizados)
                print("V: Obrigada! Vou lembrar disso.")

        memoria.setdefault("historico", []).append({
            "pergunta": entrada,
            "resposta": resposta,
            "data": datetime.now(timezone.utc).isoformat()
        })
        salvar_json(CAMINHO_MEMORIA, memoria)

        contador_mensagens += 1

if __name__ == "__main__":
    iniciar_conversa()
