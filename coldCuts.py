# Arquivo de jogo.
# Aproveitar do que já foi construido em 'cellularAutomata.py' pra fazer um rogue-like.
# [mvfm]
#
# Criado : 12/01/2026  ||  Última modificação : 14/01/2026

from cellularAutomata import mapa as mapaCA
import cellularAutomata as ca
from collections import deque
import pygame
import time
import os
import random
import json
import threading
import sys

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
            danoRestante = self.ataque
            
            # Primeiro, a armadura absorve o dano
            if jogador.armadura > 0:
                danoAbsorvido = min(danoRestante, jogador.armadura)
                jogador.armadura -= danoAbsorvido
                danoRestante -= danoAbsorvido
                print(f"{self.nome} atacou! Sua armadura absorveu {danoAbsorvido} de dano! (Armadura: {jogador.armadura})")
            
            # Se ainda houver dano, deduz do HP
            if danoRestante > 0:
                jogador.hp -= danoRestante
                print(f"{self.nome} te atacou diretamente! Você recebeu {danoRestante} de dano!")
                
                # Verifica se o jogador morreu
                if jogador.hp <= 0:
                    jogador.lidaMorte(self)
            else:
                print("Sua armadura resistiu completamente ao ataque!")
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
        self.acuracia = 0

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
                self.acuracia = 80
                self.xpParaProximoNivel = 100
            case "2":
                self.classe = "Mago"
                self.hp = 100
                self.ataque = 15
                self.armadura = 5
                self.acuracia = 85
                self.xpParaProximoNivel = 175
            case "3":
                self.classe = "Cavaleiro"
                self.hp = 125
                self.ataque = 10
                self.armadura = 10
                self.acuracia = 90
                self.xpParaProximoNivel = 150
            case "4":
                self.classe = "Ladrão"
                self.hp = 110
                self.ataque = 12
                self.armadura = 5
                self.acuracia = 95
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
    
    # Trazendo incerteza de ataques.
    # Deixar acuracia de classes altas o suficiente para não deixar tão insuportável o jogo.
    def verificaAcerto(self):
        chance = random.randint(1, 100)
        if chance <= self.acuracia:
            return True
        else:
            return False
        
# Função de ataque direcional.
    def ataca(self, mapa, direcao):
        alvoX, alvoY = 0, 0
        match direcao:
            case "7":
                alvoX, alvoY = self.x - 1, self.y - 1
            case "8":
                alvoX, alvoY = self.x - 1, self.y
            case "9":
                alvoX, alvoY = self.x - 1, self.y + 1
            case "4":
                alvoX, alvoY = self.x, self.y - 1
            case "6":
                alvoX, alvoY = self.x, self.y + 1
            case "1":
                alvoX, alvoY = self.x + 1, self.y - 1
            case "2":
                alvoX, alvoY = self.x + 1, self.y
            case "3":
                alvoX, alvoY = self.x + 1, self.y + 1
            case _:
                print("Direção inválida!")
                return
            
        # Procura se existe algum inimigo em tal posição.    
        inimigoAlvo = None
        for adv in mapa.adversarios:
            if adv.x == alvoX and adv.y == alvoY:
                # Encontrou correspondência exata.
                inimigoAlvo = adv
                break
        # Caso exista inimigo alvo.
        if inimigoAlvo:
            danoRestante = self.ataque
            # Armadura recebe o dano primeiro.
            if inimigoAlvo.armadura > 0:
                danoAbsorvido = min(danoRestante, inimigoAlvo.armadura)
                inimigoAlvo.armadura -= danoAbsorvido
                danoRestante -= danoAbsorvido
                print(f"{self.nome} atacou {inimigoAlvo.nome}! Sua armadura absorveu {danoAbsorvido} de dano! (Armadura restante : {inimigoAlvo.armadura})")
            # Se ainda houver dano, deduzirdo hp
            if danoRestante > 0:
                inimigoAlvo.hp -= danoRestante
                print(f"{self.nome} atacou {inimigoAlvo.nome} diretamente! {inimigoAlvo.nome} recebeu {danoRestante} de dano! (HP restante : {inimigoAlvo.hp})")
            # Armadura tankou todo dano!
            else :
                print(f"A armadura de {inimigoAlvo.nome} é muito forte! Sua armadura resistiu completamente seu ataque!")

            # Verifica se o inimigo morreu
            if inimigoAlvo.hp <= 0:
                print(f"\n*** Você derrotou o {inimigoAlvo.nome}! ***\n")
                mapa.adversarios.remove(inimigoAlvo)
                mapa.matriz[alvoX][alvoY].estado = 0
                # Ganha um pouco de XP pela vitória
                self.checaNivel(50)
            
        else :
            # Debug
            #print(f"Estou tentando acertar : {mapa.matriz[alvoX][alvoY].estado}, de tipo : {type(mapa.matriz[alvoX][alvoY].estado)}")
            if(mapa.matriz[alvoX][alvoY].estado == 1):
                print("Sua arma atingiu uma parede!")
                erro = random.randint(1, 100)
                if(erro >= 95):
                    print(f"Ela rebate e lhe atinge, causando {self.ataque} de dano!")
            else :
                print("Sua arma é usada para atingir o ar!")


        return

    # Só pra certificar se o jogador vai bater na parede ou não.
    def checaColisao(self, mapa, novoX, novoY):
        # Verifica limites do mapa
        if novoX < 0 or novoX >= mapa.altura or novoY < 0 or novoY >= mapa.largura:
            print("Limite do mapa!")
            return False
        
        if mapa.matriz[novoX][novoY].estado == 1:
            print("Caminho bloqueado!")
            return False
        
        # Detecta inimigos (índices 100-199)
        if isinstance(mapa.matriz[novoX][novoY].estado, int) and 100 <= mapa.matriz[novoX][novoY].estado < 200:
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
            
            # Verifica se é um item (índices 200-299)
            if isinstance(estadoAtual, int) and 200 <= estadoAtual < 300:
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
                            self.iventorio.pop(i)
                            return True
                        case 'C':
                            print("Você sente que um caminho novo se abriu...")
                            if mapa:
                                # Verifica se o portal foi criado com sucesso
                                if criaPortal(mapa):
                                    self.iventorio.pop(i)
                                    return True
                                else:
                                    print("Algo deu errado ao abrir o portal...")
                                    return False
                            return False
                        case 'P':
                            print("Você lê o pergaminho e ganha sabedoria!")
                            self.xp += 20
                            self.iventorio.pop(i)
                            return True
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
                    if mapa.matriz[nx][ny].estado == '8':
                        print("\n" + "="*50)
                        print("Você entrou no portal secreto!")
                        print("Você é puxado para outra dimensão...")
                        print("="*50 + "\n")
                        input("Pressione ENTER para continuar...")
                        
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
                            
                            # Limpa itens & adversarios antigos
                            mapa.adversarios = []
                            mapa.itens = []
                            
                            # Popula masmorra com novos inimigos
                            populaMasmorraComInimigos(mapa, quantidadeInimigos=20)
                            # Popula a nova masmorra com itens
                            populaMasmorraComItens(mapa, quantidade_items=10)
                            
                            print(f"Você acordou em uma nova masmorra! ({self.x}, {self.y})")
                            # Ganha XP por explorar masmorra
                            self.checaNivel(75)
                            return True
                            
                        except Exception as e:
                            print(f"Erro ao carregar masmorra: {e}")
                            return False
        
        print("Não há portal próximo! Procure por um portal secreto próximo a você.")
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
        
    # And died and went to hell. Good game!
    def lidaMorte(self, adversario):
        limpaTela()

        print(f"Você morreu! Sua aventura termina aqui, {self.nome}...")
        print(f"{adversario.nome} se certificou disso!")

        print("-" * 50)
        print(f"Você passou {self.lvl} meses nas cavernas... Acumulou {self.xp} de conhecimento.\n")
        print("-" * 50)
        sys.exit(0)
    
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
    
    # Verifica primeiro se já existe um portal no mapa
    for i in range(mapa.altura):
        for j in range(mapa.largura):
            if mapa.matriz[i][j].estado == '8' or mapa.matriz[i][j].estado == 8:
                print("Já existe um portal aberto no mapa!")
                return False
    
    # Primeiro, tenta encontrar células vazias de forma aleatória (mais rápido)
    tentativas = 0
    maxTentativas = 200
    
    while tentativas < maxTentativas:
        tentativas += 1
        x = random.randint(0, mapa.altura - 1)
        y = random.randint(0, mapa.largura - 1)
        
        # Verifica se a célula é um caminho livre (estado == 0)
        # Não pode ser parede (1), nem item, nem inimigo, nem portal
        if mapa.matriz[x][y].estado == 0:
            # Coloca o portal (representado por '8' como string)
            mapa.matriz[x][y].estado = '8'
            print(f"Portal secreto criado em ({x}, {y})")
            return True
    
    # Se não encontrou aleatoriamente, faz uma busca sistemática
    print("Buscando célula vazia de forma sistemática...")
    for i in range(mapa.altura):
        for j in range(mapa.largura):
            if mapa.matriz[i][j].estado == 0:
                mapa.matriz[i][j].estado = '8'
                print(f"Portal secreto criado em ({i}, {j})")
                return True
    
    print("Falha ao criar portal secreto: não há células vazias no mapa!")
    return False

# Método para facilitar encontrar o portal secreto.
# Pura conveniência, talvez secreto?
# Usando BFS
def pintaCaminhoPortal(mapa, player):
    """Usa BFS para encontrar e pintar o caminho até o portal secreto em ciano."""
    
    # Primeiro, encontra a posição do portal (verifica tanto string quanto número para compatibilidade)
    portal_x, portal_y = None, None
    for i in range(mapa.altura):
        for j in range(mapa.largura):
            estado = mapa.matriz[i][j].estado
            if estado == '8' or estado == 8:
                portal_x, portal_y = i, j
                break
        if portal_x is not None:
            break
    
    # Se não encontrar portal
    if portal_x is None:
        print("Nenhum portal aberto no mapa!")
        input("Pressione ENTER para continuar...")
        return False
    
    # BFS para encontrar o caminho mais curto
    fila = deque([(player.x, player.y)])
    visitados = {(player.x, player.y)}
    pai = {(player.x, player.y): None}  # Para rastrear o caminho
    
    # Direções dos 8 movimentos (incluindo diagonais) - correspondem aos movimentos do jogador
    # 7: ↖, 8: ↑, 9: ↗, 4: ←, 6: →, 1: ↙, 2: ↓, 3: ↘
    direções = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    encontrou_portal = False
    
    # BFS
    while fila and not encontrou_portal:
        x, y = fila.popleft()
        
        # Se encontrou o portal
        if x == portal_x and y == portal_y:
            encontrou_portal = True
            break
        
        # Explora vizinhos
        for dx, dy in direções:
            nx, ny = x + dx, y + dy
            
            # Verifica limites
            if 0 <= nx < mapa.altura and 0 <= ny < mapa.largura:
                estado_vizinho = mapa.matriz[nx][ny].estado
                # Verifica se não visitou e é caminho livre ou portal
                if (nx, ny) not in visitados and (estado_vizinho == 0 or estado_vizinho == '8' or estado_vizinho == 8):
                    visitados.add((nx, ny))
                    pai[(nx, ny)] = (x, y)
                    fila.append((nx, ny))
    
    # Se encontrou caminho
    if encontrou_portal:
        # Reconstrói o caminho
        caminho = []
        atual = (portal_x, portal_y)
        
        while pai[atual] is not None:
            caminho.append(pai[atual])
            atual = pai[atual]
        
        # Pinta o caminho em ciano (representado por 'C')
        for x, y in caminho:
            # Não pinta a posição do jogador
            if not (x == player.x and y == player.y):
                mapa.matriz[x][y].estado = 'C'
        
        print(f"Caminho para o portal encontrado! Distância: {len(caminho)} passos.")
        input("Pressione ENTER para continuar...")
        return True
    else:
        print("Não há caminho até o portal!")
        input("Pressione ENTER para continuar...")
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
            # Armazena o índice do inimigo (100 + id)
            mapa.matriz[x][y].estado = 100 + advEscolhido['id']
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
            # Armazena o índice do item (200 + id)
            mapa.matriz[x][y].estado = 200 + itemEscolhido['id']
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
    print("Controles: 7-8-9 (↖↑↗) | 4-6 (←→) | 1-2-3 (↙↓↘) | 'a' Ataca | 'c' Caminho | 'i' Inventário | 'u' Usar item | 'p' Entrar portal | 'q' Sair")
    print("-" * 50)

# Processa input do jogador.
def processaComando(comando, player, mapa, jogando):
        if comando.lower() == 'i':
            player.checaIventorio()
            input("Pressione ENTER para continuar...")
        elif comando.lower() == 't':
            print("Você... Não faz nada?")
            input("Pressione ENTER para continuar.")
        # Alterando para ataques direcionais.
        elif 'a' in comando.lower():
            print("Atacando!")
            player.ataca(mapa, comando[1])
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
        elif comando.lower() == 'c':
            pintaCaminhoPortal(mapa, player)
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