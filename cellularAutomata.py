# Brincando com geração de cavernas usando cellular automata.
# [mvfm]
#
# Criação : 09/01/2026  ||  Última modificação : 13/01/2026

import numpy as np
import random
import termcolor as color
import time
from datetime import datetime

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
        print(f"Célula atualizada : ({self.x}, {self.y})")
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

        #print(f"Célula analisada : ({self.x}, {self.y})")
        #print(f"Número de vizinhos encontrados : {self.vizinhos}")
        #print()
        return self.vizinhos

# Classe principal para geração do mapa.
# Puro barulho ainda.
class mapa:
    def __init__(self):
        self.largura = 0
        self.altura = 0
        self.titulo = ""
        self.matriz = []

    # Modularizando setters.
    def setAltura(self, altura):
        self.altura = altura
    def setLargura(self, largura):
        self.largura = largura

    # Criação de mapas.
    # Agora recebe quantidade de gerações para maior controle e não ter que depender do main, assim como sua exportação final.
    def geraMapa(self, geracoes):
        self.matriz = [[celula(i, j) for j in range(self.largura)] for i in range(self.altura)]
        for g in range(geracoes):
            print(f"Geração {g + 1} de {geracoes}")
            self.atualizaCelulas()
        self.exportaEstadoFinal()
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
                    color.cprint("1", "magenta", end=" ")
                    contParedes += 1
                elif(self.matriz[i][j].estado == "@"):
                    color.cprint("@", "yellow", end=" ")
                elif(self.matriz[i][j].estado == 0):
                    color.cprint("0", "white", end=" ")
                    contCaminhos += 1
                elif(self.matriz[i][j].estado == "8"):
                    # Sprite da PORTA SECRETA.
                    color.cprint("8", "light_blue", end=" ")
                elif(self.matriz[i][j].estado in ['g', 'T', 'E', 'f']):
                    color.cprint(self.matriz[i][j].estado, "red", end=" ")
                else:
                    # Renderiza itens em verde
                    color.cprint(self.matriz[i][j].estado, "green", end=" ")
            print()
        print(f"Número de Paredes : {contParedes} | Número de Caminhos : {contCaminhos}")
        print()
    
    # Função para alterar estado das células contidas no mapa.
    # Tendo mais que 4 vizinhos imediatos, a célula 'morre', vira caminho livre.
    def atualizaCelulas(self):
        # Contador de mundanças nessa geração.
        # Também se reinicia a cada chamada como contagem de vizinhos.
        mudancas = 0

        # Contador do tempo de início da atualizção.
        comeco = time.perf_counter()

        # 1) Primeiro calcula vizinhos para todas as células sem alterar estados
        for i in range(self.altura):
            for j in range(self.largura):
                self.matriz[i][j].calculaVizinhos(self.matriz)

        # 2) Depois aplica as mudanças e mutações com base nos contadores já calculados
        for i in range(self.altura):
            for j in range(self.largura):
                if(self.matriz[i][j].vizinhos > 4):
                    # Só conta se realmente muda.
                    if(self.matriz[i][j].estado == 1):  
                        self.matriz[i][j].atualizaEstado(0)
                        mudancas += 1
                    if(self.mutaCelula(self.matriz[i][j])):
                        mudancas += 1

        # Contador do tempo de fim da atualização.
        fim = time.perf_counter()
        print(f"Mapa atualizado em : {fim - comeco:.4f} segundos")
        print(f"Número de mudanças nessa geração : {mudancas}")

    # Trazendo aleatoridade pra criação das cavernas.
    def mutaCelula(self, celula):
        dado = random.randint(0,100)
        # 25% de chance de mudar o estado.
        # Equivalente de jogar um D100, 1/4 de chance.
        if(dado >= 75):
            celula.atualizaEstado(1) if celula.estado == 0 else celula.atualizaEstado(0)
            print(f"Mutação aleatória ocorrida na célula ({celula.x}, {celula.y})!")
            return True
        else :
            return False
        
    # Escreve o estado final do mapa em um arquivo de texto.
    def exportaEstadoFinal(self):
        ultimo = self.verificaUltimoExportado()
        with open("masmorras\masmorra" + str(ultimo) + ".txt", 'w', encoding="utf-8") as f:
            print(f"{self.geraNome()}!", file=f)
            print(f"Data de criação : {datetime.today().strftime('%d/%m/%Y')}\n", file=f)
            for i in range(self.altura):
                for j in range(self.largura):
                    f.write(f"{self.matriz[i][j].estado} ")
                f.write("\n")
        print(f"Estado final exportado para o arquivo : masmorras\masmorra{ultimo}.txt")
        # Atualiza contador de arquivos exportados.
        with open("ultimo_exportado.txt", 'w', encoding="utf-8") as f:
            f.write(str(ultimo + 1))

    # Agora ficando mais parecido com Rogue.
    # Gerador automático de nomes pras masmorras criadas.
    def geraNome(self):
        p = ["Masmorra", "Caverna", "Abismo", "Calabouço", "Covil", "Tumba"]
        m = ["Sombria", "Sombrio", "Perdida", "Perdido", "Esquecida", "Esquecido", "Maldita", "Maldito"]
        f = ["Dos Mortos", "Dos Condenados", "Das Almas", "Do Senhor", "Da Desgraça", "Da Perdição"]

        nome = random.choice(p) + " " + random.choice(m) + " " + random.choice(f)
        self.titulo = nome
        return nome
    
    # Maneira mais chata que achei pra fazer isso, mas funciona pelo menos.
    # Variáveis globais não me ajudaram.
    def verificaUltimoExportado(self):
        with open("ultimo_exportado.txt", 'r', encoding="utf-8") as f:
            ultimo = f.read()
            print("Último mapa exportado : " + ultimo)
            return int(ultimo)
    
    # Torna 'jogável' o mapa escrito em arquivo.
    def leMapaExportado(self, caminhoArquivo):
        with open(caminhoArquivo, 'r', encoding="utf-8") as f:
            print(f"Lendo mapa do arquivo : {caminhoArquivo}")
            linhas = f.readlines()
            # Captura o título da primeira linha
            self.titulo = linhas[0].strip()
            print(f"Título do mapa : {self.titulo}")
            # Ignora as duas outras linhas (data & espaço vazio).
            linhas = linhas[3:]
            # Assumindo sempre mapas quadrados por enquanto.
            self.altura = len(linhas)
            self.largura = len(linhas)
            print(f"Dimensões : {self.largura}x{self.altura}")
            self.matriz = [[celula(i, j) for j in range(self.largura)] for i in range(self.altura)]
            for i in range(self.altura):
                valores = linhas[i].strip().split()
                for j in range(self.largura):
                    self.matriz[i][j].estado = int(valores[j])
        print(f"Mapa importado do arquivo : {caminhoArquivo}")

        return self

        

#mapa = mapa(20, 20)
#apa.geraMapa()
#print("Estado inicial : ")
#mapa.imprimeMapa()

#comecoSim = time.perf_counter()
#for i in range(10):
#    print(f"Geração : {i}")
#    mapa.atualizaCelulas()
#    mapa.imprimeMapa()

#fimSim = time.perf_counter()
#print(f"Simulação finalizada em : {fimSim - comecoSim:.4f} segundos")

# Ecrevendo mapa final em arquivo.
#mapa.exportaEstadoFinal()
