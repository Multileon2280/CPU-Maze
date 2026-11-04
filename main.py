from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Quad, Line, Rectangle
from kivy.core.window import Window
import math

# ==========================================
# HOMEMADE 32-BIT CPU (Calculates rotation)
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
# GAME: 3D MAZE
# ==========================================
class MazeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.map = [
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,2,2,2,0,0,1],
            [1,0,2,0,0,0,0,1],
            [1,0,2,0,3,3,0,1],
            [1,0,0,0,3,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1]
        ]
        
        self.px = 1.5
        self.py = 1.5
        self.angle = 0
        self.exit_x = 6.5
        self.exit_y = 6.5
        
        self.moving = 0 
        self.turning = 0
        
        with self.canvas:
            self.colors = []
            self.walls = []
            for _ in range(40):
                c = Color(0.2, 0.6, 1)
                self.colors.append(c)
                quad = Quad(points=[0, 0, 0, 0, 0, 0, 0, 0])
                self.walls.append(quad)
                
        with self.canvas:
            Color(1, 1, 0)
            self.player_dot = Rectangle(pos=(0, 0), size=(5, 5))
            Color(0, 1, 0)
            self.exit_dot = Rectangle(pos=(0, 0), size=(5, 5))
            Color(0.5, 0.5, 0.5)
            self.map_lines = []
            for y in range(8):
                for x in range(8):
                    if self.map[y][x] > 0:
                        line = Line(rectangle=(0, 0, 0, 0))
                        self.map_lines.append((x, y, line))
                        
        Clock.schedule_interval(self.update, 1.0 / 20.0)

    def cast_ray(self, angle_offset):
        rad = math.radians(self.angle + angle_offset)
        dx = math.cos(rad)
        dy = math.sin(rad)
        
        dist = 0
        while dist < 15:
            dist += 0.1 
            x = int(self.px + dx * dist)
            y = int(self.py + dy * dist)
            
            if x < 0 or x >= 8 or y < 0 or y >= 8:
                return dist, 1
                
            if self.map[y][x] > 0:
                return dist, self.map[y][x]
                
        return dist, 0

    def update(self, dt):
        speed = 0.1
        turn_speed = 5
        
        if self.moving != 0:
            new_x = self.px + math.cos(math.radians(self.angle)) * speed * self.moving
            new_y = self.py + math.sin(math.radians(self.angle)) * speed * self.moving
            if self.map[int(new_y)][int(new_x)] == 0:
                self.px = new_x
                self.py = new_y
                
        if self.turning != 0:
            program = [1, int(self.angle), 2, turn_speed * self.turning, 3, 0]
            self.angle = run_cpu(program)
            
        screen_width = Window.width
        screen_height = Window.height
        col_width = screen_width / 40
        
        for i in range(40):
            ray_angle = -30 + (i * 60 / 40)
            dist, wall_type = self.cast_ray(ray_angle)
            
            if dist < 0.1: dist = 0.1
            
            wall_height = screen_height / dist
            
            x1 = i * col_width
            y1 = (screen_height / 2) - (wall_height / 2)
            x2 = (i + 1) * col_width
            y2 = y1 + wall_height
            
            self.walls[i].points = [x1, y1, x1, y2, x2, y2, x2, y1]
            
            brightness = max(0.3, min(1.0, 1.5 / (dist + 0.5)))
            
            if wall_type == 1:
                self.colors[i].rgba = (0.2 * brightness, 0.4 * brightness, 1.0 * brightness, 1)
            elif wall_type == 2:
                self.colors[i].rgba = (1.0 * brightness, 0.2 * brightness, 0.2 * brightness, 1)
            elif wall_type == 3:
                self.colors[i].rgba = (0.2 * brightness, 1.0 * brightness, 0.2 * brightness, 1)
            else:
                self.walls[i].points = [0,0,0,0,0,0,0,0]
                
        map_size = 100
        map_x = screen_width - map_size - 10
        map_y = screen_height - map_size - 10
        cell_size = map_size / 8
        
        player_screen_x = map_x + self.px * cell_size
        player_screen_y = map_y + self.py * cell_size
        self.player_dot.pos = (player_screen_x - 2, player_screen_y - 2)
        
        exit_screen_x = map_x + self.exit_x * cell_size
        exit_screen_y = map_y + self.exit_y * cell_size
        self.exit_dot.pos = (exit_screen_x - 2, exit_screen_y - 2)
        
        for (x, y, line) in self.map_lines:
            if self.map[y][x] > 0:
                line.rectangle = (map_x + x * cell_size, map_y + y * cell_size, cell_size, cell_size)

        self.check_exit()

    def check_exit(self):
        dist = math.sqrt((self.px - self.exit_x)**2 + (self.py - self.exit_y)**2)
        if dist < 0.5:
            print("YOU ESCAPED THE MAZE! (Returning to start)")
            self.px = 1.5
            self.py = 1.5
            self.angle = 0

class MazeApp(App):
    def build(self):
        root = FloatLayout()
        game = MazeGame()
        root.add_widget(game)
        
        btn_fwd = Button(text="FORWARD", size_hint=(0.3, 0.1), pos_hint={'x': 0.35, 'y': 0.02})
        btn_left = Button(text="<", size_hint=(0.1, 0.1), pos_hint={'x': 0.05, 'y': 0.02})
        btn_right = Button(text=">", size_hint=(0.1, 0.1), pos_hint={'x': 0.85, 'y': 0.02})
        
        btn_fwd.bind(on_press=lambda x: setattr(game, 'moving', 1))
        btn_fwd.bind(on_release=lambda x: setattr(game, 'moving', 0))
        
        btn_left.bind(on_press=lambda x: setattr(game, 'turning', -1))
        btn_left.bind(on_release=lambda x: setattr(game, 'turning', 0))
        
        btn_right.bind(on_press=lambda x: setattr(game, 'turning', 1))
        btn_right.bind(on_release=lambda x: setattr(game, 'turning', 0))
        
        root.add_widget(btn_fwd)
        root.add_widget(btn_left)
        root.add_widget(btn_right)
        
        return root

if __name__ == '__main__':
    MazeApp().run()
