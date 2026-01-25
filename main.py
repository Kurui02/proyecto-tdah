import pygame
import random
import sys

pygame.init()
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width,screen_height))

color_fondo= (30,30,50)
color_boton= (70,70,150)
color_hover= (100,100,250)
white=(255,255,255)

class GameState:
    def __init__(self):
        self.state = 'MENU'
        self.difficulty = None
        self.current_stage = 0
        self.stage_pool = [] #lista para generar un pool de imagenes para que no sean las mismas siempre
        self.found_difs = [] #lista para guardar los clicks correctos 
        self.font_title = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_btns = pygame.font.SysFont("Arial", 30 , bold=True)
    
    def crear_boton(self,texto,y_pos,ancho=250,alto=60):
        x_pos = (screen_width // 2) - (ancho // 2)
        rect = pygame.Rect(x_pos,y_pos,ancho,alto)

        mouse_pos = pygame.mouse.get_pos()
        color = color_hover if rect.collidepoint(mouse_pos) else color_boton

        pygame.draw.rect(screen,color,rect, border_radius=15)
        pygame.draw.rect(screen,white,rect,3,border_radius=15)

        text_surf = self.font_btns.render(texto, True, white)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf,text_rect)

        return rect
    
    def start_game (self, diff_level):
        self.difficulty = diff_level
        self.state = 'PLAYING'
        self.current_stage = 1
        print(f"Iniciando Dificultad : {self.difficulty}")
        #Aqui se cargaria la pool y se barajaria (random.shuffle)

    def draw_menu(self):
        screen.fill(color_fondo)

        titulo = self.font_title.render("Proyecto", True , (0,200,255))
        x_titulo = (screen_width // 2) - (titulo.get_width() // 2)
        y_titulo = 100
        screen.blit(titulo,(x_titulo,y_titulo))

        self.btn_facil = self.crear_boton("Facil", 250)
        self.btn_medio = self.crear_boton("Medio", 350)
        self.btn_dificil = self.crear_boton("Dificil", 450)
        pygame.display.flip()
    
    def draw_stage(self):
        screen.fill((255,255,255))
        #Aqui iria la logica para las imagenes

        ui_text = self.font_btns.render(f"Dificultad: {self.difficulty} | Stage: {self.current_stage}/10", True, (50, 50, 50))
        screen.blit(ui_text, (20,20))
        pygame.display.flip()

game= GameState()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
        if game.state == 'MENU':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.btn_facil.collidepoint(event.pos):
                    game.start_game('Facil')
                elif game.btn_medio.collidepoint(event.pos):
                    game.start_game('Medio')
                elif game.btn_dificil.collidepoint(event.pos):
                    game.start_game('Dificil')
       
        elif game.state == 'PLAYING':
            if event.type == pygame.MOUSEBUTTONDOWN:
                #logica de la deteccion de las diferencias 
                pass
    
    if game.state == 'MENU':
        game.draw_menu()
    elif game.state == 'PLAYING':
        game.draw_stage()

pygame.quit()
    