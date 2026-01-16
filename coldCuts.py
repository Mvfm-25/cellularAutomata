# Arquivo de jogo.
# Aproveitar do que já foi construido em 'cellularAutomata.py' pra fazer um rogue-like.
# [mvfm]
#
# Criado : 12/01/2026  ||  Última modificação : 16/01/2026

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

# Classe para gerenciar a música de fundo
class GerenciadorMusica:
    def __init__(self):
        pygame.mixer.init()
        self.tocando = False
        self.thread = None
        self.efeitosAtivos = []  # Lista para manter referência dos sons em toque

    def tocaEfeito(self, caminhoSom):
        """ Toca efeito sonoro sem bloquear o game loop """
        try:
            som = pygame.mixer.Sound(caminhoSom)
            som.play()
            self.efeitosAtivos.append(som)  # Mantém referência para não ser coletado
            print(f"Efeito sonoro tocado: {caminhoSom}")
        except Exception as e:
            print(f"Erro ao tocar efeito sonoro: {e}")
    
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

# Cria instância do gerenciador de música
# Colocando desse jeito por conveniência?
gMusica = GerenciadorMusica()
gMusica.tocaMusica("musica/coldCuts - dungeon1.ogg", loops=-1)

# Classe de itens que podem ser encontrados no mapa.
class item:

    def __init__(self, nome, sprite, valor, usavel, glossario, x, y):
        self.nome = nome
        self.sprite = sprite
        # Para itens como moedas etc.
        self.valor = valor
        # Verifica se jogador consegue usar item (poções, chaves, pergaminhos.)
        self.usavel = usavel
        # O que o jogador vai conseguir pesquisar em seu dicionário.
        self.glossario = glossario
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
                    gMusica.tocaEfeito("musica/wilhelm")
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

        # Stats de personagem
        self.hp = 0
        self.hpMaximo = 0
        self.ataque = 0
        self.armadura = 0
        self.acuracia = 0

        # Misc.
        self.inventario = []
        self.ultimoItemInserido = 0
        self.dicionario = []

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
                self.hpMaximo = 150
                self.ataque = 20
                self.armadura = 0
                self.acuracia = 80
                self.xpParaProximoNivel = 100
            case "2":
                self.classe = "Mago"
                self.hp = 100
                self.hpMaximo = 100
                self.ataque = 15
                self.armadura = 5
                self.acuracia = 85
                self.xpParaProximoNivel = 175
            case "3":
                self.classe = "Cavaleiro"
                self.hp = 125
                self.hpMaximo = 125
                self.ataque = 10
                self.armadura = 10
                self.acuracia = 90
                self.xpParaProximoNivel = 150
            case "4":
                self.classe = "Ladrão"
                self.hp = 110
                self.hpMaximo = 110
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
                if mapa.matriz[i][j].estado == '0':
                    vizinhos = mapa.matriz[i][j].calculaVizinhos(mapa.matriz)
                    if vizinhos <= 3:
                        # Verifica se há pelo menos um vizinho livre para movimentação
                        tem_caminho_livre = False
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if dx == '0' and dy == '0':
                                    continue
                                nx, ny = i + dx, j + dy
                                if 0 <= nx < mapa.altura and 0 <= ny < mapa.largura:
                                    if mapa.matriz[nx][ny].estado == '0':
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
                mapa.matriz[alvoX][alvoY].estado = '0'
                # Ganha um pouco de XP pela vitória
                self.checaNivel(50)
            
        else :
            # Debug
            #print(f"Estou tentando acertar : {mapa.matriz[alvoX][alvoY].estado}, de tipo : {type(mapa.matriz[alvoX][alvoY].estado)}")
            if(mapa.matriz[alvoX][alvoY].estado == '1'):
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
        
        if mapa.matriz[novoX][novoY].estado == '1':
            print("Caminho bloqueado!")
            return False
        
        # Detecta inimigos
        if mapa.matriz[novoX][novoY].estado in mapa.spritesInimigos :
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
            itemColetado = None
            
            # Procura na lista de colecionáveis
            for i in range(len(mapa.colecionaveis)):
                if mapa.colecionaveis[i].x == novoX and mapa.colecionaveis[i].y == novoY:
                    itemColetado = mapa.colecionaveis.pop(i)
                    break
            
            # Restaura célula antiga
            mapa.matriz[velhoX][velhoY].estado = '0'
            # Move para nova posição
            self.x, self.y = novoX, novoY
            mapa.matriz[self.x][self.y].estado = self.sprite
            
            # Se coletou um item
            if itemColetado:
                self.adicionaItemInventario(itemColetado)
            
            return True
        return False
    
    # Mais e mais parecido com rogue.
    def checaInventario(self):
        if self.inventario:
            print("Itens no inventário:")
            for item in self.inventario:
                print(f"{item[0]} - {item[1].nome} (Valor: {item[1].valor})")
            print()
        else :
            print("Inventário vazio!\n")

    # Bem direto.
    def adicionaItemInventario(self, item):
        self.inventario.append([self.ultimoItemInserido, item])
        self.ultimoItemInserido += 1
        # Palavra agora é conhecida!
        self.dicionario.append([item.nome, item.glossario])
        print(f"Item '{item.nome}' adicionado ao inventário!")
        input("Pressione ENTER para continuar...")

    def usaItem(self, id, mapa=None):
        for i in range(len(self.inventario)):
            if self.inventario[i][0] == id:
                item = self.inventario[i][1]
                if item.usavel:
                    print(f"Usando item: {item.nome}")
                    # Implementar efeitos do item aqui
                    match item.sprite:
                        case 'V':
                            cura = 50
                            curaReal = min(cura, self.hpMaximo - self.hp)
                            self.hp += curaReal
                            print(f"Você recuperou {curaReal} de HP! (HP: {self.hp}/{self.hpMaximo})")
                            self.inventario.pop(i)
                            return True
                        case 'C':
                            print("Você sente que um caminho novo se abriu...")
                            if mapa:
                                # Verifica se o portal foi criado com sucesso
                                if criaPortal(mapa):
                                    self.inventario.pop(i)
                                    return True
                                else:
                                    print("Algo deu errado ao abrir o portal...")
                                    return False
                            return False
                        case 'P':
                            print("Você lê o pergaminho e ganha sabedoria!")
                            self.xp += 20
                            self.inventario.pop(i)
                            return True
                    self.inventario.pop(i)
                    return True
                else:
                    print(f"O item '{item.nome}' não pode ser usado.")
                    return False
        print(f"Nenhum item com ID {id} encontrado no inventário.")
        return False
    
    def entraPortal(self, mapa):
        # Verifica os 8 blocos adjacentes ao jogador
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # Ignora a própria posição do jogador
                if dx == '0' and dy == '0':
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
                        masmorrasDisponiveis = []
                        for i in range(11):
                            caminho = f"masmorras/masmorra{i}.txt"
                            if os.path.exists(caminho):
                                masmorrasDisponiveis.append(caminho)
                        
                        if not masmorrasDisponiveis:
                            print("Erro: Nenhuma masmorra disponível!")
                            return False
                        
                        # Escolhe uma masmorra aleatória
                        novaMasmorra = random.choice(masmorrasDisponiveis)
                        
                        try:
                            # Carrega a nova masmorra
                            mapa.leMapaExportado(novaMasmorra)
                            
                            # Inicializa a masmorra para o jogo
                            if not inicializaMasmorraParaJogo(mapa, self, quantidadeInimigos=20, quantidadeItems=10):
                                return False
                            
                            print(f"Você acordou em uma nova masmorra! ({self.x}, {self.y})")
                            # Ganha XP por explorar masmorra
                            self.checaNivel(75)
                            
                            # Atualiza a tela para mostrar a nova masmorra com jogador e itens
                            desenhaInterface(self, mapa)
                            input("Pressione ENTER para continuar...")
                            
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
                    self.hpMaximo += 15
                    self.ataque += 5
                    self.armadura += 1
                case "Mago":
                    self.hp += 5
                    self.hpMaximo += 5
                    self.ataque += 7
                    self.armadura += 2
                case "Cavaleiro":
                    self.hp += 10
                    self.hpMaximo += 10
                    self.ataque += 3
                    self.armadura += 5
                case "Ladrão":
                    self.hp += 5
                    self.hpMaximo += 5
                    self.ataque += 4
                    self.armadura += 3
            print(f"Novo nível: {self.lvl} | HP: {self.hp} | Ataque: {self.ataque} | Armadura: {self.armadura} | HP max : {self.hpMaximo}\n")
            input("Pressione ENTER para continuar...")
        else :
            self.xp += adicaoXP
            print(f"Você ganhou {adicaoXP}xp!")
        
    # And died and went to hell. Good game!
    def lidaMorte(self, adversario):
        gMusica.paraMusica()
        time.sleep(0.5)  # Aguarda música parar
        gMusica.tocaMusica("musica/coldCuts - dungeon2 (pedra sagrada).ogg", loops=-1)
        limpaTela()

        print(f"Você morreu! Sua aventura termina aqui, {self.nome}...")
        print(f"{adversario.nome} se certificou disso!")

        print("-" * 50)
        print(f"Você passou {self.lvl} meses nas cavernas... Acumulou {self.xp} de conhecimento.\n")
        print("-" * 50)
        input("\nPressione ENTER para deixar esse mundo..")
        time.sleep(1)  # Aguarda um pouco antes de sair (garante que a música toca)
        sys.exit(0) 

    def olhar(self, mapa, direcao):
        olhoX = 0
        olhoY = 0
        
        match direcao:
            case "7":  # Canto superior esquerdo
                 olhoX, olhoY = self.x - 1, self.y - 1
            case "8":  # Cima
                 olhoX, olhoY = self.x, self.y - 1
            case "9":  # Canto superior direito
                 olhoX, olhoY = self.x + 1, self.y - 1
            case "4":  # Esquerda
                 olhoX, olhoY = self.x - 1, self.y
            case "6":  # Direita
                 olhoX, olhoY = self.x + 1, self.y
            case "1":  # Canto inferior esquerdo
                 olhoX, olhoY = self.x - 1, self.y + 1
            case "2":  # Baixo
                 olhoX, olhoY = self.x, self.y + 1
            case "3":  # Canto inferior direito
                 olhoX, olhoY = self.x + 1, self.y + 1
            case _:
                print("Direção inválida!")
                return
            
         # Verificar de novo se não estou me confundindo x com y.   
        print(f"Você enxerga um(a) : {mapa.matriz[olhoX][olhoY].nome}...")
        input("Pressione ENTER para continuar")

    # Jogador pesquisa aqui por palavras chave sobre itens e inimigos que enctrou em sua jornada.
    def abreDicionario(self):
        print("Você alcança por suas anotações...\n")
        pesquisa = input("Digite a palavra que procuras : ")
        print(f"Procurando por '{pesquisa}' em suas anotações...\n")

        for entrada in self.dicionario:
            # Achou a palavra, retorna sua entrada no glossário.
            # Busca por substring, pois não acredito que o jogador vai sempre lembrar do nome correto e completo.
            if pesquisa.lower() in entrada[0].lower():
                print(f"{entrada[0]} --- {entrada[1]}\n")
                input("Pressione ENTER para continuar...")
                return
            
        # Palavra ainda não conhecida, personagem precisa aprender mais!
        print(f"Palavra {pesquisa} não está em seu vocabulário...\n")
        input("Pressione ENTER para continuar...")
        return
    
# Popula a masmorra com um caminho secreto
def criaPortal(mapa):
    """Cria um portal secreto em uma posição aleatória do mapa"""
    
    # Verifica primeiro se já existe um portal no mapa
    for i in range(mapa.altura):
        for j in range(mapa.largura):
            if mapa.matriz[i][j].estado == '8':
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
        if mapa.matriz[x][y].estado == '0':
            # Coloca o portal (representado por '8' como string)
            mapa.matriz[x][y].estado = '8'
            print(f"Portal secreto criado em ({x}, {y})")
            return True
    
    # Se não encontrou aleatoriamente, faz uma busca sistemática
    print("Buscando célula vazia de forma sistemática...")
    for i in range(mapa.altura):
        for j in range(mapa.largura):
            if mapa.matriz[i][j].estado == '0':
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
    portalX, portalY = None, None
    for i in range(mapa.altura):
        for j in range(mapa.largura):
            estado = mapa.matriz[i][j].estado
            if estado == '8' :
                portalX, portalY = i, j
                break
        if portalX is not None:
            break
    
    # Se não encontrar portal
    if portalX is None:
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
    
    encontrouPortal = False
    
    # BFS
    while fila and not encontrouPortal:
        x, y = fila.popleft()
        
        # Se encontrou o portal
        if x == portalX and y == portalY:
            encontrouPortal = True
            break
        
        # Explora vizinhos
        for dx, dy in direções:
            nx, ny = x + dx, y + dy
            
            # Verifica limites
            if 0 <= nx < mapa.altura and 0 <= ny < mapa.largura:
                estadoVizinho = mapa.matriz[nx][ny].estado
                # Verifica se não visitou e é caminho livre ou portal
                if (nx, ny) not in visitados and (estadoVizinho == '0' or estadoVizinho == '8'):
                    visitados.add((nx, ny))
                    pai[(nx, ny)] = (x, y)
                    fila.append((nx, ny))
    
    # Se encontrou caminho
    if encontrouPortal:
        # Reconstrói o caminho
        caminho = []
        atual = (portalX, portalY)
        
        while pai[atual] is not None:
            caminho.append(pai[atual])
            atual = pai[atual]
        
        # Pinta o caminho em ciano (representado por '*')
        for x, y in caminho:
            # Não pinta a posição do jogador
            if not (x == player.x and y == player.y):
                mapa.matriz[x][y].estado = '*'
        
        print(f"Caminho para o portal encontrado! Distância: {len(caminho)} passos.")
        input("Pressione ENTER para continuar...")
        return True
    else:
        print("Não há caminho até o portal!")
        input("Pressione ENTER para continuar...")
        return False

# Popula masmorra com inimigos. 
# Quase idêntico ao de itens.
def populaMasmorraComInimigos(mapa, quantidadeInimigos=20, posicaoJogadorX=None, posicaoJogadorY=None):
    adversarios = 0
    tentativas = 0
    maxTentativas = quantidadeInimigos * 10

    while adversarios < quantidadeInimigos and tentativas < maxTentativas:
        tentativas += 1

        x = random.randint(0, mapa.altura - 1)
        y = random.randint(0, mapa.largura - 1)

        # Verifica se é caminho livre E não é posição do jogador
        if mapa.matriz[x][y].estado == '0' and not (x == posicaoJogadorX and y == posicaoJogadorY):
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
            # Tentando fazer 'olhar' funcionar
            mapa.matriz[x][y].nome == novoAdv.nome
            adversarios += 1

    print(f"Total de inimigos inseridos : {adversarios}")


# Função para popular a masmorra com itens
def populaMasmorraComItens(mapa, quantidadeItems=10, posicaoJogadorX=None, posicaoJogadorY=None):
    itensColocados = 0
    tentativas = 0
    maxTentativas = quantidadeItems * 10  # Evita loop infinito

    # Evitando mapas sem chaves.
    garanteChave(mapa)
    
    while itensColocados < quantidadeItems and tentativas < maxTentativas:
        tentativas += 1
        
        # Escolhe posição aleatória
        x = random.randint(0, mapa.altura - 1)
        y = random.randint(0, mapa.largura - 1)
        
        # Verifica se é caminho livre, não ocupado por mais nada, E não é posição do jogador
        if mapa.matriz[x][y].estado == '0' and not (x == posicaoJogadorX and y == posicaoJogadorY):

            # Escolhe item aleatório, importando de items do JSON
            with open("entidades/items.json", "r") as file:
                itemData = json.load(file)

            itemEscolhido = random.choice(itemData)

            novoItem = item(
                nome=itemEscolhido['nome'],
                sprite=itemEscolhido['sprite'],
                valor=itemEscolhido['valor'],
                usavel=itemEscolhido['usavel'],
                glossario=itemEscolhido['glossario'],
                x=x,
                y=y
            )
            
            # Adiciona à lista de itens do mapa e atualiza matriz
            mapa.colecionaveis.append(novoItem)
            mapa.matriz[x][y].estado = novoItem.sprite
            # Tentando fazer 'olhar' funcionar
            mapa.matriz[x][y].nome == novoItem.nome
            itensColocados += 1
    
    print(f"Total de itens colocados: {itensColocados}")

# Evitando masmorras sem chaves.
def garanteChave(mapa):
    tentativas = 0
    maxTentativas = 100

    chavesColocadas = 0

    while tentativas < maxTentativas  and chavesColocadas != 1:
        tentativas += 1

        x = random.randint(0, mapa.altura - 1)
        y = random.randint(0, mapa.largura -1)

        if mapa.matriz[x][y].estado == '0':
            chave = item(
                nome="Chave",
                sprite="C",
                valor=25,
                usavel=True,
                # Hehehehe spooky key. Just like tf2....
                glossario="Poucos conhecem deste item, outros iriam preferir não o conhecer...",
                x = x,
                y = y
            )

            mapa.colecionaveis.append(chave)
            mapa.matriz[x][y].estado = chave.sprite
            chavesColocadas += 1
            
    print("Uma chave foi colocada no mapa!")

# Função auxiliar para inicializar uma masmorra após carregá-la
def inicializaMasmorraParaJogo(mapa, player, quantidadeInimigos=20, quantidadeItems=10):
    """
    Inicializa uma masmorra após carregá-la:
    1. Limpa estados antigos (mantendo apenas '0' e '1')
    2. Encontra posição inicial válida para o jogador
    3. Posiciona o jogador no mapa
    4. Popula com inimigos e itens, evitando a posição do jogador
    
    Retorna True se bem-sucedido, False caso contrário
    """
    # Limpa estados do mapa (mantendo apenas '0' parede e '1' caminho)
    for i in range(mapa.altura):
        for j in range(mapa.largura):
            estado = mapa.matriz[i][j].estado
            if estado not in ['0', '1']:
                mapa.matriz[i][j].estado = '0'

    # Limpa inimigos e itens antigos
    mapa.adversarios = []
    mapa.colecionaveis = []

    # Encontra posição inicial válida
    if not player.encontraPosicaoInicial(mapa):
        print("Erro: Não foi possível encontrar uma posição válida na masmorra!")
        return False
    
    # Posiciona o jogador no mapa
    mapa.matriz[player.x][player.y].estado = player.sprite
    
    # Popula com inimigos (passando posição do jogador para evitar sobreposição)
    populaMasmorraComInimigos(mapa, quantidadeInimigos=quantidadeInimigos, 
                             posicaoJogadorX=player.x, posicaoJogadorY=player.y)
    
    # Popula com itens (passando posição do jogador para evitar sobreposição)
    populaMasmorraComItens(mapa, quantidadeItems=quantidadeItems, 
                          posicaoJogadorX=player.x, posicaoJogadorY=player.y)
    
    # Garante que o jogador ainda está visível no mapa após popular
    mapa.matriz[player.x][player.y].estado = player.sprite
    
    return True

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
    print("Controles: 7-8-9 (↖↑↗) | 4-6 (←→) | 1-2-3 (↙↓↘) | 'a+dir' Ataca | 'c' Caminho | 'i' Inventário | 'u' Usar item | 'p' Entrar portal | 'q' Sair")
    print("-" * 50)

# Processa input do jogador.
def processaComando(comando, player, mapa, jogando):
        if comando.lower() == 'i':
            player.checaInventario()
            input("Pressione ENTER para continuar...")
        elif comando.lower() == 't':
            print("Você... Não faz nada?")
            input("Pressione ENTER para continuar.")
        # Alterando para ataques direcionais.
        elif 'a' in comando.lower():
            print("Atacando!")
            player.ataca(mapa, comando[1])
            input("Pressione ENTER para continuar...")
        elif 'o' in comando.lower():
            player.olhar(mapa, comando[1])
        elif comando.lower() == 'u':
            print("Pressione o 'id' do item que deseja usar:")
            player.checaInventario()
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
        elif comando.lower() == 'k':
            print("Você se suicidou! What a rotten way to die...")
            input("Pressione ENTER para continuar...")
            player.lidaMorte(player)
        elif comando.lower() == 'g':
            player.abreDicionario()
        else:
            print("Comando inválido!")
            input("Pressione ENTER para continuar...")
        
        return jogando

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
    
    # Inicializa a masmorra para o jogo
    if not inicializaMasmorraParaJogo(mapa, player, quantidadeInimigos=20, quantidadeItems=10):
        print("Erro: Falha ao inicializar a masmorra!")
        return
    
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