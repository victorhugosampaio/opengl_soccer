from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
from playsound import playsound
import threading
import random

# Tamanho do campo
campo_largura = 700
campo_altura = 400

# Define as dimensões da janela (campo + margem)
janela_largura = campo_largura + 100
janela_altura = campo_altura + 100

# Define os limites do campo
campo_x_min = -campo_largura // 2
campo_x_max = campo_largura // 2
campo_y_min = -campo_altura // 2
campo_y_max = campo_altura // 2

# Define o tamanho do gol
gol_largura = campo_largura * 0.05
gol_altura = campo_altura * 0.5

# Define a bola
bola_x, bola_y = 0, 0
bola_velocidade_x, bola_velocidade_y = 0, 0
bola_raio = 10
bola_atrito = 0.95  # fator de atrito (diminuir a velocidade)

# Define o placar para os times da esquerda e direita
placar_esquerda, placar_direita = 0, 0

# Define as teclas WASD para movimentar a bola
teclas = {"w": False, "a": False, "s": False, "d": False}

# Define os jogadores
jogadores = []

# Define o tempo de jogo em segundos
tempo_restante = 180
fim_de_jogo = False


# Define os jogador
class Jogador:
    def __init__(self, x, y, cor=(1, 0, 0), limite=None, velocidade=3, funcao=""):
        self.x = x  # posição x
        self.y = y  # posição y
        self.cor = cor  # cor no sistema RGB
        self.tamanho = 30  # tamanho do jogador
        self.limite = limite  # área limitada onde o jogador pode se mover
        self.velocidade = velocidade  # velocidade do jogador
        self.funcao = funcao  # função do jogador A - Atacante, M - Meio-campo, Z - Zagueiro, G - Goleiro

    # Desenha o jogador no plano
    def desenhar(self):
        # Calcula proporção do círculo e triângulo dentro do tamanho total
        raio_cabeca = self.tamanho * 0.4
        altura_triangulo = self.tamanho * 0.6

        # Cabeça do jogador
        glColor3f(1, 1, 0)
        glBegin(GL_POLYGON)
        num_segmentos = 50
        for i in range(num_segmentos):
            angulo = 2 * math.pi * i / num_segmentos
            glVertex2f(self.x + math.cos(angulo) * raio_cabeca,
                       self.y + math.sin(angulo) * raio_cabeca)
        glEnd()

        # Corpo do jogador
        glColor3f(*self.cor)
        glBegin(GL_TRIANGLES)
        glVertex2f(self.x - raio_cabeca, self.y - raio_cabeca)  # ponta esquerda do triângulo
        glVertex2f(self.x + raio_cabeca, self.y - raio_cabeca)  # ponta direita do triângulo
        glVertex2f(self.x, self.y - raio_cabeca - altura_triangulo)  # ponta inferior
        glEnd()

        # desenha o caracter que representa a função do jogador sobre a cabeça
        glColor3f(0, 0, 0)  # texto em preto para melhor contraste
        glRasterPos2f(self.x - 5, self.y - 5)
        for caractere in self.funcao:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(caractere))

    # Movimenta o jogador em direção da bola
    def seguir_bola(self, todos_jogadores):
        distancia_x = bola_x - self.x
        distancia_y = bola_y - self.y
        distancia = math.hypot(distancia_x, distancia_y)  # calcula a distância euclidiana até a bola

        if distancia > 1:
            distancia_x /= distancia  # normaliza o vetor direção em x
            distancia_y /= distancia  # normaliza o vetor direção em y

            novo_x = self.x + distancia_x * self.velocidade  # calcula a nova posição em x
            novo_y = self.y + distancia_y * self.velocidade  # calcula a nova posição em y

            if self.limite:
                x_min, x_max, y_min, y_max = self.limite

                # garante que o jogador ficará entre os limites obrigatoriamente
                novo_x = max(x_min, min(x_max, novo_x))
                novo_y = max(y_min, min(y_max, novo_y))

            self.x = novo_x
            self.y = novo_y

            if self.funcao != "G":
                self.evitar_travamento(todos_jogadores)

    # Evita que os jogadores travem ao colidir
    def evitar_travamento(self, todos_jogadores):
        for jogador in todos_jogadores:
            if jogador is self or jogador.funcao == "G":  # ignora colisão consigo mesmo e com goleiro
                continue

            distancia_x = self.x - jogador.x
            distancia_y = self.y - jogador.y
            distancia = math.hypot(distancia_x, distancia_y)  # calcula distância entre os jogadores
            distancia_min = self.tamanho + jogador.tamanho

            if distancia_min > distancia > 0:  # se houver colisão
                sobreposicao = distancia_min - distancia
                ajuste_x = distancia_x / distancia * sobreposicao / 2
                ajuste_y = distancia_y / distancia * sobreposicao / 2

                self.x += ajuste_x
                self.y += ajuste_y

                jogador.x -= ajuste_x
                jogador.y -= ajuste_y

    # Chuta a bola em direção ao gol adversário
    def chutar_bola(self, potencia=1.5):
        global bola_x, bola_y, bola_velocidade_x, bola_velocidade_y
        distancia_x = bola_x - self.x
        distancia_y = bola_y - self.y
        distancia = math.hypot(distancia_x, distancia_y)  # cálculo da distância do jogador até a bola

        if distancia < self.tamanho + bola_raio:
            if self.funcao == "G":  # goleiro chuta no sentido oposto do movimento
                bola_velocidade_x = -bola_velocidade_x * potencia
                bola_velocidade_y = -bola_velocidade_y * potencia

            else:  # jogador de linha chuta em direção ao gol adversário
                alvo_x = campo_x_max if self.cor == (0, 0, 1) else campo_x_min
                alvo_y = 0

                direcao_x = alvo_x - bola_x
                direcao_y = alvo_y - bola_y

                norma = math.hypot(direcao_x, direcao_y)

                if norma == 0:
                    norma = 0.1  # evita divisão por zero

                bola_velocidade_x += direcao_x / norma * potencia
                bola_velocidade_y += direcao_y / norma * potencia

    # Posiciona o jogador aleatoriamente dentro da área permitida
    def posicionar(self):
        x_min, x_max, y_min, y_max = self.limite

        self.x = random.uniform(x_min + 20, x_max - 20)
        self.y = random.uniform(y_min + 20, y_max - 20)


def criar_jogadores():
    global jogadores
    jogadores = []

    metade_campo_esquerdo = campo_x_min / 2  # metade do campo esquerdo
    metade_campo_direito = campo_x_max / 2  # metade do campo direito

    cor_azul = (0, 0, 1)  # time esquerdo
    cor_verde = (0, 1, 0)  # time direito

    # Time Esquerdo

    # O goleiro se move apenas no gol
    jogadores.append(Jogador(0, 0, cor=cor_azul,
                             limite=(campo_x_min, campo_x_min + gol_largura, -gol_altura / 2, gol_altura / 2),
                             funcao="G"))

    # O zagueiro se move do seu gol até a metade do seu campo
    jogadores.append(Jogador(0, 0, cor=cor_azul,
                             limite=(campo_x_min + gol_largura, metade_campo_esquerdo, campo_y_min, campo_y_max),
                             funcao="Z"))

    # O meio-campo se move da metade do seu campo até a metade do campo adversário
    jogadores.append(Jogador(0, 0, cor=cor_azul,
                             limite=(metade_campo_esquerdo, metade_campo_direito, campo_y_min, campo_y_max),
                             funcao="M"))

    # O atacante se move da metade do campo adversário até o gol adversário
    jogadores.append(Jogador(0, 0, cor=cor_azul,
                             limite=(metade_campo_direito, campo_x_max - gol_largura, campo_y_min, campo_y_max),
                             funcao="A"))

    # Time Direito
    jogadores.append(Jogador(0, 0, cor=cor_verde,
                             limite=(campo_x_max - gol_largura, campo_x_max, -gol_altura / 2, gol_altura / 2),
                             funcao="G"))

    jogadores.append(Jogador(0, 0, cor=cor_verde,
                             limite=(metade_campo_direito, campo_x_max - gol_largura, campo_y_min, campo_y_max),
                             funcao="Z"))

    jogadores.append(Jogador(0, 0, cor=cor_verde,
                             limite=(metade_campo_esquerdo, metade_campo_direito, campo_y_min, campo_y_max),
                             funcao="M"))

    jogadores.append(Jogador(0, 0, cor=cor_verde,
                             limite=(campo_x_min + gol_largura, metade_campo_esquerdo, campo_y_min, campo_y_max),
                             funcao="A"))

    for jogador in jogadores:
        jogador.posicionar()


def desenhar_campo():
    # Desenha o contorno do campo
    glColor3f(0, 1, 0)  # verde
    glBegin(GL_LINE_LOOP)
    glVertex2f(campo_x_min, campo_y_min)
    glVertex2f(campo_x_max, campo_y_min)
    glVertex2f(campo_x_max, campo_y_max)
    glVertex2f(campo_x_min, campo_y_max)
    glEnd()

    # Linha do meio de campo
    glBegin(GL_LINES)
    glVertex2f(0, campo_y_min)
    glVertex2f(0, campo_y_max)
    glEnd()

    # Limites do gol esquerdo
    glBegin(GL_LINE_LOOP)
    glVertex2f(campo_x_min, -gol_altura / 2)
    glVertex2f(campo_x_min + gol_largura, -gol_altura / 2)
    glVertex2f(campo_x_min + gol_largura, gol_altura / 2)
    glVertex2f(campo_x_min, gol_altura / 2)
    glEnd()

    # Limites do gol direito
    glBegin(GL_LINE_LOOP)
    glVertex2f(campo_x_max, -gol_altura / 2)
    glVertex2f(campo_x_max - gol_largura, -gol_altura / 2)
    glVertex2f(campo_x_max - gol_largura, gol_altura / 2)
    glVertex2f(campo_x_max, gol_altura / 2)
    glEnd()

    # Círculo central
    glColor3f(1, 1, 1)  # branco
    raio_circulo = campo_altura * 0.25  # 25% da altura do campo
    glBegin(GL_LINE_LOOP)
    for i in range(100):
        angulo = 2 * math.pi * i / 100
        glVertex2f(raio_circulo * math.cos(angulo), raio_circulo * math.sin(angulo))
    glEnd()


# Desenha a bola
def desenhar_bola():
    glColor3f(1, 1, 1)  # cor branca
    glBegin(GL_POLYGON)

    for i in range(100):
        angulo = 2 * math.pi * i / 100
        glVertex2f(bola_x + math.cos(angulo) * bola_raio, bola_y + math.sin(angulo) * bola_raio)
    glEnd()


# Atualiza a posição da bola
def atualizar_bola():
    global bola_x, bola_y, bola_velocidade_x, bola_velocidade_y, placar_esquerda, placar_direita
    bola_x += bola_velocidade_x  # aplica velocidade em x
    bola_y += bola_velocidade_y  # aplica velocidade em y
    bola_velocidade_x *= bola_atrito  # aplica atrito para reduzir velocidade
    bola_velocidade_y *= bola_atrito

    # colisão com limites do campo
    if bola_x - bola_raio < campo_x_min:
        bola_x = campo_x_min + bola_raio
        bola_velocidade_x *= -1

    if bola_x + bola_raio > campo_x_max:
        bola_x = campo_x_max - bola_raio
        bola_velocidade_x *= -1

    if bola_y - bola_raio < campo_y_min:
        bola_y = campo_y_min + bola_raio
        bola_velocidade_y *= -1

    if bola_y + bola_raio > campo_y_max:
        bola_y = campo_y_max - bola_raio
        bola_velocidade_y *= -1

    # verifica se houve gol
    if bola_x - bola_raio <= campo_x_min and abs(bola_y) <= gol_altura / 2:
        threading.Thread(target=lambda: playsound("sons/gol.mp3")).start()  # Toca o som de gol
        placar_direita += 1
        bola_x, bola_y = 0, 0
        bola_velocidade_x, bola_velocidade_y = 0, 0

    if bola_x + bola_raio >= campo_x_max and abs(bola_y) <= gol_altura / 2:
        threading.Thread(target=lambda: playsound("sons/gol.mp3")).start()  # Toca o som de gol
        placar_esquerda += 1
        bola_x, bola_y = 0, 0
        bola_velocidade_x, bola_velocidade_y = 0, 0


# Atualiza a posição dos jogadores
def atualizar_jogadores():
    for jogador in jogadores:
        jogador.seguir_bola(jogadores)
        jogador.chutar_bola()


# Callback de tecla pressionada
def tecla_pressionada(key, x, y):
    if key.decode("utf-8") in teclas:
        teclas[key.decode("utf-8")] = True


# Callback de tecla liberada
def tecla_liberada(key, x, y):
    if key.decode("utf-8") in teclas:
        teclas[key.decode("utf-8")] = False


# Função de callback do jogo
def jogo(distancia=1):
    global bola_velocidade_y, bola_velocidade_x

    if teclas["w"]:
        bola_velocidade_y += distancia

    if teclas["s"]:
        bola_velocidade_y -= distancia

    if teclas["a"]:
        bola_velocidade_x -= distancia

    if teclas["d"]:
        bola_velocidade_x += distancia

    atualizar_bola()
    atualizar_jogadores()
    glutPostRedisplay()


# Cronometro do jogo
def cronometro():
    global tempo_restante, fim_de_jogo

    if fim_de_jogo:
        return

    if tempo_restante > 0:
        tempo_restante -= 1
        threading.Timer(1, cronometro).start()
    else:
        fim_de_jogo = True
        threading.Thread(target=lambda: playsound("sons/apito.mp3")).start()


# Desenha o canvas
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    desenhar_campo()
    desenhar_bola()

    for jogador in jogadores:
        jogador.desenhar()

    # desenha o placar
    glColor3f(1, 1, 0)
    glRasterPos2f(-20, campo_y_max + 25)
    for caractere in f"{placar_esquerda} - {placar_direita}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(caractere))

    # desenha o timer
    minutos = tempo_restante // 60
    segundos = tempo_restante % 60
    glRasterPos2f(-15, campo_y_max + 5)
    for caractere in f"{minutos:02d}:{segundos:02d}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(caractere))

    glutSwapBuffers()


# Mostra o vencedor da partida
def mostrar_vencedor():
    if placar_esquerda > placar_direita:
        linhas = ["Fim de Jogo!", "Time Azul venceu!"]
    elif placar_direita > placar_esquerda:
        linhas = ["Fim de Jogo!", "Time Verde venceu!"]
    else:
        linhas = ["Fim de Jogo!", "Empate!"]

    glColor3f(1, 1, 1)

    for i, linha in enumerate(linhas):
        largura = sum([glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in linha])
        pos_x = -largura / 2  # centraliza horizontalmente
        pos_y = 20 * (len(linhas) - i - 1) - 15  # desenha da parte superior para baixo
        glRasterPos2f(pos_x, pos_y)
        for c in linha:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    glutSwapBuffers()


# Inicializa o canvas
def inicializar():
    glClearColor(0, 0.5, 0, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-janela_largura // 2, janela_largura // 2, -janela_altura // 2, janela_altura // 2)


# Define a thread do jogo
def thread(value):
    if fim_de_jogo:
        mostrar_vencedor()
    else:
        jogo()  # atualiza bola e jogadores
        glutPostRedisplay()
        glutTimerFunc(30, thread, 1)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(janela_largura, janela_altura)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Jogo de Futebol 2D")
    inicializar()
    glutDisplayFunc(display)
    glutKeyboardFunc(tecla_pressionada)
    glutKeyboardUpFunc(tecla_liberada)
    glutTimerFunc(30, thread, 1)
    criar_jogadores()
    cronometro()
    glutMainLoop()


if __name__ == "__main__":
    main()


