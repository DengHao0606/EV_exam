import pygame
import random
import sys
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏窗口设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 80
FPS = 30

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 创建游戏窗口
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('植物大战僵尸简化版')
clock = pygame.time.Clock()

# 加载图像（这里用简单图形代替）
def create_simple_surface(color, width, height):
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return surface

# 游戏资源
SUN_IMG = create_simple_surface(YELLOW, 40, 40)
PEASHOOTER_IMG = create_simple_surface(GREEN, 60, 60)
ZOMBIE_IMG = create_simple_surface(BROWN, 50, 80)
PEA_IMG = create_simple_surface(GREEN, 20, 20)
LAWN_BG = create_simple_surface((124, 252, 0), WINDOW_WIDTH, WINDOW_HEIGHT)

# 游戏字体
font = pygame.font.SysFont('Arial', 24)

class Sun:
    def __init__(self):
        self.x = random.randint(50, WINDOW_WIDTH - 50)
        self.y = 0
        self.speed = 2
        self.collected = False
        self.rect = pygame.Rect(self.x, self.y, 40, 40)
        self.fall_end_y = random.randint(100, 300)
    
    def update(self):
        if not self.collected and self.y < self.fall_end_y:
            self.y += self.speed
            self.rect.y = self.y
    
    def draw(self, surface):
        if not self.collected:
            surface.blit(SUN_IMG, (self.x, self.y))
    
    def collect(self, pos):
        if not self.collected and self.rect.collidepoint(pos):
            self.collected = True
            return 25
        return 0

class Plant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.rect = pygame.Rect(x, y, 60, 60)
        self.shoot_timer = 0
    
    def update(self):
        self.shoot_timer += 1
    
    def draw(self, surface):
        surface.blit(PEASHOOTER_IMG, (self.x, self.y))
    
    def can_shoot(self):
        return self.shoot_timer >= 60  # 每60帧射击一次
    
    def reset_shoot_timer(self):
        self.shoot_timer = 0

class Pea:
    def __init__(self, x, y):
        self.x = x
        self.y = y + 20
        self.speed = 5
        self.damage = 20
        self.rect = pygame.Rect(self.x, self.y, 20, 20)
    
    def update(self):
        self.x += self.speed
        self.rect.x = self.x
        return self.x > WINDOW_WIDTH
    
    def draw(self, surface):
        surface.blit(PEA_IMG, (self.x, self.y))

class Zombie:
    def __init__(self, row):
        self.x = WINDOW_WIDTH
        self.y = 100 + row * GRID_SIZE
        self.speed = 1
        self.health = 100
        self.damage = 0.5
        self.rect = pygame.Rect(self.x, self.y, 50, 80)
        self.row = row
    
    def update(self):
        self.x -= self.speed
        self.rect.x = self.x
        return self.x < -50
    
    def draw(self, surface):
        surface.blit(ZOMBIE_IMG, (self.x, self.y))
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

class Game:
    def __init__(self):
        self.plants = []
        self.zombies = []
        self.peas = []
        self.suns = []
        self.sun_count = 100
        self.selected_plant = None
        self.game_over = False
        self.zombie_spawn_timer = 0
        self.sun_spawn_timer = 0
        self.rows = 5
        self.cols = 9
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
    
    def spawn_sun(self):
        self.sun_spawn_timer += 1
        if self.sun_spawn_timer >= 300:  # 每300帧生成一个阳光
            self.suns.append(Sun())
            self.sun_spawn_timer = 0
    
    def spawn_zombie(self):
        self.zombie_spawn_timer += 1
        if self.zombie_spawn_timer >= 600:  # 每600帧生成一个僵尸
            row = random.randint(0, self.rows - 1)
            self.zombies.append(Zombie(row))
            self.zombie_spawn_timer = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # 收集阳光
                for sun in self.suns[:]:
                    sun_value = sun.collect(pos)
                    if sun_value > 0:
                        self.sun_count += sun_value
                        self.suns.remove(sun)
                
                # 检查是否点击了植物选择区域
                if 10 <= pos[0] <= 70 and 10 <= pos[1] <= 70:
                    self.selected_plant = "peashooter"
                
                # 种植植物
                if self.selected_plant:
                    grid_x = pos[0] // GRID_SIZE
                    grid_y = (pos[1] - 100) // GRID_SIZE
                    
                    if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
                        if self.grid[grid_y][grid_x] is None and self.sun_count >= 100:
                            plant_x = grid_x * GRID_SIZE
                            plant_y = 100 + grid_y * GRID_SIZE
                            self.plants.append(Plant(plant_x, plant_y))
                            self.grid[grid_y][grid_x] = "plant"
                            self.sun_count -= 100
    
    def update(self):
        if self.game_over:
            return
        
        # 生成阳光和僵尸
        self.spawn_sun()
        self.spawn_zombie()
        
        # 更新阳光
        for sun in self.suns[:]:
            sun.update()
        
        # 更新植物和豌豆射击
        for plant in self.plants[:]:
            plant.update()
            if plant.can_shoot():
                grid_x = plant.x // GRID_SIZE
                grid_y = (plant.y - 100) // GRID_SIZE
                
                # 检查这一行是否有僵尸
                for zombie in self.zombies:
                    if zombie.row == grid_y and zombie.x > plant.x:
                        self.peas.append(Pea(plant.x + 50, plant.y))
                        plant.reset_shoot_timer()
                        break
        
        # 更新豌豆
        for pea in self.peas[:]:
            if pea.update():  # 如果豌豆飞出屏幕
                self.peas.remove(pea)
                continue
            
            # 检查豌豆是否击中僵尸
            for zombie in self.zombies[:]:
                if pea.rect.colliderect(zombie.rect):
                    if zombie.take_damage(pea.damage):
                        self.zombies.remove(zombie)
                    self.peas.remove(pea)
                    break
        
        # 更新僵尸
        for zombie in self.zombies[:]:
            if zombie.update():  # 如果僵尸走出屏幕
                self.game_over = True
                break
            
            # 检查僵尸是否碰到植物
            grid_x = (zombie.x + 50) // GRID_SIZE
            grid_y = zombie.row
            
            if 0 <= grid_x < self.cols and self.grid[grid_y][grid_x] == "plant":
                # 找到被攻击的植物
                for plant in self.plants[:]:
                    if (plant.x // GRID_SIZE == grid_x and 
                        (plant.y - 100) // GRID_SIZE == grid_y):
                        plant.health -= zombie.damage
                        if plant.health <= 0:
                            self.plants.remove(plant)
                            self.grid[grid_y][grid_x] = None
                        break
    
    def draw(self):
        # 绘制背景
        window.blit(LAWN_BG, (0, 0))
        
        # 绘制网格线
        for row in range(self.rows + 1):
            pygame.draw.line(window, BLACK, (0, 100 + row * GRID_SIZE), 
                           (WINDOW_WIDTH, 100 + row * GRID_SIZE), 2)
        
        for col in range(self.cols + 1):
            pygame.draw.line(window, BLACK, (col * GRID_SIZE, 100), 
                           (col * GRID_SIZE, WINDOW_HEIGHT), 2)
        
        # 绘制阳光数量
        sun_text = font.render(f"阳光: {self.sun_count}", True, BLACK)
        window.blit(sun_text, (WINDOW_WIDTH - 150, 20))
        
        # 绘制植物选择区域
        pygame.draw.rect(window, GREEN, (10, 10, 60, 60))
        plant_text = font.render("100", True, BLACK)
        window.blit(plant_text, (25, 35))
        
        # 绘制阳光
        for sun in self.suns:
            sun.draw(window)
        
        # 绘制植物
        for plant in self.plants:
            plant.draw(window)
        
        # 绘制豌豆
        for pea in self.peas:
            pea.draw(window)
        
        # 绘制僵尸
        for zombie in self.zombies:
            zombie.draw(window)
        
        # 游戏结束提示
        if self.game_over:
            game_over_text = font.render("游戏结束! 按R键重新开始", True, BLACK)
            window.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        
        pygame.display.update()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)
            
            # 重新开始游戏
            keys = pygame.key.get_pressed()
            if keys[K_r] and self.game_over:
                self.__init__()

# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.run()