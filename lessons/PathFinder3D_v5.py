import pygame
import numpy as np
from math import sin, cos, pi
import random
import time
import os

# Initialize Pygame
pygame.init()
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Maze Runner")
clock = pygame.time.Clock()

# Set up mouse for FPS controls
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)  # Added sky blue color

# Try to load textures
try:
    WALL_TEXTURE = pygame.image.load('Assets/wall1.png')
    WALL_TEXTURE = pygame.transform.scale(WALL_TEXTURE, (64, 64))
    FLOOR_TEXTURE = pygame.image.load('Assets/wall3.png')
    FLOOR_TEXTURE = pygame.transform.scale(FLOOR_TEXTURE, (64, 64))
    USE_TEXTURE = True
except:
    USE_TEXTURE = False
    # Create procedural textures if image loading fails
    WALL_TEXTURE = pygame.Surface((64, 64))
    FLOOR_TEXTURE = pygame.Surface((64, 64))
    def create_brick_texture():
        texture = pygame.Surface((64, 64))
        texture.fill((139, 69, 19))
        for y in range(0, 64, 16):
            offset = 32 if (y // 16) % 2 == 0 else 0
            for x in range(-32 + offset, 64 + offset, 32):
                pygame.draw.rect(texture, (120, 60, 15), (x, y, 30, 14))
                pygame.draw.rect(texture, (160, 80, 20), (x, y, 30, 14), 1)
        return texture
    WALL_TEXTURE = create_brick_texture()
    FLOOR_TEXTURE = create_brick_texture()

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for x in range(width)] for y in range(height)]

    def generate(self):
        # Start from 1,1 to keep outer walls
        self._dfs(1, 1)
        # Set start and end points
        self.maze[1][1] = 2  # Start
        self.maze[self.height-2][self.width-2] = 3  # End
        return self.maze

    def _dfs(self, x, y):
        self.maze[y][x] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 < new_x < self.width-1 and
                0 < new_y < self.height-1 and
                self.maze[new_y][new_x] == 1):
                self.maze[y + dy//2][x + dx//2] = 0
                self._dfs(new_x, new_y)

class World:
    def __init__(self, size=15):
        self.size = size
        self.generator = MazeGenerator(size, size)
        self.map = self.generator.generate()
        self.coins = self.place_coins()
        self.total_coins = len(self.coins)

    def place_coins(self, num_coins=10):
        coins = set()
        paths = [(x, y) for y in range(self.size) for x in range(self.size)
                if self.map[y][x] == 0]
        random.shuffle(paths)
        return set(paths[:num_coins])

    def is_valid_move(self, x, y):
        map_x, map_y = int(x), int(y)
        return (0 <= map_x < self.size and
                0 <= map_y < self.size and
                self.map[map_y][map_x] != 1)

    def collect_coin(self, x, y):
        if (x, y) in self.coins:
            self.coins.remove((x, y))
            return True
        return False

    def is_finish(self, x, y):
        return self.map[y][x] == 3

    def cast_ray(self, x, y, angle):
        dist = 0
        ray_x = x
        ray_y = y
        dx = cos(angle) * 0.1
        dy = sin(angle) * 0.1

        while dist < 20:
            map_x = int(ray_x)
            map_y = int(ray_y)

            if (map_y < 0 or map_y >= self.size or
                map_x < 0 or map_x >= self.size or
                self.map[map_y][map_x] == 1):
                return dist, 1

            if self.map[map_y][map_x] == 3:
                return dist, 3

            ray_x += dx
            ray_y += dy
            dist += 0.1

        return dist, 0

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.angle = 0
        self.fov = pi/3
        self.base_speed = 0.1  # Normal walking speed
        self.sprint_speed = 0.2  # Running speed
        self.move_speed = self.base_speed
        self.mouse_sensitivity = 0.002
        self.coins_collected = 0

    def handle_mouse(self):
        rel_x, _ = pygame.mouse.get_rel()
        self.angle += rel_x * self.mouse_sensitivity
        self.angle %= 2 * pi

    def update_speed(self, sprinting):
        self.move_speed = self.sprint_speed if sprinting else self.base_speed

    def move(self, forward, strafe, world):
        next_x = self.x
        next_y = self.y

        if forward != 0:
            next_x += forward * self.move_speed * cos(self.angle)
            next_y += forward * self.move_speed * sin(self.angle)

        if strafe != 0:
            next_x += strafe * self.move_speed * cos(self.angle + pi/2)
            next_y += strafe * self.move_speed * sin(self.angle + pi/2)

        if world.is_valid_move(next_x, next_y):
            self.x, self.y = next_x, next_y
            if world.collect_coin(int(self.x), int(self.y)):
                self.coins_collected += 1
            return world.is_finish(int(self.x), int(self.y))
        return False

def draw_minimap(screen, world, player, minimap_size=200):
    padding = 20
    cell_size = minimap_size // world.size
    minimap_surface = pygame.Surface((minimap_size, minimap_size))
    minimap_surface.fill(BLACK)
    minimap_surface.set_alpha(128)  # More translucent (changed from 200 to 128)

    # Draw maze
    for y in range(world.size):
        for x in range(world.size):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if world.map[y][x] == 1:  # Wall
                pygame.draw.rect(minimap_surface, WHITE, rect)
            elif world.map[y][x] == 2:  # Start
                pygame.draw.rect(minimap_surface, GREEN, rect)
            elif world.map[y][x] == 3:  # End
                pygame.draw.rect(minimap_surface, RED, rect)
            else:  # Path
                pygame.draw.rect(minimap_surface, GRAY, rect, 1)

    # Draw coins
    for coin_x, coin_y in world.coins:
        pygame.draw.circle(minimap_surface, YELLOW,
                         (int(coin_x * cell_size + cell_size/2),
                          int(coin_y * cell_size + cell_size/2)),
                         cell_size//4)

    # Draw player position and direction
    player_x = int(player.x * cell_size)
    player_y = int(player.y * cell_size)
    pygame.draw.circle(minimap_surface, BLUE, (player_x, player_y), cell_size//3)
    end_x = player_x + cos(player.angle) * cell_size
    end_y = player_y + sin(player.angle) * cell_size
    pygame.draw.line(minimap_surface, BLUE, (player_x, player_y), (end_x, end_y), 2)

    screen.blit(minimap_surface, (SCREEN_WIDTH - minimap_size - padding, padding))

def draw_hud(screen, player, elapsed_time, game_completed):
    font = pygame.font.Font(None, 36)
    hud_surface = pygame.Surface((200, 80))
    hud_surface.fill(BLACK)
    hud_surface.set_alpha(200)

    # Only update time if game is not completed
    time_text = font.render(f"Time: {elapsed_time}s", True, WHITE)
    coins_text = font.render(f"Coins: {player.coins_collected}", True, YELLOW)

    padding = 20
    screen.blit(hud_surface, (padding, padding))
    screen.blit(time_text, (padding + 10, padding + 10))
    screen.blit(coins_text, (padding + 10, padding + 40))

def render_wall_slice(screen, x, start_pos, height, distance, wall_x):
    if USE_TEXTURE or True:
        # Calculate texture coordinates with improved precision
        tex_x = int((wall_x * WALL_TEXTURE.get_width() * 2) % WALL_TEXTURE.get_width())
        wall_slice = pygame.Surface((2, WALL_TEXTURE.get_height()))  # Increased width to 2
        wall_slice.blit(WALL_TEXTURE, (0, 0), (tex_x, 0, 2, WALL_TEXTURE.get_height()))

        if height > 0:
            # Scale with improved smoothing
            wall_slice = pygame.transform.smoothscale(wall_slice, (2, int(height)))

            # Enhanced shading with smoother falloff
            shade = max(0, min(255, 255 - int(distance * 15)))  # Reduced distance multiplier
            shadow_surface = pygame.Surface(wall_slice.get_size())
            shadow_surface.fill((shade, shade, shade))
            wall_slice.blit(shadow_surface, (0, 0), special_flags=pygame.BLEND_MULT)

            # Apply anti-aliasing effect
            if x > 0:  # Not the first column
                # Blend with previous column for smoother transition
                pygame.draw.line(screen, (0, 0, 0),
                               (x, start_pos),
                               (x, start_pos + height),
                               1)

            screen.blit(wall_slice, (x, start_pos))
    else:
        # Improved fallback rendering
        color = max(0, min(255, 255 - int(distance * 15)))
        pygame.draw.rect(screen, (color, color, color),
                        (x, start_pos, 2, height))  # Use rect instead of line

def main():
    world = World(15)
    player = Player(1.5, 1.5)
    running = True
    start_time = time.time()
    end_time = None
    game_completed = False

    pygame.mouse.set_pos(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    pygame.mouse.get_rel()

    while running:
        # Fix: Changed event handling to use pygame.event.get() instead of key.get_pressed()
        for event in pygame.event.get():  # Changed this line
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and game_completed:
                    running = False
                elif event.key == pygame.K_r and game_completed:
                    world = World(15)
                    player = Player(1.5, 1.5)
                    start_time = time.time()
                    end_time = None
                    game_completed = False
                    pygame.mouse.set_pos(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                    pygame.mouse.get_rel()

        if not game_completed:
            player.handle_mouse()
            keys = pygame.key.get_pressed()  # This is the correct way to get pressed keys
            forward = 0
            strafe = 0
            sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            player.update_speed(sprinting)

            if keys[pygame.K_w]: forward += 1
            if keys[pygame.K_s]: forward -= 1
            if keys[pygame.K_a]: strafe -= 1
            if keys[pygame.K_d]: strafe += 1

            if forward != 0 or strafe != 0:
                game_completed = player.move(forward, strafe, world)
                if game_completed:
                    end_time = time.time()

        # Clear screen and draw sky
        screen.fill(SKY_BLUE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        screen.fill(GRAY, (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))

        # Render 3D view with improved smoothing
        num_rays = SCREEN_WIDTH // 2  # Reduce number of rays for wider slices
        for i in range(num_rays):
            x = i * 2  # Double the x increment for wider slices
            ray_angle = (player.angle - player.fov/2) + (i/num_rays) * player.fov

            # Add slight angle interpolation for smoother transitions
            dist, wall_type = world.cast_ray(player.x, player.y, ray_angle)
            if i > 0:
                prev_dist, _ = world.cast_ray(player.x, player.y, ray_angle - player.fov/(num_rays*2))
                dist = (dist + prev_dist) / 2  # Average with previous distance

            wall_height = min(SCREEN_HEIGHT, (SCREEN_HEIGHT / (dist + 0.0001)))
            start_pos = (SCREEN_HEIGHT - wall_height) // 2

            ray_x = player.x + cos(ray_angle) * dist
            ray_y = player.y + sin(ray_angle) * dist
            wall_x = ray_x - int(ray_x) if cos(ray_angle) <= 0 else 1 - (ray_x - int(ray_x))

            if wall_type == 3:
                color = max(0, min(255, 255 - int(dist * 15)))
                pygame.draw.rect(screen, (color, 0, 0),
                               (x, start_pos, 2, wall_height))
            else:
                render_wall_slice(screen, x, start_pos, wall_height, dist, wall_x)

        # Calculate elapsed time based on game state
        elapsed_time = int(end_time - start_time if end_time else time.time() - start_time)

        draw_minimap(screen, world, player)
        draw_hud(screen, player, elapsed_time, game_completed)

        if game_completed:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)

            font = pygame.font.Font(None, 48)
            win_text = font.render(f"Maze Completed in {elapsed_time}s! Press R to restart or Q to quit", True, GREEN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(win_text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    pygame.quit()

if __name__ == "__main__":
    main()