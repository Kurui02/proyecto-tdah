import pygame
import random
import sys
import math
import json
from pathlib import Path
from enfocate import GameBase, GameMetadata

Dir = Path(__file__).resolve().parent.parent

color_fondo = (55, 55, 60)
color_boton = (160, 196, 255)
color_hover = (160, 246, 255)
color_texto = (240, 240, 240)
color_aciertos = (85, 239, 196)
color_error = (255, 107, 107)
white = (255, 255, 255)

class MiJuego(GameBase):
    def __init__(self):
        meta = GameMetadata(
            title="Encuentra las diferencias",
            description="Juego de concentración de encontrar diferencias",
            authors=["Marcelys Tebres", "Jose Areinamo", "Frednali Fernandez", "Joswar Ramirez"],
            group_number=3
        )
        super().__init__(meta)
    
        self.state = 'MAIN_MENU'
        self.difficulty = None
        self.current_stage = 0
        self.total_stages = 0
        self.stage_pool = []
        self.found_difs = [] 
        self.difs_actuales = [] 
        self.circles_draw = []

        self.vidas = 3
        self.fallos_totales = 0
        self.limite_fallos = 0
        self.fallos_vida = 0

        self.zoom_factor = 0
        self.zoom_dir = 0.5
        
        self.mouse_was_pressed = False

        ruta_f = Dir / "Imagenes" / "Imagenes_F.JSON"
        ruta_m = Dir / "Imagenes" / "Imagenes_M.JSON"
        ruta_d = Dir / "Imagenes" / "Imagenes_D.JSON"

        with open(ruta_f, "r") as imgF: self.all_data_F = json.load(imgF)["imgs"]
        with open(ruta_m, "r") as imgM: self.all_data_M = json.load(imgM)["imgs"]
        with open(ruta_d, "r") as imgD: self.all_data_D = json.load(imgD)["imgs"]

        self.btn_jugar = pygame.Rect(0,0,0,0)
        self.btn_salir = pygame.Rect(0,0,0,0)
        self.btn_facil = pygame.Rect(0,0,0,0)
        self.btn_medio = pygame.Rect(0,0,0,0)
        self.btn_dificil = pygame.Rect(0,0,0,0)
        self.btn_atras = pygame.Rect(0,0,0,0)
        self.btn_entendido = pygame.Rect(0,0,0,0)
        self.btn_volver = pygame.Rect(0,0,0,0)
        self.btn_reintentar = pygame.Rect(0,0,0,0)
        self.btn_volver_menu = pygame.Rect(0,0,0,0)

    def on_start(self):
        self.screen_width = self.surface.get_width()
        self.screen_height = self.surface.get_height()

        self.font_title = pygame.font.SysFont("Arial", 80, bold=True)
        self.font_btns = pygame.font.SysFont("Arial", 35, bold=True)
        self.font_ui = pygame.font.SysFont('Arial', 25, bold=True)

        self.img_izq = None
        self.img_der = None

        path_titulo = Dir / "Imagenes" / "Titulo.png"
        path_menu_bg = Dir / "Imagenes" / "menu.jpg"
        path_corazon = Dir / "Imagenes" / "corazon.png"

        self.img_title = pygame.image.load(str(path_titulo)).convert_alpha()
        img_bg = pygame.image.load(str(path_menu_bg)).convert()
        self.img_background = pygame.transform.smoothscale(img_bg, (self.screen_width, self.screen_height))

        corazon = pygame.image.load(str(path_corazon)).convert_alpha()
        self.img_corazon = pygame.transform.smoothscale(corazon, (50, 50))
        self.img_corazon_gris = self.img_corazon.copy()
        self.img_corazon_gris.fill((60, 60, 60, 255), special_flags=pygame.BLEND_RGBA_MULT)

        acierto = Dir / "sonido" / "acierto.mp3"
        win = Dir / "sonido" / "win.mp3"
        error = Dir / "sonido" / "Error.mp3"
        musica = Dir / "sonido" / "menu.mp3"

        self.sonido_acierto = pygame.mixer.Sound(str(acierto))
        self.sonido_win = pygame.mixer.Sound(str(win))
        self.sonido_error = pygame.mixer.Sound(str(error))

        self.sonido_error.set_volume(0.3)
        self.sonido_acierto.set_volume(0.4) 
        self.sonido_win.set_volume(0.8)

        pygame.mixer.music.load(str(musica))
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

    def update(self, dt: float):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        just_clicked = mouse_pressed and not self.mouse_was_pressed
        self.mouse_was_pressed = mouse_pressed

        if just_clicked:
            pos = pygame.mouse.get_pos()

            if self.state == 'MAIN_MENU':
                if self.btn_jugar.collidepoint(pos): self.state = 'DIFF_MENU'
                elif self.btn_salir.collidepoint(pos): sys.exit() 
            
            elif self.state == 'DIFF_MENU':
                if self.btn_facil.collidepoint(pos): self.set_difficulty('Facil')
                elif self.btn_medio.collidepoint(pos): self.set_difficulty('Medio')
                elif self.btn_dificil.collidepoint(pos): self.set_difficulty('Dificil')
                elif self.btn_atras.collidepoint(pos): self.state = 'MAIN_MENU'
            
            elif self.state == 'PRE_GAME':
                if self.btn_entendido.collidepoint(pos): self.start_game()

            elif self.state == 'PLAYING':
                self.procesar_clic(pos)
            
            elif self.state == 'Victory':
                if self.btn_volver.collidepoint(pos): self.state = 'MAIN_MENU'
            
            elif self.state == 'GAME_OVER':
                if self.btn_reintentar.collidepoint(pos): 
                    self.set_difficulty(self.difficulty) 
                    self.start_game() 
                elif self.btn_volver_menu.collidepoint(pos): self.state = 'MAIN_MENU'

    def draw(self):
        if self.state == 'MAIN_MENU': self.draw_main_menu()
        elif self.state == 'DIFF_MENU': self.draw_diff_menu()
        elif self.state == 'PRE_GAME': self.draw_pre_game()
        elif self.state == 'PLAYING': self.draw_stage()
        elif self.state == 'Victory': self.draw_victory()
        elif self.state == 'GAME_OVER': self.draw_game_over()
    
    def dibujar_degradado(self, color_inicio, color_fin):
        for y in range(0, self.screen_height, 2):
            r = color_inicio[0] + (color_fin[0] - color_inicio[0]) * y // self.screen_height
            g = color_inicio[1] + (color_fin[1] - color_inicio[1]) * y // self.screen_height
            b = color_inicio[2] + (color_fin[2] - color_inicio[2]) * y // self.screen_height
            pygame.draw.rect(self.surface, (r, g, b), (0, y, self.screen_width, 2))
    
    def crear_boton(self, texto, y_pos, ancho=300, alto=70, palpitar=False):
        x_pos = (self.screen_width // 2) - (ancho // 2)
        mouse_pos = pygame.mouse.get_pos()
        rect_temp = pygame.Rect(x_pos, y_pos, ancho, alto)

        if palpitar and rect_temp.collidepoint(mouse_pos):
            self.zoom_factor += 0.005 * self.zoom_dir
            if self.zoom_factor > 0.08 or self.zoom_factor < 0: self.zoom_dir *= -1
            ancho += int(ancho * self.zoom_factor)
            alto += int(alto * self.zoom_factor)
            x_pos = (self.screen_width // 2) - (ancho // 2)
        elif palpitar:
            self.zoom_factor = 0

        rect = pygame.Rect(x_pos, y_pos, ancho, alto)
        color = color_hover if rect.collidepoint(mouse_pos) else color_boton
        sombra = (40, 40, 45)

        pygame.draw.rect(self.surface, sombra, (rect.x + 6, rect.y + 6, ancho, alto), border_radius=20)
        pygame.draw.rect(self.surface, color, rect, border_radius=20)
        pygame.draw.rect(self.surface, white, rect, 4, border_radius=20)

        text_surf = self.font_btns.render(texto, True, white)
        text_rect = text_surf.get_rect(center=rect.center)
        self.surface.blit(text_surf, text_rect)
        return rect
    
    def draw_main_menu(self):
        if not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1)
        if self.img_background: self.surface.blit(self.img_background, (0, 0))
        else: self.surface.fill(color_fondo)
            
        self.surface.blit(self.img_title, (self.screen_width // 2 - self.img_title.get_width() // 2, 25))
        self.btn_jugar = self.crear_boton("JUGAR", 320, palpitar=True)
        self.btn_salir = self.crear_boton("SALIR", 450)
    
    def draw_diff_menu(self):
        if self.img_background: self.surface.blit(self.img_background, (0, 0))
        else: self.surface.fill(color_fondo)

        subtitulo = self.font_btns.render("Selecciona la Dificultad", True, color_fondo)
        self.surface.blit(subtitulo, (self.screen_width // 2 - subtitulo.get_width() // 2, 200))
        self.btn_facil = self.crear_boton("FÁCIL", 300)
        self.btn_medio = self.crear_boton("MEDIO", 400)
        self.btn_dificil = self.crear_boton("DIFÍCIL", 500)
        self.btn_atras = self.crear_boton("ATRÁS", 620, ancho=150, alto=50)
    
    def draw_pre_game(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 25))
        self.surface.blit(overlay, (0, 0))

        cartel_rect = pygame.Rect(self.screen_width // 2 - 350, 150, 700, 400)
        pygame.draw.rect(self.surface, color_fondo, cartel_rect, border_radius=30)
        pygame.draw.rect(self.surface, white, cartel_rect, 5, border_radius=30)

        titulo_texto = f"MODO {self.difficulty.upper()}"
        if self.difficulty == 'Facil':
            reglas = ["- Encuentra 3 diferencias por nivel.", "- Tienes fallos INFINITOS.", "- ¡Recuerda en las diferencias grandes", "tocar siempre el centro!", "- ¡Tómate tu tiempo para practicar!"]
        elif self.difficulty == 'Medio':
            reglas = [f"- Tienes 3 vidas.", f"- Cada 7 fallos pierdes 1 vida.", f"- Máximo {self.limite_fallos} fallos totales.", "¡Recuerda en las diferencias grandes", "tocar siempre el centro!"]
        else:
            reglas = [f"- ¡Cuidado! Tienes 3 vidas.", f"- Cada 3 fallos pierdes 1 vida.", f"- Solo {self.limite_fallos} fallos permitidos.","¡Recuerda en las diferencias grandes", "tocar siempre el centro!"]

        t_surf = self.font_btns.render(titulo_texto, True, color_boton)
        self.surface.blit(t_surf, (self.screen_width // 2 - t_surf.get_width() // 2, 180))
        for i, regla in enumerate(reglas):
            r_surf = self.font_ui.render(regla, True, white)
            self.surface.blit(r_surf, (cartel_rect.x + 50, 260 + (i * 40)))
        self.btn_entendido = self.crear_boton("¡ENTENDIDO!", 450, ancho=250, alto=60)
    
    def set_difficulty(self, diff_level):
        self.difficulty = diff_level
        self.state = 'PRE_GAME'
        self.vidas = 3
        self.fallos_totales = 0
        if self.difficulty == 'Facil': self.limite_fallos = 999 
        elif self.difficulty == 'Medio':
            self.limite_fallos = 21
            self.fallos_vida = 7
        else: 
            self.limite_fallos = 9
            self.fallos_vida = 3

    def start_game(self):
        self.state = 'PLAYING'
        self.current_stage = 1
        cantidad = 5 if self.difficulty == 'Facil' else 8 if self.difficulty == 'Medio' else 10
        
        if self.difficulty == 'Facil': self.stage_pool = random.sample(self.all_data_F, min(cantidad, len(self.all_data_F)))
        elif self.difficulty == 'Medio': self.stage_pool = random.sample(self.all_data_M, min(cantidad, len(self.all_data_M)))
        elif self.difficulty == 'Dificil': self.stage_pool = random.sample(self.all_data_D, min(cantidad, len(self.all_data_D)))

        self.total_stages = len(self.stage_pool)
        self.cargar_stage_actual()

    def cargar_stage_actual(self):
        self.found_difs = []; self.circles_draw = []; self.difs_actuales = []
        id_actual = self.current_stage - 1
        nivel_data = list(self.stage_pool[id_actual].values())[0]

        path_izq = nivel_data["img_izq"] + ".jpg" if "." not in nivel_data["img_izq"] else nivel_data["img_izq"]
        path_der = nivel_data["img_der"] + ".jpg" if "." not in nivel_data["img_der"] else nivel_data["img_der"]

        izq = Dir / path_izq
        der = Dir / path_der

        self.img_izq = pygame.transform.smoothscale(pygame.image.load(str(izq)).convert_alpha(), (500, 600))
        self.img_der = pygame.transform.smoothscale(pygame.image.load(str(der)).convert_alpha(), (500, 600))

        if self.difficulty == 'Facil': puntos = ["punto1", "punto2", "punto3"]
        elif self.difficulty == 'Medio': puntos = ["punto1", "punto2", "punto3", "punto4", "punto5", "punto6"]
        else: puntos = ["punto1", "punto2", "punto3", "punto4", "punto5", "punto6", "punto7", "punto8", "punto9"]

        for key in puntos:
            px, py = nivel_data[key]
            self.difs_actuales.append((650 + px , 100 + py))

    def draw_hud(self):
        pygame.draw.rect(self.surface, (220, 220, 220), (400, 30, 400, 20), border_radius=10)
        ancho_progreso = (self.current_stage / self.total_stages) * 400
        pygame.draw.rect(self.surface, color_aciertos, (400, 30, ancho_progreso, 20), border_radius=10)

        ui_text = self.font_ui.render(f"Dificultad: {self.difficulty} | Stage: {self.current_stage}/{self.total_stages}", True, color_texto)
        self.surface.blit(ui_text, (20, 20))

        txt_fallos = f"Fallos {self.fallos_totales}/{self.limite_fallos if self.difficulty != 'Facil' else '∞'}"
        fallos_surf = self.font_ui.render(txt_fallos, True, color_texto)
        self.surface.blit(fallos_surf, (self.screen_width - 350, 20))

        for i in range(3):
            x_pos = self.screen_width - 180 + (i * 55)
            y_pos = 15
            if i < self.vidas: self.surface.blit(self.img_corazon, (x_pos, y_pos))
            else: self.surface.blit(self.img_corazon_gris, (x_pos, y_pos))

    def draw_stage(self):
        self.dibujar_degradado((20, 25, 40), (60, 70, 90))
        self.draw_hud()

        if self.img_izq:
            self.surface.blit(self.img_izq, (50, 100))
            self.surface.blit(self.img_der, (650, 100))

        for (dx, dy) in self.circles_draw:
            pygame.draw.circle(self.surface, color_aciertos, (dx, dy), 35, 5)
            pygame.draw.circle(self.surface, color_aciertos, (dx - 600, dy), 35, 5)
    
    def procesar_clic(self, pos):
        if not (650 <= pos[0] <= 1150 and 100 <= pos[1] <= 700): return

        acierto = False
        for i , (dx, dy) in enumerate(self.difs_actuales):
            distancia = math.sqrt((pos[0] - dx)**2 + (pos[1] - dy)**2)
            if distancia < 35 and i not in self.found_difs:
                self.found_difs.append(i)
                self.circles_draw.append((dx, dy))
                self.sonido_acierto.play()
                acierto = True
                break
                
        if not acierto:
            self.fallos_totales += 1
            self.sonido_error.play()
            if self.difficulty != 'Facil':
                if self.fallos_totales % self.fallos_vida == 0: self.vidas -= 1
                if self.vidas <= 0 or self.fallos_totales >= self.limite_fallos:
                    self.state = 'GAME_OVER'

        if len(self.found_difs) == len(self.difs_actuales):
            pygame.time.delay(300) 
            self.pasar_siguiente_stage()

    def pasar_siguiente_stage(self):
        if self.current_stage < self.total_stages:
            self.current_stage += 1
            self.cargar_stage_actual()
        else:
            self.sonido_win.play()
            self.state = 'Victory'
    
    def draw_victory(self):
        self.dibujar_degradado((30, 80, 50), (85, 239, 196))
        texto = self.font_title.render("¡LO LOGRASTE!", True, white)
        info = self.font_ui.render(f"Superado con {self.fallos_totales} fallos y {self.vidas} vidas", True, white)
        self.surface.blit(texto, (self.screen_width // 2 - texto.get_width() // 2, 250))
        self.surface.blit(info, (self.screen_width // 2 - info.get_width() // 2, 350))
        self.btn_volver = self.crear_boton("Menú Principal", 450)

    def draw_game_over(self):
        self.dibujar_degradado((80, 20, 20), (255, 100, 100))
        texto = self.font_title.render("¡OH, HAS PERDIDO!", True, white)
        sub = self.font_btns.render("Vuelve a intentarlo", True, white)
        self.surface.blit(texto, (self.screen_width // 2 - texto.get_width() // 2, 200))
        self.surface.blit(sub, (self.screen_width // 2 - sub.get_width() // 2, 300))
        self.btn_reintentar = self.crear_boton("Reintentar", 400)
        self.btn_volver_menu = self.crear_boton("Menú Principal", 500)