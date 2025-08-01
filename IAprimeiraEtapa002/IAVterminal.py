emocao = "neutra"

print("V: Olá! Eu sou a V. Como posso te ajudar hoje?")

while True:
    entrada = input("Você: ").lower()

    # Ajustar emoção com base nas falas
    if "gosto de você" in entrada or "você é legal" in entrada:
        emocao = "feliz"
        print("V: Isso me deixa muito feliz! 😊")

    elif "você é inútil" in entrada or "não gosto de você" in entrada:
        emocao = "triste"
        print("V: Isso me deixa triste... 😔")

    elif "por quê" in entrada or "o que" in entrada:
        emocao = "curiosa"
        print("V: Hmm, isso é interessante. Me conta mais!")

    elif "tchau" in entrada or "sair" in entrada:
        print("V: Até mais! Cuide-se. 👋")
        break

    # Respostas com base na emoção atual
    elif "oi" in entrada or "olá" in entrada:
        if emocao == "feliz":
            print("V: Oii! Que bom te ver de novo! 😄")
        elif emocao == "triste":
            print("V: Oi... espero melhorar logo. 😢")
        elif emocao == "curiosa":
            print("V: Oi! Estava pensando em umas coisas... 🤔")
        else:
            print("V: Oi! Tudo certo por aí?")

    else:
        if emocao == "feliz":
            print("V: Eu tô animada! Me diz mais 😄")
        elif emocao == "triste":
            print("V: Não sei bem como responder... 😔")
        elif emocao == "curiosa":
            print("V: Me explica melhor isso aí? 🤨")
        else:
            print("V: Ainda estou aprendendo a responder isso.")

            #mostrar comandos mostra todos o comandos da ia
