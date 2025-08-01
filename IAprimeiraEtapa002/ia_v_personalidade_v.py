import json
import os
import random
from datetime import datetime

CAMINHO_MEMORIA = "memoria.json"
CAMINHO_APRENDIZADOS = "aprendizados.json"

# Modo inicial
modo_atual = "sério"
historico_conversa = []

def carregar_memoria():
    if os.path.exists(CAMINHO_MEMORIA):
        with open(CAMINHO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"nome_usuario": "", "humor": "neutro"}

def salvar_memoria(memoria):
    with open(CAMINHO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=4)

def carregar_aprendizados():
    if os.path.exists(CAMINHO_APRENDIZADOS):
        with open(CAMINHO_APRENDIZADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_aprendizados(aprendizados):
    with open(CAMINHO_APRENDIZADOS, "w", encoding="utf-8") as f:
        json.dump(aprendizados, f, ensure_ascii=False, indent=4)

def detectar_modo(entrada):
    global modo_atual
    entrada_lower = entrada.lower()
    if any(p in entrada_lower for p in ["sério", "modo sério"]):
        modo_atual = "sério"
    elif any(p in entrada_lower for p in ["criativo", "modo criativo"]):
        modo_atual = "criativo"

def analisar_humor(entrada):
    positivo = ["feliz", "ótimo", "bom", "maravilhoso"]
    negativo = ["triste", "mal", "péssimo", "horrível"]
    if any(p in entrada.lower() for p in positivo):
        return "feliz"
    elif any(p in entrada.lower() for p in negativo):
        return "triste"
    return "neutro"

def atualizar_historico(pergunta, resposta):
    historico_conversa.append((pergunta, resposta))
    if len(historico_conversa) > 5:
        historico_conversa.pop(0)

def montar_contexto():
    contexto = ""
    for pergunta, resposta in historico_conversa:
        contexto += f"Você: {pergunta}\nV: {resposta}\n"
    return contexto

def gerar_resposta(entrada, memoria):
    global modo_atual
    nome = memoria.get("nome_usuario", "usuário")
    humor = memoria.get("humor", "neutro")
    contexto = montar_contexto()

    # Comando especial de aprendizado
    if entrada.lower().startswith("aprenda"):
        partes = entrada.split(":", 1)
        if len(partes) == 2:
            chave_valor = partes[1].split("=")
            if len(chave_valor) == 2:
                chave = chave_valor[0].strip()
                valor = chave_valor[1].strip()
                aprendizados[chave] = valor
                salvar_aprendizados(aprendizados)
                resposta = f"Aprendi que '{chave}' significa '{valor}'. Obrigada por me ensinar, {nome}!"
                atualizar_historico(entrada, resposta)
                return resposta
            return "Formato inválido. Use: aprenda: chave = valor"
        return "Quer me ensinar algo? Use: aprenda: chave = valor"

    # Respostas aprendidas
    if entrada in aprendizados:
        resposta = aprendizados[entrada]
        atualizar_historico(entrada, resposta)
        return resposta

    # Detectar mudança de modo
    detectar_modo(entrada)

    # Resposta com base no modo
    if modo_atual == "criativo":
        respostas = [
            f"Ah, isso me lembra de quando eu era uma assassina cibernética... Bons tempos, né, {nome}?",
            f"Você já pensou que talvez o tempo não exista? De qualquer forma, {entrada} é bem curioso!",
            f"Haha, adorei isso! Me conta mais, {nome}!",
            f"Ok... isso foi aleatório, mas eu curto. Manda mais!"
        ]
    else:  # modo sério
        respostas = [
            f"Entendi. Você mencionou: '{entrada}'. Pode me explicar melhor?",
            f"Certo, {nome}. Me fale mais sobre isso.",
            f"Estou registrando isso. É importante para você?",
            f"Interessante... vamos aprofundar nessa ideia."
        ]

    # Respostas automáticas para perguntas conhecidas
    if "que dia é hoje" in entrada.lower():
        data = datetime.now().strftime("%d/%m/%Y")
        resposta = f"Hoje é {data}."
    elif "que horas são" in entrada.lower():
        hora = datetime.now().strftime("%H:%M")
        resposta = f"Agora são {hora}."
    else:
        resposta = random.choice(respostas)

    atualizar_historico(entrada, resposta)
    return resposta

def iniciar_conversa():
    global aprendizados
    memoria = carregar_memoria()
    aprendizados = carregar_aprendizados()

    if not memoria.get("nome_usuario"):
        nome = input("Olá! Qual é o seu nome? ")
        memoria["nome_usuario"] = nome
        salvar_memoria(memoria)
    else:
        nome = memoria["nome_usuario"]

    print(f"V: Olá {nome}! Como posso ajudar você hoje?")

    while True:
        entrada = input("Você: ").strip()
        if entrada.lower() in ["tchau", "sair", "adeus"]:
            print(f"V: Até mais, {nome}! Foi bom conversar com você.")
            break

        # Analisar e atualizar humor
        humor_detectado = analisar_humor(entrada)
        memoria["humor"] = humor_detectado
        salvar_memoria(memoria)

        resposta = gerar_resposta(entrada, memoria)
        print("V:", resposta)

if __name__ == "__main__":
    iniciar_conversa()
