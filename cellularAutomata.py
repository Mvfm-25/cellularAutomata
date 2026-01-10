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
        self.x = x
        self.y = y


    # Determina o número de vizinhos imediatos vivos.
    # Vai ajudar depois para geração.
    def calculaVizinhos(self, matriz):
        vizinhos = 0
        for(i, j) in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            if(matriz[i][j] == 1):
                vizinhos+=1
        return vizinhos

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

    def imprimeMapa(self):
        for i in range(self.altura) :
            for j in range(self.largura) :
                if(self.matriz[i][j].estado == 1):
                    color.cprint(self.matriz[i][j].estado, "red", end=" ")
                else:
                    color.cprint(self.matriz[i][j].estado, "green", end=" ")
            print()

mapa = mapa(10, 10)
mapa.geraMapa()
mapa.imprimeMapa()