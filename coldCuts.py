# Arquivo de jogo.
# Aproveitar do que já foi construido em 'cellularAutomata.py' pra fazer um rogue-like.
# [mvfm]
#
# Criado : 12/01/2026  ||  Última modificação : 14/01/2026

from cellularAutomata import mapa as mapaCA
import cellularAutomata as ca
import pygame
import time
import os
import random
import json
import threading

# Classe de itens que podem ser encontrados no mapa.
class item:

    def __init__(self, nome, sprite, valor, usavel, x, y):
        self.nome = nome
        self.sprite = sprite
        # Para itens como moedas etc.
        self.valor = valor
        # Verifica se jogador consegue usar item (poções, chaves, pergaminhos.)
        self.usavel = usavel
        self.x = x
        self.y = y

# Coisas para matar
class adversario :

    def __init__(self, nome, sprite, hp, ataque, armadura, x,y):
        self.nome = nome
        self.sprite = sprite
        self.hp = hp

        self.acuracia = random.randint(25, 90)
        self.ataque = ataque
        self.armadura = armadura

        self.x = x
        self.y = y
        pass

    def verificaAcerto(self):
        chance = random.randint(1, 100)
        if chance <= self.acuracia:
            return True
        else:
            return False

    def ataca(self, jogador):
        # Verifica se o jogador está nos 8 espaços adjacentes imediatos
        distanciaX = abs(self.x - jogador.x)
        distanciaY = abs(self.y - jogador.y)
        
        # Se não está adjacente, não pode atacar
        if distanciaX > 1 or distanciaY > 1:
            return
        
        # Vê se acertou o ataque.
        if self.verificaAcerto():
            if jogador.armadura != 0:
                danoCausado = self.ataque - jogador.armadura
                print(f"{self.nome} atacou e acertou sua armadura!")
                if danoCausado < 0:
                    danoCausado = 0
            else:
                danoCausado = self.ataque
                jogador.hp -= danoCausado
                print(f"{self.nome} atacou e causou {danoCausado} de dano!")
        else:
            print(f"{self.nome} tentou te acertar... Mas falhou!")

# O Rogue!
class jogador:

    def __init__(self):
        self.x = 0
        self.y = 0

        self.nome = ""
        self.sprite = "@"
        self.classe = ""

        # Progressão de personagem
        self.lvl = 1
        self.xp = 0
        self.xpParaProximoNivel = 0

        self.hp = 0
        self.ataque = 0
        self.armadura = 0

        # Começando a testar a coleta de itens
        self.iventorio = []
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
                self.xpParaProximoNivel = 100
            case "2":
                self.classe = "Mago"
                self.hp = 100
                self.ataque = 15
                self.armadura = 5
                self.xpParaProximoNivel = 175
            case "3":
                self.classe = "Cavaleiro"
                self.hp = 125
                self.ataque = 10
                self.armadura = 10
                self.xpParaProximoNivel = 150
            case "4":
                self.classe = "Ladrão"
                self.hp = 110
                self.ataque = 12
                self.armadura = 5
                self.xpParaProximoNivel = 125

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
    
    # Função de ataque
    def ataca(self, mapa):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                targetX = self.x + dx
                targetY = self.y + dy
                
                # Verifica se há um inimigo nesta posição
                inimigoAlvo = None
                for adv in mapa.adversarios:
                    if adv.x == targetX and adv.y == targetY:
                        inimigoAlvo = adv
                        break
                
                if inimigoAlvo:
                    # Realiza o ataque
                    if inimigoAlvo.armadura > 0:
                        inimigoAlvo.armadura = inimigoAlvo.armadura - self.ataque
                        print(f"Você atacou {inimigoAlvo.nome} e acertou sua armadura!")

                    if self.ataque > 0:
                        inimigoAlvo.hp -= self.ataque
                        print(f"Causou {self.ataque} de dano! (HP: {inimigoAlvo.hp})")
                    else:
                        print("Sua arma não perfurou a armadura do inimigo!")
                    
                    # Verifica se o inimigo morreu
                    if inimigoAlvo.hp <= 0:
                        print(f"Você derrotou o {inimigoAlvo.nome}!")
                        mapa.adversarios.remove(inimigoAlvo)
                        mapa.matriz[targetX][targetY].estado = 0
                        # Ganha um pouco de XP pela vitória
                        self.checaNivel(50)
                    
                    return # Ataca apenas o primeiro encontrado

    # Só pra certificar se o jogador vai bater na parede ou não.
    def checaColisao(self, mapa, novoX, novoY):
        # Verifica limites do mapa
        if novoX < 0 or novoX >= mapa.altura or novoY < 0 or novoY >= mapa.largura:
            print("Limite do mapa!")
            return False
        
        if mapa.matriz[novoX][novoY].estado == 1:
            print("Caminho bloqueado!")
            return False
        
        # Detecta inimigos
        if mapa.matriz[novoX][novoY].estado in ['g', 'T', 'E', 'f']:
            print("Inimigo encontrado!")

        # Permite movimento para células vazias ou com items
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
            # Verifica se há item na nova posição
            estadoAtual = mapa.matriz[novoX][novoY].estado
            item_coletado = None
            
            if estadoAtual != 0 and estadoAtual != 1 and estadoAtual != self.sprite:
                # É um item! Encontra o item na lista global
                for i in range(len(mapa.itens)):
                    if mapa.itens[i].x == novoX and mapa.itens[i].y == novoY:
                        item_coletado = mapa.itens.pop(i)
                        break
            
            # Restaura célula antiga
            mapa.matriz[velhoX][velhoY].estado = 0
            # Move para nova posição
            self.x, self.y = novoX, novoY
            mapa.matriz[self.x][self.y].estado = self.sprite
            
            # Se coletou um item
            if item_coletado:
                self.adicionaItemIventorio(item_coletado)
            
            return True
        return False
    
    # Mais e mais parecido com rogue.
    def checaIventorio(self):
        if self.iventorio:
            print("Itens no invetório:")
            for item in self.iventorio:
                print(f"{item[0]} - {item[1].nome} (Valor: {item[1].valor})")
            print()
        else :
            print("Invetório vazio!\n")

    # Verificação de 'id' de itens.
    ultimoItemInserido = 0
    # Bem direto.
    def adicionaItemIventorio(self, item):
        self.iventorio.append([self.ultimoItemInserido, item])
        self.ultimoItemInserido += 1
        print(f"Item '{item.nome}' adicionado ao invetório!")

    def usaItem(self, id, mapa=None):
        for i in range(len(self.iventorio)):
            if self.iventorio[i][0] == id:
                item = self.iventorio[i][1]
                if item.usavel:
                    print(f"Usando item: {item.nome}")
                    # Implementar efeitos do item aqui
                    match item.sprite:
                        case 'V':
                            self.hp += 50
                        case 'C':
                            print("Você sente que um caminho novo se abriu...")
                            if mapa:
                                criaPortal(mapa)
                        case 'P':
                            print("Você lê o pergaminho e ganha sabedoria!")
                            self.xp += 20
                    self.iventorio.pop(i)
                    return True
                else:
                    print(f"O item '{item.nome}' não pode ser usado.")
                    return False
        print(f"Nenhum item com ID {id} encontrado no invetório.")
        return False
    
    def entraPortal(self, mapa):
        # Verifica os 8 blocos adjacentes ao jogador
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # Ignora a própria posição do jogador
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = self.x + dx, self.y + dy
                
                # Verifica se está dentro dos limites
                if 0 <= nx < mapa.altura and 0 <= ny < mapa.largura:
                    # Verifica se há um portal adjacente
                    if mapa.matriz[nx][ny].estado == '#':
                        print("Você entrou no portal secreto!")
                        print("Você é puxado para outra dimensão...")
                        
                        # Lista de masmorras disponíveis
                        masmorras_disponiveis = []
                        for i in range(11):
                            caminho = f"masmorras/masmorra{i}.txt"
                            if os.path.exists(caminho):
                                masmorras_disponiveis.append(caminho)
                        
                        if not masmorras_disponiveis:
                            print("Erro: Nenhuma masmorra disponível!")
                            return False
                        
                        # Escolhe uma masmorra aleatória
                        nova_masmorra = random.choice(masmorras_disponiveis)
                        
                        try:
                            # Carrega a nova masmorra
                            mapa.leMapaExportado(nova_masmorra)
                            
                            # Encontra uma posição inicial válida na nova masmorra
                            if not self.encontraPosicaoInicial(mapa):
                                print("Erro: Não foi possível encontrar uma posição válida na nova masmorra!")
                                return False
                            
                            # Coloca o jogador no mapa
                            mapa.matriz[self.x][self.y].estado = self.sprite
                            
                            # Limpa itens antigos
                            mapa.itens = []
                            
                            # Popula a nova masmorra com itens
                            populaMasmorraComItens(mapa, quantidade_items=10)
                            
                            print(f"Você acordou em uma nova masmorra! ({self.x}, {self.y})")
                            input("Pressione ENTER para continuar...")
                            # Ganha XP por explorar masmorra
                            self.checaNivel(75)
                            return True
                            
                        except Exception as e:
                            print(f"Erro ao carregar masmorra: {e}")
                            return False
        
        print("Não há portal próximo!")
        return False
    
    # Progressão de nível
    # Tentando deixar as diferenças entre classes mais significativas.
    def checaNivel(self, adicaoXP):
        if(self.xp + adicaoXP) >= self.xpParaProximoNivel:
            self.lvl += 1
            self.xp = (self.xp + adicaoXP) - self.xpParaProximoNivel
            self.xpParaProximoNivel = int(self.xpParaProximoNivel * 1.50)

            # Atualização stats
            print("Parabéns! Você subiu de nível!")
            match self.classe:
                case "Bárbaro":
                    self.hp += 15
                    self.ataque += 5
                    self.armadura += 1
                case "Mago":
                    self.hp += 5
                    self.ataque += 7
                    self.armadura += 2
                case "Cavaleiro":
                    self.hp += 10
                    self.ataque += 3
                    self.armadura += 5
                case "Ladrão":
                    self.hp += 5
                    self.ataque += 4
                    self.armadura += 3
            print(f"Novo nível: {self.lvl} | HP: {self.hp} | Ataque: {self.ataque} | Armadura: {self.armadura}\n")
            input("Pressione ENTER para continuar...")
        else :
            self.xp += adicaoXP
            print(f"Você ganhou {adicaoXP}xp!")
        

    
# Classe para gerenciar a música de fundo
class GerenciadorMusica:
    def __init__(self):
        pygame.mixer.init()
        self.tocando = False
        self.thread = None
    
    def tocaMusica(self, caminhoMusica, loops=-1):
        """Toca música em uma thread separada, não bloqueando o game loop"""
        if self.tocando:
            self.paraMusica()
        
        self.tocando = True
        self.thread = threading.Thread(target=self._tocaEmBackground, args=(caminhoMusica, loops))
        self.thread.daemon = True  # Thread daemon encerra com o programa
        self.thread.start()
    
    def _tocaEmBackground(self, caminhoMusica, loops):
        """Função interna que roda na thread separada"""
        try:
            pygame.mixer.music.load(caminhoMusica)
            pygame.mixer.music.play(loops)
            
            # Aguarda enquanto música toca
            while pygame.mixer.music.get_busy() and self.tocando:
                time.sleep(0.1)
        except Exception as e:
            print(f"Erro ao tocar música: {e}")
        finally:
            self.tocando = False
    
    def paraMusica(self):
        """Para a música"""
        self.tocando = False
        pygame.mixer.music.stop()
        
    
# Popula a masmorra com um caminho secreto
def criaPortal(mapa):
    """Cria um portal secreto em uma posição aleatória do mapa"""
    tentativas = 0
    maxTentativas = 100
    
    while tentativas < maxTentativas:
        tentativas += 1
        x = random.randint(0, mapa.altura - 1)
        y = random.randint(0, mapa.largura - 1)
        
        # Verifica se a célula é um caminho livre
        if mapa.matriz[x][y].estado == 0:
            # Coloca o portal (representado por '8')
            mapa.matriz[x][y].estado = '8'
            print(f"Portal secreto criado em ({x}, {y})")
            return True
    
    print("Falha ao criar portal secreto após várias tentativas.")
    return False

# Popula masmorra com inimigos. 
# Quase idêntico ao de itens.
def populaMasmorraComInimigos(mapa, quantidadeInimigos=20):
    adversarios = 0
    tentativas = 0
    maxTentativas = quantidadeInimigos * 10

    while adversarios < quantidadeInimigos and tentativas < maxTentativas:
        tentativas += 1

        x = random.randint(0, mapa.altura - 1)
        y = random.randint(0, mapa.largura - 1)

        if mapa.matriz[x][y].estado == 0:
            with open("entidades/adversarios.json", "r") as file :
                advData = json.load(file)

            advEscolhido = random.choice(advData)
            novoAdv = adversario(
                nome=advEscolhido['nome'],
                sprite=advEscolhido['sprite'],
                hp=advEscolhido['hp'],
                ataque=advEscolhido['ataque'],
                armadura=advEscolhido['armadura'],
                x=x,
                y=y
            )

            mapa.adversarios.append(novoAdv)
            mapa.matriz[x][y].estado = novoAdv.sprite
            adversarios += 1

    print(f"Total de inimigos inseridos : {adversarios}")


# Função para popular a masmorra com itens
def populaMasmorraComItens(mapa, quantidadeItems=10):
    """Coloca items aleatoriamente no mapa em células vazias"""
    itensColocados = 0
    tentativas = 0
    maxTentativas = quantidadeItems * 10  # Evita loop infinito
    
    while itensColocados < quantidadeItems and tentativas < maxTentativas:
        tentativas += 1
        
        # Escolhe posição aleatória
        x = random.randint(0, mapa.altura - 1)
        y = random.randint(0, mapa.largura - 1)
        
        # Verifica se é caminho livre, não ocupado por mais nada.
        if mapa.matriz[x][y].estado == 0:
            # Escolhe item aleatório, importando de items do JSON
            with open("entidades/items.json", "r") as file:
                itemData = json.load(file)

            itemEscolhido = random.choice(itemData)

            novoItem = item(
                nome=itemEscolhido['nome'],
                sprite=itemEscolhido['sprite'],
                valor=itemEscolhido['valor'],
                usavel=itemEscolhido['usavel'],
                x=x,
                y=y
            )
            
            # Adiciona à lista de itens do mapa e atualiza matriz
            mapa.itens.append(novoItem)
            mapa.matriz[x][y].estado = novoItem.sprite
            itensColocados += 1
    
    print(f"Total de itens colocados: {itensColocados}")

# Função para limpar a tela (funciona em Windows e Linux)
def limpaTela():
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para desenhar a interface do jogo
def desenhaInterface(player, mapa):
    limpaTela()
    print("=" * 50)
    print(f"Jogador: {player.nome} | Classe: {player.classe} | Nível: {player.lvl} | XP: {player.xp}")
    print(f"HP: {player.hp} | Ataque: {player.ataque} | Armadura: {player.armadura}")
    print(f"Posição: ({player.x}, {player.y})")
    print("=" * 50)
    print()
    print(f"{mapa.titulo}")
    mapa.imprimeMapa()
    print()
    print("Controles: 7-8-9 (↖↑↗) | 4-6 (←→) | 1-2-3 (↙↓↘) | 'a' Ataca | 'i' Inventário | 'u' Usar item | 'p' Entrar portal | 'q' Sair")
    print("-" * 50)

# Processa input do jogador.
def processaComando(comando, player, mapa, jogando):
        if comando.lower() == 'i':
            player.checaIventorio()
            input("Pressione ENTER para continuar...")
        elif comando.lower() == 'a':
            print("Atacando!")
            player.ataca(mapa)
            input("Pressione ENTER para continuar...")
        elif comando.lower() == 'u':
            print("Pressione o 'id' do item que deseja usar:")
            player.checaIventorio()
            id_item = int(input("ID do item: "))
            player.usaItem(id_item, mapa)
            input("Pressione ENTER para continuar...")
            # MUHAHAHAHA!
        elif comando.lower() == 'p':
            player.entraPortal(mapa)    
        elif comando.lower() == 'q':
            print("Encerrando o jogo...")
            jogando = False
        elif comando in ['1', '2', '3', '4', '6', '7', '8', '9']:
            player.movimenta(mapa, comando)
        else:
            print("Comando inválido!")
            input("Pressione ENTER para continuar...")
        
        return jogando

# GAME LOOP PRINCIPAL
def main():

    # Cria instância do gerenciador de música
    musica = GerenciadorMusica()
    musica.tocaMusica("musica/coldCuts - dungeon1.ogg", loops=-1)

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
   
    # Inicializa lista de inimigos no mapa
    mapa.adversarios = []
    # Inicializa lista de itens no mapa
    mapa.itens = []
    
    # Popula masmorra com inimigos
    populaMasmorraComInimigos(mapa, quantidadeInimigos=20)
    # Popula masmorra com itens
    populaMasmorraComItens(mapa, quantidadeItems=10)
    
    # Loop principal do jogo
    jogando = True
    while jogando:
        # Desenha a interface
        desenhaInterface(player, mapa)

        for adversario in mapa.adversarios :
            adversario.ataca(player)
        
        # Recebe input do jogador
        comando = input("Seu comando: ").strip()
        jogando = processaComando(comando, player, mapa, jogando)

if __name__ == "__main__":
    main()