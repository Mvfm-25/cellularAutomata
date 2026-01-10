# Brincando com geração de cavernas usando cellular automata.
# [mvfm]
#
# Criação : 09/01/2026  ||  Última modificação : 10/01/2026

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

    # Atualiza o estado da célula.
    def atualizaEstado(self, novoEstado):
        print(f"Atualizando estado de {self.estado} para {novoEstado}")
        self.estado = novoEstado

    # Determina o número de vizinhos imediatos paredes.
    # Vai ajudar depois para geração.
    def calculaVizinhos(self, matriz):
        # Reseta contador a cada chamada.
        self.vizinhos = 0

        # Verifica os 8 vizinhos imediatos.
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # Ignora a própria célula.
                if(dx == 0 and dy == 0):
                    continue

                nx = self.x + dx
                ny = self.y + dy

                # Verifica se o vizinho está dentro dos limites da matriz.
                if(0 <= nx < len(matriz) and 0 <= ny < len(matriz[0])):
                    if(matriz[nx][ny].estado == 1):
                        self.vizinhos += 1

        print(f"Célula analisada : ({self.x}, {self.y})")
        print(f"Número de vizinhos encontrados : {self.vizinhos}")
        print()
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
        # Contagem de de céulas Caminhos ou Paredes. 
        contParedes = 0
        contCaminhos = 0
        for i in range(self.altura) :
            for j in range(self.largura) :
                if(self.matriz[i][j].estado == 1):
                    color.cprint(self.matriz[i][j].estado, "magenta", end=" ")
                    contParedes += 1
                else:
                    color.cprint(self.matriz[i][j].estado, "white", end=" ")
                    contCaminhos += 1
            print()
        print(f"Número de Paredes : {contParedes} | Número de Caminhos : {contCaminhos}")
        print()
    
    # Função para alterar estado das células contidas no mapa.
    # Tendo mais que 5 vizinhos imediatos, a célula 'morre', vira caminho livre.
    def muta(self):
        # Contador de mundanças nessa geração.
        # Também se reinicia a cada chamada como contagem de vizinhos.
        mudancas = 0

        # 1) Primeiro calcula vizinhos para todas as células sem alterar estados
        for i in range(self.altura):
            for j in range(self.largura):
                self.matriz[i][j].calculaVizinhos(self.matriz)

        # 2) Depois aplica as mutações com base nos contadores já calculados
        for i in range(self.altura):
            for j in range(self.largura):
                if(self.matriz[i][j].vizinhos > 2):
                    # Só conta se realmente muda
                    if(self.matriz[i][j].estado == 1):  
                        self.matriz[i][j].estado = 0
                        mudancas += 1

        print(f"Número de mudanças nessa geração : {mudancas}")


mapa = mapa(3, 3)
mapa.geraMapa()
print("Estado inicial : ")
mapa.imprimeMapa()

for i in range(5):
    print(f"Geração : {i}")
    mapa.muta()
    mapa.imprimeMapa()

