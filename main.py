import pygame
import random
import sys
import math

pygame.init()
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width,screen_height))

color_fondo= (235,245,255)
color_boton= (116,185,255)
color_hover= (162,210,255)
color_texto= (45,52,54)
color_aciertos= (85,239,196)
white=(255,255,255)

class GameState:
    def __init__(self):
        self.state = 'MENU'
        self.difficulty = None
        self.current_stage = 0
        self.total_stages = 10
        self.stage_pool = [] #lista para generar un pool de imagenes para que no sean las mismas siempre
        self.found_difs = [] #lista para guardar los clicks correctos 
        self.difs_actuales = [] #lista de (x, y) del nivel actual
        self.circles_draw = []
        self.font_title = pygame.font.SysFont("Arial", 80, bold=True)
        self.font_btns = pygame.font.SysFont("Arial", 35 , bold=True)
        self.font_ui = pygame.font.SysFont('Arial', 25 , bold=True)
    
    def crear_boton(self,texto,y_pos,ancho=250,alto=60):
        x_pos = (screen_width // 2) - (ancho // 2)
        rect = pygame.Rect(x_pos,y_pos,ancho,alto)

        mouse_pos = pygame.mouse.get_pos()
        color = color_hover if rect.collidepoint(mouse_pos) else color_boton

        pygame.draw.rect(screen, (200, 210, 220), (rect.x+4, rect.y+4, ancho, alto), border_radius=15)
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
        self.found_difs = []
        self.circles_draw = []
        print(f"Iniciando Dificultad : {self.difficulty}")
        #Aqui se cargaria la pool y se barajaria (random.shuffle)
        #self.difs_actuales = pool[self.current_stage]['diferencias']
        

    def draw_menu(self):
        screen.fill(color_fondo)

        titulo = self.font_title.render("Proyecto", True , color_boton)
        x_titulo = (screen_width // 2) - (titulo.get_width() // 2)
        y_titulo = 120
        screen.blit(titulo,(x_titulo,y_titulo))

        self.btn_facil = self.crear_boton("Facil", 300)
        self.btn_medio = self.crear_boton("Medio", 400)
        self.btn_dificil = self.crear_boton("Dificil", 500)
        pygame.display.flip()
    
    def draw_hud(self):
        pygame.draw.rect(screen,(220,220,220), (400,30,400,20), border_radius=10)

        ancho_progreso = (self.current_stage / self.total_stages) *400
        pygame.draw.rect(screen, color_aciertos, (400,30, ancho_progreso, 20), border_radius=10)

        ui_text = self.font_ui.render(f"Dificultad: {self.difficulty} | Stage: {self.current_stage}/{self.total_stages}", True, color_texto)
        screen.blit(ui_text, (20,20))
    def draw_stage(self):
        screen.fill(white)
        self.draw_hud()

        #Aqui iria la logica para las imagenes

        for pos in self.circles_draw:
            pygame.draw.circle(screen, color_aciertos, pos, 35, 5)

        
        pygame.display.flip()
    
    def procesar_clic(self, pos):
        #dx, dy son las coordenadas de las imagenes ya sean con JSON para que no este todo en el codigo o como sea
        for i , (dx, dy) in enumerate(self.difs_actuales):
            distancia = math.sqrt((pos[0] - dx)**2 + (pos[1] - dy)**2)
            if distancia < 35 and i not in self.found_difs:
                self.found_difs.append(i)
                self.circles_to_draw.append((dx, dy))

                if len(self.found_difs) == len(self.difs_actuales):
                    self.pasar_siguiente_stage()
    def pasar_siguiente_stage(self):
        if self.current_stage < self.total_stages:
            self.current_stage +=1
            self.found_difs = []
            self.circles_draw = []
            #cargar la imagen siguiente
        else:
            self.state = 'Victory'
    
    def draw_victory(self):
        screen.fill(color_aciertos)
        texto = self.font_title.render("¡LO LOGRASTE!", True , white)
        screen.blit(texto, (screen_width//2 - texto.get_width()//2, 300))
        self.btn_volver = self.crear_boton("Menú Principal",450)
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
                game.procesar_clic(event.pos)
        elif game.state == 'Victory':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.btn_volver.collidepoint(event.pos): game.state = 'MENU'
    
    if game.state == 'MENU':
        game.draw_menu()
    elif game.state == 'PLAYING':
        game.draw_stage()
    elif game.state == 'Victory':
        game.draw_victory()

pygame.quit()
    