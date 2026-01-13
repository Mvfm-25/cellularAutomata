# Arquivo de jogo.
# Aproveitar do que já foi construido em 'cellularAutomata.py' pra fazer um rogue-like.
# [mvfm]
#
# Criado : 12/01/2026  ||  Última modificação : 12/01/2026

from cellularAutomata import mapa as mapaCA
import cellularAutomata as ca
import subprocess
import os

# O Rogue!
class jogador:

    def __init__(self):
        self.x = 0
        self.y = 0

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
        input("Pressione ENTER para progredir...\n")

    # Função para encontrar uma posição inicial válida (caminho livre) & com não muitos vizinhos.
    # Não queremos prender o jogador em um beco sem saída.
    def encontraPosicaoInicial(self, mapa):
        # Tenta encontrar uma posição com pelo menos um caminho livre ao redor (≤ 3 vizinhos = parede)
        for i in range(mapa.altura):
            for j in range(mapa.largura):
                if mapa.matriz[i][j].estado == 0:
                    vizinhos = mapa.matriz[i][j].calculaVizinhos(mapa.matriz)
                    if vizinhos <= 3:
                        # Verifica se há pelo menos um vizinho livre para movimentação
                        tem_caminho_livre = False
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if dx == 0 and dy == 0:
                                    continue
                                nx, ny = i + dx, j + dy
                                if 0 <= nx < mapa.altura and 0 <= ny < mapa.largura:
                                    if mapa.matriz[nx][ny].estado == 0:
                                        tem_caminho_livre = True
                                        break
                            if tem_caminho_livre:
                                break
                        
                        if tem_caminho_livre:
                            self.x = i
                            self.y = j
                            return True
        return False

    # Só pra certificar se o jogador vai bater na parede ou não.
    def checaColisao(self, mapa, novoX, novoY):
        # Verifica limites do mapa
        if novoX < 0 or novoX >= mapa.altura or novoY < 0 or novoY >= mapa.largura:
            print("Limite do mapa!")
            return False
        
        if mapa.matriz[novoX][novoY].estado == 1:
            print("Caminho bloqueado!")
            return False
        return True

    # Função pra movimentar o jogador.
    def movimenta(self, mapa, direcao):
        # Guarda posição antiga
        velhoX, velhoY = self.x, self.y
        novoX, novoY = self.x, self.y

        match direcao:
            case "7":
                novoX, novoY = self.x - 1, self.y - 1
            case "8":
                novoX, novoY = self.x - 1, self.y
            case "9":
                novoX, novoY = self.x - 1, self.y + 1
            case "4":
                novoX, novoY = self.x, self.y - 1
            case "6":
                novoX, novoY = self.x, self.y + 1
            case "1":
                novoX, novoY = self.x + 1, self.y - 1
            case "2":
                novoX, novoY = self.x + 1, self.y
            case "3":
                novoX, novoY = self.x + 1, self.y + 1
            case _:
                return False

        # Verifica colisão antes de mover
        if self.checaColisao(mapa, novoX, novoY):
            # Restaura célula antiga
            mapa.matriz[velhoX][velhoY].estado = 0
            # Move para nova posição
            self.x, self.y = novoX, novoY
            mapa.matriz[self.x][self.y].estado = self.sprite
            return True
        return False

# Função para limpar a tela (funciona em Windows e Linux)
def limpaTela():
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para desenhar a interface do jogo
def desenhaInterface(player, mapa):
    limpaTela()
    print("=" * 50)
    print(f"Jogador: {player.nome} | Classe: {player.classe}")
    print(f"HP: {player.hp} | Ataque: {player.ataque} | Armadura: {player.armadura}")
    print(f"Posição: ({player.x}, {player.y})")
    print("=" * 50)
    print()
    print(f"{mapa.titulo}")
    mapa.imprimeMapa()
    print()
    print("Controles: 7-8-9 (↖↑↗) | 4-6 (←→) | 1-2-3 (↙↓↘) | 'q' para sair")
    print("-" * 50)

# GAME LOOP PRINCIPAL
def main():
    # Cria instância do mapa.
    mapa = mapaCA()

    # Cria instância do jogador.
    player = jogador()

    # Parecendo Dwarf Fortress.
    print("Desejas criar uma nova masmorra ou carregar uma existente?")
    escolha = input("1 - Criar nova masmorra  |  2 - Carregar masmorra existente\n")

    match escolha:
        case "1":
            dimensoes = int(input("Digite as dimensões do mapa (ex: 20 para 20x20):"))
            mapa.setAltura(dimensoes)
            mapa.setLargura(dimensoes)
            # Número padrão de gerações. Deixar como escolha do jogador depois.
            mapa.geraMapa(geracoes=10)
        case "2":
            caminhoArquivo = input("Determine a masmorra a ser carregada (ex: 'masmorras/masmorra0.txt'):\n")
            mapa.leMapaExportado(caminhoArquivo)
            player.encontraPosicaoInicial(mapa)
    
    # Encontra posição inicial
    if not player.encontraPosicaoInicial(mapa):
        print("Erro: Não foi possível encontrar uma posição inicial válida!")
        return
    
    # Coloca o jogador no mapa
    mapa.matriz[player.x][player.y].estado = player.sprite
    
    # Loop principal do jogo
    jogando = True
    while jogando:
        # Desenha a interface
        desenhaInterface(player, mapa)
        
        # Recebe input do jogador
        comando = input("Seu comando: ").strip()
        
        # Processa comando
        if comando.lower() == 'q':
            print("Encerrando o jogo...")
            jogando = False
        elif comando in ['1', '2', '3', '4', '6', '7', '8', '9']:
            player.movimenta(mapa, comando)
        else:
            print("Comando inválido!")
            input("Pressione ENTER para continuar...")

if __name__ == "__main__":
    main()