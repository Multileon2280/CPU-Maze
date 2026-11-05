from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Quad, Line, Rectangle
from kivy.core.window import Window
import math
import random

# ==========================================
# HOMEMADE CPU
# ==========================================
memory = [0] * 1000
reg_A = 0
reg_B = 0
pc = 0
running = True

def run_cpu(program):
    global pc, reg_A, reg_B, running
    pc = 0
    reg_A = 0
    reg_B = 0
    running = True
    steps = 0
    for i in range(len(program)):
        memory[i] = program[i]
    while running and steps < 1000:
        steps += 1
        instruction = memory[pc]
        if instruction == 1: pc += 1; reg_A = memory[pc]
        elif instruction == 2: pc += 1; reg_B = memory[pc]
        elif instruction == 3: reg_A += reg_B
        elif instruction == 5: reg_A -= reg_B
        elif instruction == 16: reg_A *= reg_B
        elif instruction == 17:
            if reg_B == 0: running = False
            else: reg_A //= reg_B
        elif instruction == 0: running = False
        pc += 1
    return reg_A

# ==========================================
# GAME: DOORS (Комнаты)
# ==========================================
class DoorsGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,0,0,0,2,0,0,0,2,0,0,0,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,1,2,1,1,1,2,1,1,1,2,1,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,0,0,0,2,0,0,0,2,0,0,0,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,1,2,1,1,1,2,1,1,1,2,1,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,0,0,0,2,0,0,0,2,0,0,0,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        
        self.px = 2.5
        self.py = 2.5
        self.angle = 0
        
        self.scare_x = 11.5
        self.scare_y = 11.5
        
        self.moving = 0 
        self.turning = 0
        self.is_scared = False
        
        self.flicker_timer = 0
        self.next_flicker = random.randint(20, 60) 
        self.flicker_sequence = 0 
        self.current_brightness = 1.0
        
        with self.canvas:
            self.colors = []
            self.walls = []
            for _ in range(60):
                c = Color(0.8, 0.7, 0.1)
                self.colors.append(c)
                quad = Quad(points=[0, 0, 0, 0, 0, 0, 0, 0])
                self.walls.append(quad)
                
        with self.canvas:
            Color(1, 1, 0)
            self.player_dot = Rectangle(pos=(0, 0), size=(4, 4))
            Color(1, 1, 1)
            self.arrow = Line(points=[0, 0, 0, 0], width=2)
            Color(0.3, 0.3, 0.3)
            self.map_lines = []
            for y in range(13):
                for x in range(13):
                    if self.map[y][x] > 0:
                        line = Line(rectangle=(0, 0, 0, 0))
                        self.map_lines.append((x, y, line))
                        
        with self.canvas:
            Color(1, 0.8, 0)
            self.handle = Rectangle(pos=(0, 0), size=(0, 0))
                        
        self.scare_label = Label(
            text="BEHIND YOU.",
            font_size='60sp',
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(Window.width, 150),
            pos=(0, Window.height / 2 - 75),
            halign='center',
            valign='middle',
            opacity=0
        )
        self.scare_label.bind(size=self.scare_label.setter('text_size'))
        self.add_widget(self.scare_label)
                        
        Clock.schedule_interval(self.update, 1.0 / 20.0)

    def cast_ray(self, angle_offset):
        rad = math.radians(self.angle + angle_offset)
        dx = math.cos(rad)
        dy = math.sin(rad)
        
        dist = 0
        while dist < 20:
            dist += 0.1 
            x = int(self.px + dx * dist)
            y = int(self.py + dy * dist)
            
            if x < 0 or x >= 13 or y < 0 or y >= 13:
                return dist, 1
                
            if self.map[y][x] == 1 or self.map[y][x] == 2:
                return dist, self.map[y][x]
                
        return dist, 0

    def interact(self):
        check_x = int(self.px + math.cos(math.radians(self.angle)) * 1.2)
        check_y = int(self.py + math.sin(math.radians(self.angle)) * 1.2)
        
        if 0 <= check_x < 13 and 0 <= check_y < 13:
            if self.map[check_y][check_x] == 2:
                self.map[check_y][check_x] = 3
            elif self.map[check_y][check_x] == 3:
                self.map[check_y][check_x] = 2

    def update(self, dt):
        if self.is_scared:
            return
            
        speed = 0.1
        turn_speed = 5
        
        if self.moving != 0:
            new_x = self.px + math.cos(math.radians(self.angle)) * speed * self.moving
            new_y = self.py + math.sin(math.radians(self.angle)) * speed * self.moving
            
            if self.map[int(self.py)][int(new_x)] != 1 and self.map[int(self.py)][int(new_x)] != 2:
                self.px = new_x
                
            if self.map[int(new_y)][int(self.px)] != 1 and self.map[int(new_y)][int(self.px)] != 2:
                self.py = new_y
                
        if self.turning != 0:
            program = [1, int(self.angle), 2, turn_speed * self.turning, 3, 0]
            self.angle = run_cpu(program)
            
        screen_width = Window.width
        screen_height = Window.height
        col_width = screen_width / 60
        
        self.flicker_timer += 1
        if self.flicker_sequence > 0:
            self.flicker_sequence -= 1
            self.current_brightness = random.uniform(0.7, 1.0)
        else:
            self.current_brightness = 1.0
            if self.flicker_timer > self.next_flicker:
                self.flicker_sequence = random.randint(3, 8)
                self.flicker_timer = 0
                self.next_flicker = random.randint(20, 60)
        
        brightness_mult = self.current_brightness
        
        handle_drawn = False
        
        door_in_sight = False
        for ray_offset in [-10, -5, 0, 5, 10]:
            rad = math.radians(self.angle + ray_offset)
            dx = math.cos(rad)
            dy = math.sin(rad)
            dist = 0
            while dist < 1.5:
                dist += 0.1
                x = int(self.px + dx * dist)
                y = int(self.py + dy * dist)
                if 0 <= x < 13 and 0 <= y < 13:
                    if self.map[y][x] == 2 or self.map[y][x] == 3:
                        door_in_sight = True
                        break
                else:
                    break
            if door_in_sight: break

        for i in range(60):
            ray_angle = -30 + (i * 60 / 60)
            dist, wall_type = self.cast_ray(ray_angle)
            
            if dist < 0.1: dist = 0.1
            
            wall_height = screen_height / dist
            
            x1 = i * col_width
            y1 = (screen_height / 2) - (wall_height / 2)
            x2 = (i + 1) * col_width
            y2 = y1 + wall_height
            
            self.walls[i].points = [x1, y1, x1, y2, x2, y2, x2, y1]
            
            dist_brightness = max(0.1, min(1.0, 1.5 / (dist + 0.5)))
            angle_brightness = 1.0 - (abs(ray_angle) / 30.0) * 0.7 
            brightness = dist_brightness * angle_brightness * brightness_mult
            
            if wall_type == 1:
                self.colors[i].rgba = (0.8 * brightness, 0.7 * brightness, 0.1 * brightness, 1)
            elif wall_type == 2:
                self.colors[i].rgba = (0.4 * brightness, 0.2 * brightness, 0.0 * brightness, 1)
            else:
                self.walls[i].points = [0,0,0,0,0,0,0,0]
                
        if door_in_sight:
            for i in range(60):
                ray_angle = -30 + (i * 60 / 60)
                if -2 < ray_angle < 2:
                    rad = math.radians(self.angle + ray_angle)
                    dist = 0
                    while dist < 2:
                        dist += 0.1
                        x = int(self.px + math.cos(rad) * dist)
                        y = int(self.py + math.sin(rad) * dist)
                        if 0 <= x < 13 and 0 <= y < 13 and self.map[y][x] == 2:
                            x1 = i * col_width
                            handle_x = x1 + (col_width / 2) - 3
                            handle_y = (screen_height / 2) - 5
                            self.handle.pos = (handle_x, handle_y)
                            self.handle.size = (6, 10)
                            handle_drawn = True
                            break
                    break

        if not handle_drawn:
            self.handle.size = (0, 0)
                
        map_size = 120 
        map_x = screen_width - map_size - 10
        map_y = screen_height - map_size - 10
        cell_size = map_size / 13
        
        player_screen_x = map_x + self.px * cell_size
        player_screen_y = map_y + self.py * cell_size
        self.player_dot.pos = (player_screen_x - 2, player_screen_y - 2)
        
        arrow_len = 6
        arrow_end_x = player_screen_x + math.cos(math.radians(self.angle)) * arrow_len
        arrow_end_y = player_screen_y + math.sin(math.radians(self.angle)) * arrow_len
        self.arrow.points = [player_screen_x, player_screen_y, arrow_end_x, arrow_end_y]
        
        for (x, y, line) in self.map_lines:
            if self.map[y][x] > 0:
                line.rectangle = (map_x + x * cell_size, map_y + y * cell_size, cell_size, cell_size)

        dist_to_scare = math.sqrt((self.px - self.scare_x)**2 + (self.py - self.scare_y)**2)
        if dist_to_scare < 0.5:
            self.trigger_scare()

    def trigger_scare(self):
        self.is_scared = True
        self.scare_label.opacity = 1
        
        for i in range(60):
            self.colors[i].rgba = (1, 0, 0, 1)
            
        Clock.schedule_once(self.reset_game, 3)

    def reset_game(self, dt):
        self.is_scared = False
        self.scare_label.opacity = 0
        self.px = 2.5
        self.py = 2.5
        self.angle = 0
        for y in range(13):
            for x in range(13):
                if self.map[y][x] == 3:
                    self.map[y][x] = 2

class DoorsApp(App):
    def build(self):
        root = FloatLayout()
        game = DoorsGame()
        root.add_widget(game)
        
        btn_fwd = Button(text="FORWARD", size_hint=(0.2, 0.1), pos_hint={'x': 0.4, 'y': 0.02})
        btn_left = Button(text="<", size_hint=(0.1, 0.1), pos_hint={'x': 0.05, 'y': 0.02})
        btn_right = Button(text=">", size_hint=(0.1, 0.1), pos_hint={'x': 0.85, 'y': 0.02})
        btn_use = Button(text="USE", size_hint=(0.15, 0.1), pos_hint={'x': 0.6, 'y': 0.02}, background_color=(0, 1, 0, 1))
        
        btn_fwd.bind(on_press=lambda x: setattr(game, 'moving', 1))
        btn_fwd.bind(on_release=lambda x: setattr(game, 'moving', 0))
        
        btn_left.bind(on_press=lambda x: setattr(game, 'turning', -1))
        btn_left.bind(on_release=lambda x: setattr(game, 'turning', 0))
        
        btn_right.bind(on_press=lambda x: setattr(game, 'turning', 1))
        btn_right.bind(on_release=lambda x: setattr(game, 'turning', 0))
        
        btn_use.bind(on_press=lambda x: game.interact())
        
        root.add_widget(btn_fwd)
        root.add_widget(btn_left)
        root.add_widget(btn_right)
        root.add_widget(btn_use)
        
        return root

if __name__ == '__main__':
    DoorsApp().run()
