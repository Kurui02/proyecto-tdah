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
color_error = (255,107,107)
white=(255,255,255)

sonido_acierto = pygame.mixer.Sound("sonido/acierto.mp3")
sonido_win = pygame.mixer.Sound("sonido/win.mp3")

sonido_acierto.set_volume(0.4) 
sonido_win.set_volume(0.8)

pygame.mixer.music.load("sonido/menu.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

img_background = pygame.image.load("Imagenes/menu.jpg").convert()
img_background = pygame.transform.smoothscale(img_background, (screen_width, screen_height))

#facil : 3 imamagenes, medio 6 , 9 dificil,
# comprobar que todo funcione bien y que se vean las imagenes correspondientes en cada dificultad

class GameState:
    def __init__(self):
        self.state = 'MAIN_MENU'
        self.difficulty = None
        self.current_stage = 0
        self.total_stages = 0
        self.stage_pool = []
        self.found_difs = [] 
        self.difs_actuales = [] 
        self.circles_draw = []

        self.vidas= 3
        self.fallos_totales= 0
        self.limite_fallos = 0
        self.fallos_vida = 0

        self.zoom_factor = 0
        self.zoom_dir = 0.5

        with open("Imagenes_F.JSON","r") as imgF:
            self.all_data = json.load(imgF)["imgs"]

        self.font_title = pygame.font.SysFont("Arial", 80, bold=True)
        self.font_btns = pygame.font.SysFont("Arial", 35 , bold=True)
        self.font_ui = pygame.font.SysFont('Arial', 25 , bold=True)

        self.img_izq= None
        self.img_der= None

        self.img_corazon = pygame.image.load("Imagenes/corazon.png").convert_alpha()
        self.img_corazon = pygame.transform.smoothscale(self.img_corazon, (50, 50))

        self.img_corazon_gris = self.img_corazon.copy()
        self.img_corazon_gris.fill((60, 60, 60, 255), special_flags=pygame.BLEND_RGBA_MULT)
    
    def dibujar_degradado(self, color_inicio, color_fin):
        for y in range(0, screen_height, 2):
            r = color_inicio[0] + (color_fin[0] - color_inicio[0]) * y // screen_height
            g = color_inicio[1] + (color_fin[1] - color_inicio[1]) * y // screen_height
            b = color_inicio[2] + (color_fin[2] - color_inicio[2]) * y // screen_height
            pygame.draw.rect(screen, (r, g, b), (0, y, screen_width, 2))
    
    def crear_boton(self,texto,y_pos,ancho=300,alto=70, palpitar = False):
        x_pos = (screen_width // 2) - (ancho // 2)
        mouse_pos = pygame.mouse.get_pos()
        rect_temp = pygame.Rect(x_pos,y_pos,ancho,alto)

        if palpitar and rect_temp.collidepoint(mouse_pos):
            self.zoom_factor += 0.0005 * self.zoom_dir
            if self.zoom_factor>0.08 or self.zoom_factor <0:
                self.zoom_dir *= -1
            
            ancho += int(ancho * self.zoom_factor)
            alto += int(alto * self.zoom_factor)
            x_pos = (screen_width // 2) - (ancho // 2)
        elif palpitar:
            self.zoom_factor = 0

        rect = pygame.Rect(x_pos,y_pos,ancho,alto)
        color = color_hover if rect.collidepoint(mouse_pos) else color_boton
        sombra = (40,40,45)

        pygame.draw.rect(screen, sombra, (rect.x + 6, rect.y + 6, ancho, alto), border_radius=20)
        pygame.draw.rect(screen, color, rect, border_radius=20)
        pygame.draw.rect(screen, white, rect, 4, border_radius=20)

        text_surf = self.font_btns.render(texto, True, white)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

        return rect
    
    def draw_main_menu(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
        if img_background:
            screen.blit(img_background,(0,0))
        else:
            screen.fill(color_fondo)
        
        titulo = self.font_title.render("PROYECTO", True, white)
        sombra_tit = self.font_title.render("PROYECTO", True, (0,0,0))
        screen.blit(sombra_tit, (screen_width//2 - titulo.get_width()//2 + 5, 125))
        screen.blit(titulo, (screen_width//2 - titulo.get_width()//2, 120))

        self.btn_jugar = self.crear_boton("JUGAR", 320, palpitar=True)
        self.btn_salir = self.crear_boton("SALIR", 450)
        pygame.display.flip()
    
    def draw_diff_menu(self):
        if img_background:
            screen.blit(img_background, (0,0))
        else:
            screen.fill(color_fondo)

        subtitulo = self.font_btns.render("Selecciona la Dificultad", True, color_fondo)
        screen.blit(subtitulo, (screen_width//2 - subtitulo.get_width()//2, 200))

        self.btn_facil = self.crear_boton("FÁCIL", 300)
        self.btn_medio = self.crear_boton("MEDIO", 400)
        self.btn_dificil = self.crear_boton("DIFÍCIL", 500)
        self.btn_atras = self.crear_boton("ATRÁS", 620, ancho=150, alto=50)
        pygame.display.flip()
    
    def draw_pre_game(self):
        overlay = pygame.Surface((screen_width,screen_height))
        overlay.set_alpha(180)
        overlay.fill((20,20,25))
        screen.blit(overlay, (0,0))

        cartel_rect = pygame.Rect(screen_width//2 - 350, 150, 700, 400)
        pygame.draw.rect(screen, color_fondo, cartel_rect, border_radius=30)
        pygame.draw.rect(screen, white, cartel_rect, 5, border_radius=30)

        titulo_texto = f"MODO {self.difficulty.upper()}"
        if self.difficulty == 'Facil':
            reglas = ["- Encuentra 3 diferencias por nivel.", "- Tienes fallos INFINITOS.", "- ¡Tómate tu tiempo para practicar!"]
        elif self.difficulty == 'Medio':
            reglas = [f"- Tienes 3 vidas.", f"- Cada 7 fallos pierdes 1 vida.", f"- Máximo {self.limite_fallos} fallos totales."]
        else:
            reglas = [f"- ¡Cuidado! Tienes 3 vidas.", f"- Cada 3 fallos pierdes 1 vida.", f"- Solo {self.limite_fallos} fallos permitidos."]

        t_surf = self.font_btns.render(titulo_texto, True, color_boton)
        screen.blit(t_surf, (screen_width//2 - t_surf.get_width()//2, 180))
        for i, regla in enumerate(reglas):
            r_surf = self.font_ui.render(regla, True, white)
            screen.blit(r_surf, (cartel_rect.x + 50, 260 + (i * 40)))
        self.btn_entendido = self.crear_boton("¡ENTENDIDO!", 450, ancho=250, alto=60)
        pygame.display.flip()
    
    def set_difficulty (self, diff_level):
        self.difficulty = diff_level
        self.state = 'PRE_GAME'
        self.vidas = 3
        self.fallos_totales = 0

        if self.difficulty == 'Facil':
            self.limite_fallos = 999 
        elif self.difficulty == 'Medio':
            self.limite_fallos = 21
            self.fallos_vida = 7
        else: 
            self.limite_fallos = 9
            self.fallos_vida = 3

    def start_game (self):
        pygame.mixer.music.stop()
        self.state = 'PLAYING'
        self.current_stage = 1

        cantidad = 5 if self.difficulty == 'Facil' else 8 if self.difficulty == 'Medio' else 10
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

    def draw_hud(self):
        pygame.draw.rect(screen,(220,220,220), (400,30,400,20), border_radius=10)

        ancho_progreso = (self.current_stage / self.total_stages) *400
        pygame.draw.rect(screen, color_aciertos, (400,30, ancho_progreso, 20), border_radius=10)

        ui_text = self.font_ui.render(f"Dificultad: {self.difficulty} | Stage: {self.current_stage}/{self.total_stages}", True, color_texto)
        screen.blit(ui_text, (20,20))

        txt_fallos = f"Fallos {self.fallos_totales}/{self.limite_fallos if self.difficulty != 'Facil' else '∞'}"
        fallos_surf = self.font_ui.render(txt_fallos, True, color_texto)
        screen.blit(fallos_surf, (screen_width - 350, 20))

        for i in range(3):
            x_pos = screen_width - 180 + (i * 55)
            y_pos = 15
            if i < self.vidas:
                screen.blit(self.img_corazon, (x_pos, y_pos))
            else:
                screen.blit(self.img_corazon_gris, (x_pos, y_pos))
    
    def animacion(self):
        rect_progreso = 0
        velocidad = 20
        while rect_progreso < screen_width:
            pygame.draw.rect(screen, color_fondo, (0, 0, rect_progreso, screen_height))
            
            pygame.display.update()
            rect_progreso += velocidad
            pygame.time.Clock().tick(60)

    def draw_stage(self):
        self.dibujar_degradado((20,25,40),(60,70,90))
        self.draw_hud()

        if self.img_izq:
            screen.blit(self.img_izq, (50, 150))
            screen.blit(self.img_der, (650, 150))

        for (dx, dy) in self.circles_draw:
            pygame.draw.circle(screen, color_aciertos, (dx, dy), 35, 5)

            pygame.draw.circle(screen, color_aciertos, (dx - 600, dy), 35, 5)
        
        pygame.display.flip()
    
    def procesar_clic(self, pos):
        if not (650 <= pos[0] <= 1150 and 150 <= pos[1] <= 650):
            return

        acierto = False
        for i , (dx, dy) in enumerate(self.difs_actuales):
            distancia = math.sqrt((pos[0] - dx)**2 + (pos[1] - dy)**2)
            if distancia < 35 and i not in self.found_difs:
                self.found_difs.append(i)
                self.circles_draw.append((dx, dy))

                if sonido_acierto:
                    sonido_acierto.play()
                acierto = True
                break
        if not acierto:
            self.fallos_totales += 1
            if self.difficulty != 'Facil':
                if self.fallos_totales % self.fallos_vida == 0:
                    self.vidas -= 1
                if self.vidas <= 0 or self.fallos_totales >= self.limite_fallos:
                    self.state = 'GAME_OVER'

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
        self.dibujar_degradado((30, 80, 50), (85, 239, 196))
        texto = self.font_title.render("¡LO LOGRASTE!", True , white)
        info = self.font_ui.render(f"Superado con {self.fallos_totales} fallos y {self.vidas} vidas", True, white)
        screen.blit(texto, (screen_width//2 - texto.get_width()//2, 250))
        screen.blit(info, (screen_width//2 - info.get_width()//2, 350))
        self.btn_volver = self.crear_boton("Menú Principal",450)
        pygame.display.flip()

    def draw_game_over(self):
        self.dibujar_degradado((80, 20, 20), (255, 100, 100))
        texto = self.font_title.render("¡OH, HAS PERDIDO!", True , white)
        sub = self.font_btns.render("Vuelve a intentarlo", True, white)
        screen.blit(texto, (screen_width//2 - texto.get_width()//2, 200))
        screen.blit(sub, (screen_width//2 - sub.get_width()//2, 300))
        self.btn_reintentar = self.crear_boton("Reintentar", 400)
        self.btn_volver_menu = self.crear_boton("Menú Principal", 500)
        pygame.display.flip()

game= GameState()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
        if game.state == 'MAIN_MENU':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.btn_jugar.collidepoint(event.pos):
                    game.state = 'DIFF_MENU'
                elif game.btn_salir.collidepoint(event.pos):
                    running = False
       
        elif game.state == 'DIFF_MENU':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.btn_facil.collidepoint(event.pos): game.set_difficulty('Facil')
                elif game.btn_medio.collidepoint(event.pos): game.set_difficulty('Medio')
                elif game.btn_dificil.collidepoint(event.pos): game.set_difficulty('Dificil')
                elif game.btn_atras.collidepoint(event.pos): game.state = 'MAIN_MENU'
        
        elif game.state == 'PRE_GAME':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.btn_entendido.collidepoint(event.pos): game.start_game()

        elif game.state == 'PLAYING':
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.procesar_clic(event.pos)
        
        elif game.state == 'Victory':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.btn_volver.collidepoint(event.pos): game.state = 'MAIN_MENU'
        
        elif game.state == 'GAME_OVER':
            if event.type == pygame.MOUSEBUTTONDOWN:   
                if game.btn_reintentar.collidepoint(event.pos): 
                    game.set_difficulty(game.difficulty) 
                    game.start_game() 
                elif game.btn_volver_menu.collidepoint(event.pos): game.state = 'MAIN_MENU'
    
    if game.state == 'MAIN_MENU':
        game.draw_main_menu()
    elif game.state == 'DIFF_MENU':
        game.draw_diff_menu()
    elif game.state == 'PRE_GAME':
        game.draw_pre_game()
    elif game.state == 'PLAYING':
        game.draw_stage()
    elif game.state == 'Victory':
        game.draw_victory()
    elif game.state == 'GAME_OVER':
        game.draw_game_over()

pygame.quit()
    