import pygame
import random
import sys
import math
import json

pygame.init()
pygame.mixer.init()
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width,screen_height))

color_fondo= (55,55,60)
color_boton= (160,196,255)
color_hover= (160,246,255)
color_texto= (240,240,240)
color_aciertos= (85,239,196)
white=(255,255,255)

sonido_acierto = pygame.mixer.Sound("sonido/acierto.mp3")
sonido_win = pygame.mixer.Sound("sonido/win.mp3")

class GameState:
    def __init__(self):
        self.state = 'MENU'
        self.difficulty = None
        self.current_stage = 0
        self.total_stages = 0
        self.stage_pool = []
        self.found_difs = [] 
        self.difs_actuales = [] 
        self.circles_draw = []

        with open("Imagenes_F.JSON","r") as imgF:
            self.all_data = json.load(imgF)["imgs"]

        self.font_title = pygame.font.SysFont("Arial", 80, bold=True)
        self.font_btns = pygame.font.SysFont("Arial", 35 , bold=True)
        self.font_ui = pygame.font.SysFont('Arial', 25 , bold=True)

        self.img_izq= None
        self.img_der= None
    
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

        if self.difficulty == 'Facil':
            cantidad = 5
        elif self.difficulty == 'Medio':
            cantidad = 8
        else: 
            cantidad = 10
        
        pool_total = len(self.all_data)
        n_selecionar = min(cantidad, pool_total)

        self.stage_pool = random.sample(self.all_data, n_selecionar)
        self.total_stages = len(self.stage_pool)

        self.cargar_stage_actual()

    def cargar_stage_actual(self):
        self.found_difs = []
        self.circles_draw = []
        self.difs_actuales = []

        id = self.current_stage - 1
        nivel_data = list(self.stage_pool[id].values())[0]

        path_izq = nivel_data["img_izq"] + ".png" if "." not in nivel_data["img_izq"] else nivel_data["img_izq"]
        path_der = nivel_data["img_der"] + ".png" if "." not in nivel_data["img_der"] else nivel_data["img_der"]

        self.img_izq = pygame.image.load(path_izq).convert_alpha()
        self.img_der = pygame.image.load(path_der).convert_alpha()

        self.img_izq = pygame.transform.smoothscale(self.img_izq,(500,500))
        self.img_der = pygame.transform.smoothscale(self.img_der,(500,500))

        for key in ["punto1", "punto2", "punto3"]:
            px, py = nivel_data[key]
            self.difs_actuales.append((650 + px , 150 + py))

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
    
    def animacion(self):
        rect_progreso = 0
        velocidad = 20
        while rect_progreso < screen_width:
            pygame.draw.rect(screen, color_fondo, (0, 0, rect_progreso, screen_height))
            
            pygame.display.update()
            rect_progreso += velocidad
            pygame.time.Clock().tick(60)

    def draw_stage(self):
        screen.fill(color_fondo)
        self.draw_hud()

        
        if self.img_izq:
            screen.blit(self.img_izq, (50, 150))
            screen.blit(self.img_der, (650, 150))

        for (dx, dy) in self.circles_draw:
            pygame.draw.circle(screen, color_aciertos, (dx, dy), 35, 5)

            pygame.draw.circle(screen, color_aciertos, (dx - 600, dy), 35, 5)

        
        pygame.display.flip()
    
    def procesar_clic(self, pos):
        for i , (dx, dy) in enumerate(self.difs_actuales):
            distancia = math.sqrt((pos[0] - dx)**2 + (pos[1] - dy)**2)
            if distancia < 35 and i not in self.found_difs:
                self.found_difs.append(i)
                self.circles_draw.append((dx, dy))

                if sonido_acierto:
                    sonido_acierto.play()

                if len(self.found_difs) == len(self.difs_actuales):
                    self.draw_stage()
                    pygame.time.delay(500)
                    self.animacion()
                    self.pasar_siguiente_stage()
    def pasar_siguiente_stage(self):
        if self.current_stage < self.total_stages:
            self.current_stage +=1
            self.cargar_stage_actual()
        else:
            if sonido_win:
                sonido_win.play()
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
    