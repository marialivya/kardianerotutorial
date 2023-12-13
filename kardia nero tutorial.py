import pygame
import sys
import random
import math

pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600
FPS = 60
AZUL_MAR = (13, 59, 72)
BRANCO = (255, 255, 255)

# Classe do jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("personagem.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (LARGURA_TELA // 2, ALTURA_TELA // 2)
        self.velocidade = 10
        self.vidas = 3
        self.pode_atacar = True
        self.tempo_recarga = 500
        self.tempo_ultimo_ataque = 0  # Adicionado para corrigir a referência antes da atribuição

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_d] and self.rect.right < LARGURA_TELA:
            self.rect.x += self.velocidade
        if teclas[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.velocidade
        if teclas[pygame.K_s] and self.rect.bottom < ALTURA_TELA:
            self.rect.y += self.velocidade

        if not self.pode_atacar:
            agora = pygame.time.get_ticks()
            if agora - self.tempo_ultimo_ataque >= self.tempo_recarga:
                self.pode_atacar = True


# Classe do inimigo
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, jogador):
        super().__init__()
        self.image = pygame.image.load("inimigo.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 50))
        self.rect = self.image.get_rect()
        self.velocidade = random.randrange(1, 3)
        self.jogador = jogador
        self.vidas = 2

        posicoes_iniciais = [
            (0, random.randrange(0, ALTURA_TELA)),
            (LARGURA_TELA, random.randrange(0, ALTURA_TELA)),
            (random.randrange(0, LARGURA_TELA), 0),
            (random.randrange(0, LARGURA_TELA), ALTURA_TELA),
        ]
        self.rect.topleft = random.choice(posicoes_iniciais)

    def update(self):
        direcao_x = self.jogador.rect.x - self.rect.x
        direcao_y = self.jogador.rect.y - self.rect.y
        comprimento_vetor = ((direcao_x ** 2) + (direcao_y ** 2)) ** 0.5

        if comprimento_vetor > 0:
            direcao_x /= comprimento_vetor
            direcao_y /= comprimento_vetor

        self.rect.x += direcao_x * self.velocidade
        self.rect.y += direcao_y * self.velocidade

        if (
            self.rect.right < 0
            or self.rect.left > LARGURA_TELA
            or self.rect.bottom < 0
            or self.rect.top > ALTURA_TELA
        ):
            posicoes_iniciais = [
                (0, random.randrange(0, ALTURA_TELA)),
                (LARGURA_TELA, random.randrange(0, ALTURA_TELA)),
                (random.randrange(0, LARGURA_TELA), 0),
                (random.randrange(0, LARGURA_TELA), ALTURA_TELA),
            ]
            self.rect.topleft = random.choice(posicoes_iniciais)

# Classe do ataque
class Ataque(pygame.sprite.Sprite):
    def __init__(self, jogador):
        super().__init__()
        self.image = pygame.image.load("ataque.png").convert_alpha()
        self.rect = self.image.get_rect(center=jogador.rect.center)
        self.alcance = 500

    def update(self):
        pass


tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Kardia Nero')
relogio = pygame.time.Clock()

# Carregar imagem de fundo e redimensioná-la
fundo_original = pygame.image.load("fundo.png").convert()
fundo = pygame.transform.scale(fundo_original, (LARGURA_TELA, ALTURA_TELA))

# Grupos de sprites
todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
ataques = pygame.sprite.Group()
jogador = Jogador()
todos_sprites.add(jogador)

# Adicionar texto
fonte = pygame.font.SysFont(None, 30)
texto1 = fonte.render("Use W A S D para se movimentar", True, AZUL_MAR)
texto2 = fonte.render("Use ESPAÇO para atacar", True, AZUL_MAR)

# loop principal
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and jogador.pode_atacar:
                ataque = Ataque(jogador)
                todos_sprites.add(ataque)
                ataques.add(ataque)
                jogador.pode_atacar = False
                jogador.tempo_ultimo_ataque = pygame.time.get_ticks()

    todos_sprites.update()

    colisoes = pygame.sprite.spritecollide(jogador, inimigos, False)
    if colisoes:
        jogador.vidas -= 1
        if jogador.vidas <= 0:
            rodando = False

    for ataque in ataques:
        colisoes_inimigo = pygame.sprite.spritecollide(ataque, inimigos, True)
        for inimigo in colisoes_inimigo:
            inimigo.vidas -= 1
            if inimigo.vidas <= 0:
                inimigos.remove(inimigo)
                todos_sprites.remove(inimigo)

        agora = pygame.time.get_ticks()
        if agora - jogador.tempo_ultimo_ataque >= 200:
            ataques.remove(ataque)
            todos_sprites.remove(ataque)

    agora = pygame.time.get_ticks()
    if not jogador.pode_atacar and agora - jogador.tempo_ultimo_ataque >= jogador.tempo_recarga:
        jogador.pode_atacar = True

    if random.randrange(1000) < 7:
        inimigo = Inimigo(jogador)
        todos_sprites.add(inimigo)
        inimigos.add(inimigo)

    tela.blit(fundo, (0, 0))  # Desenha o fundo
    todos_sprites.draw(tela)

    # Desenha texto no canto inferior esquerdo
    tela.blit(texto1, (15, ALTURA_TELA - 50))
    tela.blit(texto2, (15, ALTURA_TELA - 25))

    pygame.display.flip()

    relogio.tick(FPS)

pygame.quit()
sys.exit()