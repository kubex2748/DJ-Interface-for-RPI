import pygame
import sys
import os
import json
from math import floor

from Scripts.Analyse import Analyse
from Scripts.Menu import Button, Button_Pic


os.environ["SDL_RENDER_DRIVER"] = "software"
pygame.init()
pygame.display.set_caption("Podstawka Pygame")


class Main:
    def __init__(self):

        self.tracks = []
        self.selected = 0

        # --- INIT ---
        self.WIDTH = 480
        self.HEIGHT = 320
        self.FPS = 60

        self.path_1 = None
        self.path_2 = None

        self.gamma = 0.7
        self.beats_per_bar = 4
        self.scale_y = 10    # waveform height

        self.playhead_x = self.WIDTH // 2
        self.bars_visible_each_side = 8
        self.zoom = 20

        self.arial_12 = pygame.font.SysFont("arial", 12)
        self.arial_16 = pygame.font.SysFont("arial", 16)

        self.track_pos_sec_1 = 0.0
        self.track_pos_sec_2 = 0.0

        self.px_per_sec_1 = 0
        self.px_per_sec_2 = 0

        # --- MODE ---
        self.DJ_MODE = True
        self.search_track_button = Button(5, self.HEIGHT - 35, "TRACKS")
        self.TRACKS_DIR = "TRACKS"
        self.scroll_index = 0
        self.visible_count = 5

        self.deck_button = Button(5, self.HEIGHT - 40, "DECK")
        self.analys_button = Button(self.WIDTH - 100, self.HEIGHT/2 - 140, "ANALYSE")
        self.push_button = Button(self.WIDTH - 180, self.HEIGHT/2 - 140, "PUSH")

        # --- RUN ---
        self.running = True
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT),
            pygame.NOFRAME
        )
        self.clock = pygame.time.Clock()

        self.playhead_pos_1 = 0.0  # 0.0 → 1.0
        self.playhead_pos_2 = 0.0  # 0.0 → 1.0

        self.hot_key_x_1 = [
            None,
            None,
            None,
            None
        ]

        self.hot_key_x_2 = [
            None,
            None,
            None,
            None
        ]
        
        self.options_button = Button(5, 5, "OPTION")

        # --- EDIT GRID ---
        self.edit_grid_button_1 = Button(self.WIDTH - 70, self.HEIGHT/2 - 140, "EDIT GRID")
        self.edit_save_button_1 = Button(self.WIDTH - 70, self.HEIGHT/2 - 140, "SAVE")

        self.edit_grid_buffer_1 = []
        self.edit_grid_state_1 = False

        self.arrow_left_button_1 = Button_Pic(self.WIDTH - 70, self.HEIGHT/2 - 160, "graph/arrow_left")
        self.arrow_right_button_1 = Button_Pic(self.WIDTH - 20, self.HEIGHT/2 - 160, "graph/arrow_right")

        self.edit_grid_button_2 = Button(self.WIDTH - 70, self.HEIGHT/2 + 110, "EDIT GRID")
        self.edit_save_button_2 = Button(self.WIDTH - 70, self.HEIGHT/2 + 110, "SAVE")

        self.edit_grid_buffer_2 = []
        self.edit_grid_state_2 = False

        self.arrow_left_button_2 = Button_Pic(self.WIDTH - 70, self.HEIGHT/2 + 140, "graph/arrow_left")
        self.arrow_right_button_2 = Button_Pic(self.WIDTH - 20, self.HEIGHT/2 + 140, "graph/arrow_right")

        # --- ANALYSE ---
        self.sampling_rate = 44100

        self.waveform_1 = []
        self.track_duration_sec_1 = 0.0
        self.avg_energy_1 = 0
        self.bar_x_positions_1 = []
        self.bpm_1 = 0
        self.key_1 = ""

        self.waveform_2 = []
        self.track_duration_sec_2 = 0.0
        self.avg_energy_2 = 0
        self.bar_x_positions_2 = []
        self.bpm_2 = 0
        self.key_2 = ""

        #self.label_bpm_1 = pygame.font.Font.render(self.arial_12, str(self.bpm_1), True, (200, 200, 200))
        #screen.blit(self.label_text, (self.x_cord + 5 , self.y_cord + 10))

        # --- COLOR ---
        self.bg_color = (50, 50, 50)
        self.sec_color = (0, 0, 0)
        self.bar_color = (180, 180, 180)
        self.PLAYHEAD_COLOR = (232, 9, 184)
        self.hot_key_colors = [
            (227, 16, 55),
            (237, 146, 9),
            (19, 70, 237),
            (232, 240, 12)
        ]

        self.WAVE_COLOR_BASS = (255, 50, 50)
        self.WAVE_COLOR_MIDD = (50, 255, 50)
        self.WAVE_COLOR_TREB = (50, 50, 255)

        # --- START PROCESS ---
        self.search_for_tracks()

    # --- AMALYSE ---
    def start_analyse(self, path):
        analyse = Analyse(f'TRACKS/{path}', self.sampling_rate)

        waveform = analyse.wave_form(self.WIDTH) 
        energies = [x[2] for x in waveform]   
        avg_energy = sum(energies) / len(energies)
        bpm, key, track_duration_sec = analyse.analyseBpmKey()

        bar_length_sec = self.beats_per_bar * 60 / bpm
        px_per_sec = self.WIDTH / track_duration_sec
        bar_length_px = int(bar_length_sec * px_per_sec)

        bar_x_positions = []

        if bar_length_px < 1:
            bar_length_px = 1
        x = 0

        while x <= self.WIDTH:
            bar_x_positions.append(x)
            x += bar_length_px

        data = {
            "bpm": bpm,
            "key": key,
            "waveform": waveform,
            "energy": avg_energy,
            "duration": track_duration_sec,
            "bars": bar_x_positions,
            "hotkeys": [None, None, None, None]
        }

        return data

    def save_track_json(self, track_path, data):
        json_path = os.path.splitext(track_path)[0] + ".json"
        with open(json_path, "w") as f:
            json.dump(data, f)

    def load_track_json(self, track_path):
        json_path = os.path.splitext(track_path)[0] + ".json"

        if not os.path.exists(json_path):
            return None

        with open(json_path, "r") as f:
            data = json.load(f)

        return data
    
    def track_has_json(self, track_path):
        json_path = os.path.splitext(track_path)[0] + ".json"
        return os.path.exists(json_path)
    
    def search_for_tracks(self):
        self.tracks.clear()
        for file in os.listdir(self.TRACKS_DIR):
            if file.lower().endswith((".wav")):
                if self.track_has_json(f'TRACKS/{file}'):
                    self.tracks.append(file)
                else:
                    data = self.start_analyse(file)
                    self.save_track_json(f'TRACKS/{file}', data)
                    self.tracks.append(file)
    
    def start(self):
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000
            self.screen.fill(self.bg_color)

            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                for track in self.tracks:
                    json_path = os.path.splitext(f'TRACKS/{track}')[0] + ".json"
                    if not os.path.exists(json_path):
                        continue

                    with open(json_path, "r") as f:
                        data = json.load(f)

                    if data.get("hotkeys") != self.hot_key_x_1:
                        data["hotkeys"] = self.hot_key_x_1
                    elif data.get("hotkeys") != self.hot_key_x_2:
                        data["hotkeys"] = self.hot_key_x_2
                    else:
                        continue

                    with open(json_path, "w") as f:
                        json.dump(data, f, indent=4)

                self.running = False

            # playhead control
            if keys[pygame.K_RIGHT]:
                self.playhead_pos_1 += dt * 0.025
                self.track_pos_sec += dt * 10
            if keys[pygame.K_LEFT]:
                self.playhead_pos_1 -= dt * 0.025
                self.track_pos_sec -= dt * 10
            if keys[pygame.K_d]:
                self.playhead_pos_2 += dt * 0.2
            if keys[pygame.K_a]:
                self.playhead_pos_2 -= dt * 0.2

            if self.DJ_MODE:
                if self.search_track_button.update(dt):
                    self.DJ_MODE = False
                self.search_track_button.draw(self.screen)


                if self.options_button.update(dt):
                    pass
                self.options_button.draw(self.screen)

                # edit grid
                if not self.edit_grid_state_1:
                    if self.edit_grid_button_1.update(dt):
                        self.edit_grid_state_1 = not self.edit_grid_state_1
                    self.edit_grid_button_1.draw(self.screen)
                else:
                    if self.edit_save_button_1.update(dt):
                        self.edit_grid_state_1 = not self.edit_grid_state_1
                    self.edit_save_button_1.draw(self.screen)

                if self.edit_grid_state_1:
                    if self.arrow_left_button_1.update(dt):
                        by = 0
                        by -= 1
                        for b in range(0, len(self.bar_x_positions_1)):
                            self.bar_x_positions_1[b] = self.bar_x_positions_1[b] + by
                    self.arrow_left_button_1.draw(self.screen)

                    if self.arrow_right_button_1.update(dt):
                        by = 0
                        by += 1
                        for b in range(0, len(self.bar_x_positions_1)):
                            self.bar_x_positions_1[b] = self.bar_x_positions_1[b] + by
                    self.arrow_right_button_1.draw(self.screen)

                if not self.edit_grid_state_2:
                    if self.edit_grid_button_2.update(dt):
                        self.edit_grid_state_2 = not self.edit_grid_state_2
                    self.edit_grid_button_2.draw(self.screen)
                else:
                    if self.edit_save_button_2.update(dt):
                        self.edit_grid_state_2 = not self.edit_grid_state_2
                    self.edit_save_button_2.draw(self.screen)

                if self.edit_grid_state_2:
                    if self.arrow_left_button_2.update(dt):
                        by = 0
                        by -= 1
                        for b in range(0, len(self.bar_x_positions_2)):
                            self.bar_x_positions_2[b] = self.bar_x_positions_2[b] + by
                    self.arrow_left_button_2.draw(self.screen)

                    if self.arrow_right_button_2.update(dt):
                        by = 0
                        by += 1
                        for b in range(0, len(self.bar_x_positions_2)):
                            self.bar_x_positions_2[b] = self.bar_x_positions_2[b] + by
                    self.arrow_right_button_2.draw(self.screen)

                # draw up wave form
                if self.path_1 is not None and not len(self.waveform_1) == 0:
                    step_1 = self.WIDTH / len(self.waveform_1)
                    mid_y_1 = self.HEIGHT/2 - 90    # middle point on y

                    # draw bar lines
                    for x in self.bar_x_positions_1:
                        pygame.draw.line(self.screen, self.bar_color, (x, self.HEIGHT/2 - 82), (x, self.HEIGHT/2 - 102), 1)

                    for i, ((mn, mx), (r, g, b), energy) in enumerate(self.waveform_1):
                        x = int(i * step_1)

                        if g > r or b > r or (g+b)/2 > r:
                            self.scale_y = 4
                        else:
                            self.scale_y = 8

                        y1 = int(mid_y_1 - mx * self.scale_y)
                        y2 = int(mid_y_1 - mn * self.scale_y)

                        gamma = 0.7
                        color = (
                            min(255, int((r ** gamma) * 255)),
                            min(255, int((g ** gamma) * 255)),
                            min(255, int((b ** gamma) * 255))
                        )

                        if energy > self.avg_energy_1 * 1.8:
                            color = (255, 0, 0)  # red = drop
                            scale = 1.2
                            y1 = int(mid_y_1 - mx * self.scale_y * scale)
                            y2 = int(mid_y_1 - mn * self.scale_y * scale)
                        
                        top = min(y1, y2)
                        height = abs(y2 - y1)
                        pygame.draw.rect(self.screen, color, (x - 1, top, 1, height))
                    
                # draw down wave form
                if self.path_2 is not None and not len(self.waveform_2) == 0:
                    step_2 = self.WIDTH / len(self.waveform_2)
                    mid_y_2 = self.HEIGHT/2 + 92    # middle point on y

                    # draw bar lines
                    for x in self.bar_x_positions_2:
                        pygame.draw.line(self.screen, self.bar_color, (x, self.HEIGHT/2 + 100), (x, self.HEIGHT/2 + 80), 1)

                    for i, ((mn, mx), (r, g, b), energy) in enumerate(self.waveform_2):
                        x = int(i * step_2)

                        if g > r or b > r or (g+b)/2 > r:
                            self.scale_y = 4
                        else:
                            self.scale_y = 8

                        y1 = int(mid_y_2 - mx * self.scale_y)
                        y2 = int(mid_y_2 - mn * self.scale_y)

                        gamma = 0.7
                        color = (
                            min(255, int((r ** gamma) * 255)),
                            min(255, int((g ** gamma) * 255)),
                            min(255, int((b ** gamma) * 255))
                        )

                        if energy > self.avg_energy_2 * 1.8:
                            color = (255, 0, 0)  # red = drop
                            scale = 1.4
                            y1 = int(mid_y_2 - mx * self.scale_y * scale)
                            y2 = int(mid_y_2 - mn * self.scale_y * scale)
                        
                        top = min(y1, y2)
                        height = abs(y2 - y1)

                        pygame.draw.rect(self.screen, color, (x - 1, top, 3, height))
                    
                # draw up wave form (rolling) - DECK 1
                if self.path_1 is not None and len(self.waveform_1) > 0:
                    self.px_per_sec_1 = self.WIDTH / ((60 / self.bpm_1) * self.beats_per_bar * self.bars_visible_each_side * 2)
                    mid_y_1_top = self.HEIGHT/2 - 82
                    mid_y_1_bottom = self.HEIGHT/2 - 40
                    visible_width = self.WIDTH
                    waveform_len = len(self.waveform_1)
                    step_1 = visible_width / waveform_len

                    # draw bar lines
                    for bx in self.bar_x_positions_1:
                        bx_screen = int(bx * self.zoom - self.track_pos_sec_1 * self.px_per_sec_1 + self.playhead_x)
                        if 0 <= bx_screen <= self.WIDTH:
                            pygame.draw.line(self.screen, self.bar_color, (bx_screen, mid_y_1_top), (bx_screen, mid_y_1_bottom), 3)

                    for i, ((mn, mx), (r, g, b), energy) in enumerate(self.waveform_1):
                        # przesunięcie zależne od track_pos_sec
                        x = int(i * step_1 * self.zoom - self.track_pos_sec_1 * self.px_per_sec_1 + self.playhead_x) 
                        if x < 0 or x > self.WIDTH:
                            continue  # nie rysujemy poza ekranem

                        # skalowanie y
                        scale_y = 20 if r >= max(g, b) else 4
                        y1 = int(mid_y_1_bottom - mx * scale_y)
                        y2 = int(mid_y_1_bottom - mn * scale_y)

                        gamma = 0.7
                        color = (
                            min(255, int((r ** gamma) * 255)),
                            min(255, int((g ** gamma) * 255)),
                            min(255, int((b ** gamma) * 255))
                        )

                        if energy > self.avg_energy_1 * 1.8:
                            color = (255, 0, 0)
                            scale = 1.2
                            y1 = int(mid_y_1_bottom - mx * scale_y * scale)
                            y2 = int(mid_y_1_bottom - mn * scale_y * scale)

                        top = min(y1, y2)
                        height = abs(y2 - y1)
                        pygame.draw.rect(self.screen, color, (x - 1, top, 10, height))



                    # draw up wave form (rolling) - DECK 2
                if self.path_1 is not None and len(self.waveform_2) > 0:
                    self.px_per_sec_1 = self.WIDTH / ((60 / self.bpm_1) * self.beats_per_bar * self.bars_visible_each_side * 2)
                    mid_y_2_top = self.HEIGHT/2 + 80
                    mid_y_2_bottom = self.HEIGHT/2 + 40
                    visible_width = self.WIDTH
                    waveform_len = len(self.waveform_2)
                    step_2 = visible_width / waveform_len

                    # draw bar lines
                    for bx in self.bar_x_positions_2:
                        bx_screen = int(bx * self.zoom - self.track_pos_sec_2 * self.px_per_sec_2 + self.playhead_x)
                        if 0 <= bx_screen <= self.WIDTH:
                            pygame.draw.line(self.screen, self.bar_color, (bx_screen, mid_y_2_top), (bx_screen, mid_y_2_bottom), 3)

                    for i, ((mn, mx), (r, g, b), energy) in enumerate(self.waveform_2):
                        # przesunięcie zależne od track_pos_sec
                        x = int(i * step_2 * self.zoom - self.track_pos_sec_2 * self.px_per_sec_2 + self.playhead_x) 
                        if x < 0 or x > self.WIDTH:
                            continue

                        # skalowanie y
                        scale_y = 20 if r >= max(g, b) else 4
                        y1 = int(mid_y_2_bottom - mx * scale_y)
                        y2 = int(mid_y_2_bottom - mn * scale_y)

                        gamma = 0.7
                        color = (
                            min(255, int((r ** gamma) * 255)),
                            min(255, int((g ** gamma) * 255)),
                            min(255, int((b ** gamma) * 255))
                        )

                        if energy > self.avg_energy_2 * 1.8:
                            color = (255, 0, 0)
                            scale = 1.2
                            y1 = int(mid_y_2_bottom - mx * scale_y * scale)
                            y2 = int(mid_y_2_bottom - mn * scale_y * scale)

                        top = min(y1, y2)
                        height = abs(y2 - y1)
                        pygame.draw.rect(self.screen, color, (x - 1, top, 10, height))

                #set hot keys
                # DECK 1
                if keys[pygame.K_1]:
                    if self.hot_key_x_1[0] is None:
                        self.hot_key_x_1[0] = ph_x_1
                    else:
                        self.playhead_pos_1 = self.hot_key_x_1[0] / self.WIDTH
                if keys[pygame.K_2]:
                    if self.hot_key_x_1[1] is None:
                        self.hot_key_x_1[1] = ph_x_1
                    else:
                        self.playhead_pos_1 = self.hot_key_x_1[1] / self.WIDTH
                if keys[pygame.K_3]:
                    if self.hot_key_x_1[2] is None:
                        self.hot_key_x_1[2] = ph_x_1
                    else:
                        self.playhead_pos_1 = self.hot_key_x_1[2] / self.WIDTH
                if keys[pygame.K_4]:
                    if self.hot_key_x_1[3] is None:
                        self.hot_key_x_1[3] = ph_x_1
                    else:
                        self.playhead_pos_1 = self.hot_key_x_1[3] / self.WIDTH
                
                # DECK 2
                if keys[pygame.K_5]:
                    if self.hot_key_x_2[0] is None:
                        self.hot_key_x_2[0] = ph_x_2
                    else:
                        self.playhead_pos_2 = self.hot_key_x_2[0] / self.WIDTH
                if keys[pygame.K_6]:
                    if self.hot_key_x_2[1] is None:
                        self.hot_key_x_2[1] = ph_x_2
                    else:
                        self.playhead_pos_2 = self.hot_key_x_2[1] / self.WIDTH
                if keys[pygame.K_7]:
                    if self.hot_key_x_2[2] is None:
                        self.hot_key_x_2[2] = ph_x_2
                    else:
                        self.playhead_pos_2 = self.hot_key_x_2[2] / self.WIDTH
                if keys[pygame.K_8]:
                    if self.hot_key_x_2[3] is None:
                        self.hot_key_x_2[3] = ph_x_2
                    else:
                        self.playhead_pos_2 = self.hot_key_x_2[3] / self.WIDTH

                #draw hot keys
                for h in range(0, len(self.hot_key_x_1)):
                    if self.hot_key_x_1[h] is not None:
                        pygame.draw.line(self.screen, self.hot_key_colors[h], (self.hot_key_x_1[h], self.HEIGHT/2 - 102), (self.hot_key_x_1[h], self.HEIGHT/2 - 82), 4)
                for h in range(0, len(self.hot_key_x_2)):
                    if self.hot_key_x_2[h] is not None:
                        pygame.draw.line(self.screen, self.hot_key_colors[h], (self.hot_key_x_2[h], self.HEIGHT/2 + 80), (self.hot_key_x_2[h], self.HEIGHT/2 + 100), 2)

                # playhead
                self.playhead_pos_1 = max(0.0, min(1.0, self.playhead_pos_1))
                ph_x_1 = int(self.playhead_pos_1 * self.WIDTH)
                pygame.draw.line(self.screen, self.PLAYHEAD_COLOR, (ph_x_1, self.HEIGHT/2 - 82), (ph_x_1, self.HEIGHT/2 - 102), 2)
                self.playhead_pos_2 = max(0.0, min(1.0, self.playhead_pos_2))
                ph_x_2 = int(self.playhead_pos_2 * self.WIDTH)
                pygame.draw.line(self.screen, self.PLAYHEAD_COLOR, (ph_x_2, self.HEIGHT/2 + 80), (ph_x_2, self.HEIGHT/2 + 100), 2)

                # playhead rolling
                pygame.draw.line(self.screen, self.PLAYHEAD_COLOR, (self.playhead_x, self.HEIGHT/2 - 82), (self.playhead_x, self.HEIGHT/2 + 80), 2)

                # draw GUI
                pygame.draw.rect(self.screen, self.sec_color, (0, self.HEIGHT/2 - 2, self.WIDTH, 4))
                pygame.draw.rect(self.screen, self.sec_color, (0, self.HEIGHT/2 - 102, self.WIDTH, 2))
                pygame.draw.rect(self.screen, self.sec_color, (0, self.HEIGHT/2 - 82, self.WIDTH, 2))
                pygame.draw.rect(self.screen, self.sec_color, (0, self.HEIGHT/2 + 100, self.WIDTH, 2))
                pygame.draw.rect(self.screen, self.sec_color, (0, self.HEIGHT/2 + 80, self.WIDTH, 2))

                self.screen.blit(pygame.font.Font.render(self.arial_12, f'BPM: {str(floor(self.bpm_1))}', True, (200, 200, 200)), (100 , self.HEIGHT/2 - 132))
                self.screen.blit(pygame.font.Font.render(self.arial_12, f'KEY: {self.key_1}', True, (200, 200, 200)), (100 , self.HEIGHT/2 - 118))

                self.screen.blit(pygame.font.Font.render(self.arial_12, f'BPM: {str(floor(self.bpm_2))}', True, (200, 200, 200)), (100 , self.HEIGHT/2 + 117))
                self.screen.blit(pygame.font.Font.render(self.arial_12, f'KEY: {self.key_2}', True, (200, 200, 200)), (100 , self.HEIGHT/2 + 105))

            else:
                if self.deck_button.update(dt):
                    self.DJ_MODE = True
                self.deck_button.draw(self.screen)

                if self.analys_button.update(dt):
                    self.search_for_tracks()
                self.analys_button.draw(self.screen)

                if self.push_button.update(dt):
                    pass
                self.push_button.draw(self.screen)

                if keys[pygame.K_DOWN]:
                    if self.selected < len(self.tracks)-1:
                        self.selected += 1
                        if self.selected >= self.scroll_index + self.visible_count:
                            self.scroll_index += 1
                if keys[pygame.K_UP]:
                    if self.selected > 0:
                        self.selected -= 1
                        if self.selected < self.scroll_index:
                            self.scroll_index -= 1

                if keys[pygame.K_o]:
                    self.path_1 = f'TRACKS/{self.tracks[self.selected]}'
                    data = self.load_track_json(self.path_1)

                    if data:
                        self.bpm_1 = data["bpm"]
                        self.key_1 = data["key"]
                        self.waveform_1 = data["waveform"]
                        self.avg_energy_1 = data["energy"]
                        self.track_duration_sec_1 = data["duration"]
                        self.bar_x_positions_1 = data["bars"]
                        self.hot_key_x_1 = data["hotkeys"]

                if keys[pygame.K_p]:
                    self.path_2 = f'TRACKS/{self.tracks[self.selected]}'
                    data = self.load_track_json(self.path_2)

                    if data:
                        self.bpm_2 = data["bpm"]
                        self.key_2 = data["key"]
                        self.waveform_2 = data["waveform"]
                        self.avg_energy_2 = data["energy"]
                        self.track_duration_sec_2 = data["duration"]
                        self.bar_x_positions_2 = data["bars"]
                        self.hot_key_x_2 = data["hotkeys"]
                
                # ograniczenia
                self.selected = max(0, min(self.selected, len(self.tracks) - 1))

                # --- RYSOWANIE ---
                y = 100
                for i, track in enumerate(self.tracks[self.scroll_index:self.scroll_index+self.visible_count]):
                    font_color = (220, 220, 220)
                    if i % 2 == 0:
                        pygame.draw.rect(self.screen, (100, 100, 100), (20, y - 4, self.WIDTH - 40, 15))

                    if i == self.selected:
                        pygame.draw.rect(self.screen, (80, 80, 120), (20, y - 4, self.WIDTH - 40, 15))

                    if f'TRACKS/{track}' == self.path_1 or f'TRACKS/{track}' == self.path_2:
                        font_color = (20, 255, 20)

                    text = self.arial_12.render(f'{i+self.scroll_index}: {track}', True, font_color)
                    self.screen.blit(text, (30, y-2))
                    y += 15

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    interface = Main()
    interface.start()
