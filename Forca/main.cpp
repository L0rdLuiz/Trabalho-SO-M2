#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <ctime>
#include <cstdlib>

using namespace std;

int main() {
    vector<string> palavras = {"computador", "sistema", "algoritmo", "memoria", "processador"};

    srand(time(nullptr));
    string palavra = palavras[rand() % palavras.size()];

    string tentativa(palavra.size(), '_');
    vector<char> letrasErradas;
    int tentativasRestantes = 6;
    bool venceu = false;

    cout << "=== Jogo da Forca ===\n";
    cout << "Adivinhe a palavra secreta!\n\n";

    while (tentativasRestantes > 0 && !venceu) {
        cout << "Palavra: " << tentativa << "\n";
        cout << "Letras erradas: ";
        for (char c : letrasErradas) cout << c << " ";
        cout << "\nTentativas restantes: " << tentativasRestantes << "\n";
        cout << "Digite uma letra: ";

        char letra;
        cin >> letra;
        letra = tolower(letra);

        if (!isalpha(letra)) {
            cout << "Digite apenas letras!\n";
            continue;
        }

        bool acertou = false;
        for (size_t i = 0; i < palavra.size(); i++) {
            if (palavra[i] == letra && tentativa[i] == '_') {
                tentativa[i] = letra;
                acertou = true;
            }
        }

        if (!acertou) {
            if (find(letrasErradas.begin(), letrasErradas.end(), letra) == letrasErradas.end()) {
                letrasErradas.push_back(letra);
                tentativasRestantes--;
            } else {
                cout << "Você já tentou essa letra!\n";
            }
        }

        if (tentativa == palavra) {
            venceu = true;
        }

        cout << "\n----------------------\n";
    }

    if (venceu)
        cout << "Parabéns! Você acertou a palavra: " << palavra << "\n";
    else
        cout << "Fim de jogo! A palavra era: " << palavra << "\n";
    return 0;
}
