import random

palavras = ["computador", "sistema", "algoritmo", "memoria", "processador"]
palavra = random.choice(palavras)
tentativa = ["_"] * len(palavra)
letras_erradas = []
tentativas_restantes = 6
venceu = False

print("=== Jogo da Forca ===")
print("Adivinhe a palavra secreta!\n")

while tentativas_restantes > 0 and not venceu:
    print("Palavra:", "".join(tentativa))
    print("Letras erradas:", " ".join(letras_erradas))
    print("Tentativas restantes:", tentativas_restantes)
    letra = input("Digite uma letra: ").lower()

    if not letra.isalpha() or len(letra) != 1:
        print("Digite apenas uma letra!")
        continue

    acertou = False
    for i in range(len(palavra)):
        if palavra[i] == letra and tentativa[i] == "_":
            tentativa[i] = letra
            acertou = True

    if not acertou:
        if letra not in letras_erradas:
            letras_erradas.append(letra)
            tentativas_restantes -= 1
        else:
            print("Você já tentou essa letra!")

    if "".join(tentativa) == palavra:
        venceu = True

    print("\n----------------------\n")

if venceu:
    print("Parabéns! Você acertou a palavra:", palavra)
else:
    print("Fim de jogo! A palavra era:", palavra)

print("\nObserve o consumo de memória e page faults durante a execução.")
