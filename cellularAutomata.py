# Brincando com geração de cavernas usando cellular automata.
# [mvfm]
#
# Criação : 09/01/2026  ||  Última modificação : 09/01/2026

import numpy as np
import random
import termcolor as color

# Estrutura básica de uma célula.
# Toda célula inicia com estado de 'parede' ('1'), '0' representa um caminho livre.
class celula:
    def __init__(self, x, y):
        self.estado = random.randint(0, 1)
        self.vizinhos = 0
        self.x = x
        self.y = y

    # Determina o número de vizinhos imediatos paredes.
    # Vai ajudar depois para geração.
    def calculaVizinhos(self, matriz, altura, largura):
        self.vizinhos = 0  # Reseta o contador
        for(i, j) in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            ni, nj = self.x + i, self.y + j
            # Verifica se está dentro dos limites
            if 0 <= ni < altura and 0 <= nj < largura:
                if matriz[ni][nj].estado == 1:
                    self.vizinhos += 1
        return self.vizinhos

# Classe principal para geração do mapa.
# Puro barulho ainda.
class mapa:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.matriz = []

    # For simpleszinho, nada complicado ainda
    # Imagino receber puro barulho por enquanto. Só quero ver se consigo.
    def geraMapa(self):
        self.matriz = [[celula(i, j) for j in range(self.largura)] for i in range(self.altura)]
        return self.matriz

    # Faz o que diz fazer. 
    # Agora com cores!
    def imprimeMapa(self):
        for i in range(self.altura) :
            for j in range(self.largura) :
                if(self.matriz[i][j].estado == 1):
                    color.cprint(self.matriz[i][j].estado, "magenta", end=" ")
                else:
                    color.cprint(self.matriz[i][j].estado, "white", end=" ")
            print()
    
    # Função para alterar estado das células contidas no mapa.
    # Tendo mais que 5 vizinhos imediatos, a célula 'morre', vira caminho livre.
    def muta(self):
        for i in range(self.altura):
            for j in range(self.largura):
                # Primeiro calcula os vizinhos de cada célula para então mutar.
                self.matriz[i][j].calculaVizinhos(self.matriz, self.altura, self.largura)

                if(self.matriz[i][j].vizinhos >= 5):
                    self.matriz[i][j].estado = 0


mapa = mapa(25, 25)
mapa.geraMapa()
print("Estado inicial : ")
mapa.imprimeMapa()

for i in range(5):
    print(f"Geração : {i}")
    mapa.muta()
    mapa.imprimeMapa()

