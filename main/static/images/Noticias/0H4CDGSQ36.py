import pygame
import time
import random
 
pygame.init()
 
# Define los colores que se utilizarán en el juego
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
 
# Define el tamaño de la pantalla y la velocidad de actualización
display_width = 800
display_height = 600
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Culebrita')
clock = pygame.time.Clock()
 
# Define el tamaño de los bloques y la velocidad de la serpiente
block_size = 10
FPS = 30
 
# Define la fuente para la puntuación
font = pygame.font.SysFont(None, 25)
 
def message_to_screen(msg, color):
    """
    Función para imprimir un mensaje en la pantalla
    """
    screen_text = font.render(msg, True, color)
    gameDisplay.blit(screen_text, [display_width/2, display_height/2])
 
def gameLoop():
    """
    Función principal del juego
    """
    gameExit = False
    gameOver = False
 
    # Define la posición inicial de la serpiente
    lead_x = display_width/2
    lead_y = display_height/2
    lead_x_change = 0
    lead_y_change = 0
 
    # Genera la posición aleatoria de la comida
    randAppleX = round(random.randrange(0, display_width - block_size)/10.0)*10.0
    randAppleY = round(random.randrange(0, display_height - block_size)/10.0)*10.0
 
    while not gameExit:
        while gameOver == True:
            gameDisplay.fill(white)
            message_to_screen("Presiona C para jugar de nuevo o Q para salir", red)
            pygame.display.update()
 
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        gameExit = True
                        gameOver = False
                    if event.key == pygame.K_c:
                        gameLoop()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    lead_x_change = -block_size
                    lead_y_change = 0
                elif event.key == pygame.K_RIGHT:
                    lead_x_change = block_size
                    lead_y_change = 0
                elif event.key == pygame.K_UP:
                    lead_y_change = -block_size
                    lead_x_change = 0
                elif event.key == pygame.K_DOWN:
                    lead_y_change = block_size
                    lead_x_change = 0
 
        # Verifica si la serpiente ha golpeado la pared
        if lead_x >= display_width or lead_x < 0 or lead_y >= display_height or lead_y < 0:
            gameOver = True
 
        # Actualiza la posición de la serpiente
        lead_x += lead_x_change
        lead_y += lead_y_change
 
        # Dibuja la comida y la serpiente en la pantalla
        gameDisplay.fill(white)
        pygame.draw.rect(gameDisplay, red, [randAppleX, randAppleY, block_size, block_size])
        pygame.draw.rect(gameDisplay, black, [lead_x, lead_y, block_size, block_size])
        pygame