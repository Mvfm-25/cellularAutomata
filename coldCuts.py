# Arquivo de jogo.
# Aproveitar do que já foi construido em 'cellularAutomata.py' pra fazer um rogue-like.
# [mvfm]
#
# Criado : 12/01/2026  ||  Última modificação : 12/01/2026

import cellularAutomata as ca
import subprocess

# O Rogue!
class jogador:

    def __init__(self):
        ca.celula.__init__(self, 0, 0)
        self.nome = ""
        self.sprite = "@"
        self.classe = ""

        self.lvl = 1
        self.xp = 0

        self.hp = 0
        self.ataque = 0
        self.armadura = 0
        self.criaPersonagem()

    # Função para criar personagem. Nada muito complicado ainda.
    # Talvez adicionar coisas como 'espaço do inventário', 'velocidade' & 'habilidades' depois.
    def criaPersonagem(self):
        print("--  Criação de Personagem --")
        self.nome = input("Qual o seu nome?\n")

        print(f"Escolha sua classe, {self.nome} : ")
        self.classe = input("1 - Bárbaro  |  2 - Mago  |  3 - Cavaleiro  |  4 - Ladrão\n")
        match self.classe: 
            case "1":
                self.classe = "Bárbaro"
                self.hp = 150
                self.ataque = 20
                self.armadura = 0
            case "2":
                self.classe = "Mago"
                self.hp = 100
                self.ataque = 15
                self.armadura = 5
            case "3":
                self.classe = "Cavaleiro"
                self.hp = 125
                self.ataque = 10
                self.armadura = 10
            case "4":
                self.classe = "Ladrão"
                self.hp = 110
                self.ataque = 12
                self.armadura = 5

        print(f"Personagem criado com sucesso! \nNome : {self.nome} \nClasse : {self.classe} \nHP : {self.hp} \nAtaque : {self.ataque} \nArmadura : {self.armadura}\n")
        

    # Só pra certificar se o jogador vai bater na parede ou não.
    def checaColisao(self, mapa, novoX, novoY):
        if(mapa.matriz[novoX][novoY].estado == 1):
            print("Caminho bloqueado!")
            return False
        else : 
            return True

    # Função pra movimentar o jogador.
    # Talvez usá-la pra npc's também.
    def movimenta(self, mapa, direcao):
        match direcao:
            case "7":
                if(self.checaColisao(mapa, self.x - 1, self.y - 1)):
                    self.x -= 1
                    self.y -= 1
            case "8":
                if(self.checaColisao(mapa, self.x, self.y - 1)):
                    self.y -= 1
            case "9":
                if(self.checaColisao(mapa, self.x + 1, self.y - 1)):
                    self.x += 1
                    self.y -= 1
            case "4":
                if(self.checaColisao(mapa, self.x - 1, self.y)):
                    self.x -= 1
            case "6":
                if(self.checaColisao(mapa, self.x + 1, self.y)):
                    self.x += 1
            case "1":
                if(self.checaColisao(mapa, self.x - 1, self.y + 1)):
                    self.x -= 1
                    self.y += 1
            case "2":
                if(self.checaColisao(mapa, self.x, self.y + 1)):
                    self.y += 1
            case "3":
                if(self.checaColisao(mapa, self.x + 1, self.y + 1)):
                    self.x += 1
                    self.y += 1

# O jogo!
mapa = ca.mapa(20, 20)
mapa.leMapaExportado("masmorras\masmorra0.txt")

player = jogador()

if(input != "q"):
    # Limpa tela
    subprocess.run("clear", shell=True)
    print(f"Jogador : {player.nome}  |  Classe : {player.classe}  |  HP : {player.hp}  |  Ataque : {player.ataque}  |  Armadura : {player.armadura}\n")
    mapa.imprimeMapa()


