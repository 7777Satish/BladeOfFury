import pygame
import sys
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40
PLAYER_SPEED = 5
PROJECTILE_SPEED = 8
ATTACK_COOLDOWN = 500 

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blade Of Fury")
clock = pygame.time.Clock()

def load_images():
    images = {}
    
    player_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, BLUE, (0, 0, TILE_SIZE, TILE_SIZE))
    images['player'] = player_surface
    
    cannon_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(cannon_surface, GRAY, (0, 0, TILE_SIZE, TILE_SIZE))
    pygame.draw.circle(cannon_surface, BLACK, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//3)
    images['cannon'] = cannon_surface
    
    archer_tower_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(archer_tower_surface, BROWN, (0, 0, TILE_SIZE, TILE_SIZE))
    pygame.draw.polygon(archer_tower_surface, RED, 
                       [(TILE_SIZE//2, 0), (TILE_SIZE, TILE_SIZE//2), (TILE_SIZE//2, TILE_SIZE), (0, TILE_SIZE//2)])
    images['archer_tower'] = archer_tower_surface
    
    projectile_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(projectile_surface, RED, (5, 5), 5)
    images['projectile'] = projectile_surface
    
    return images

class GameObject:
    def __init__(self, x, y, image, health=100):
        self.x = x
        self.y = y
        self.image = image
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.health = health
        self.max_health = health
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, TILE_SIZE, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, TILE_SIZE * (self.health / self.max_health), 5))
    
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
    
    def is_destroyed(self):
        return self.health <= 0

class Player(GameObject):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, health=200)
        self.last_attack_time = 0
        self.attack_range = 100
    
    def move(self, dx, dy):
        self.x = max(0, min(SCREEN_WIDTH - TILE_SIZE, self.x + dx))
        self.y = max(0, min(SCREEN_HEIGHT - TILE_SIZE, self.y + dy))
        self.update()
    
    def attack(self, current_time, defenses):
        if current_time - self.last_attack_time < ATTACK_COOLDOWN:
            return False
        
        closest_defense = None
        min_distance = float('inf')
        
        for defense in defenses:
            if defense.is_destroyed():
                continue
            
            distance = math.sqrt((self.x - defense.x)**2 + (self.y - defense.y)**2)
            if distance <= self.attack_range and distance < min_distance:
                closest_defense = defense
                min_distance = distance
        
        if closest_defense:
            closest_defense.health -= 25
            self.last_attack_time = current_time
            return True
        
        return False

class Defense(GameObject):
    def __init__(self, x, y, image, defense_type, attack_range, damage, fire_rate):
        if defense_type == 'cannon':
            health = 150
        else:
            health = 100
        
        super().__init__(x, y, image, health)
        self.defense_type = defense_type
        self.attack_range = attack_range
        self.damage = damage
        self.fire_rate = fire_rate
        self.last_attack_time = 0
    
    def should_attack(self, current_time, player):
        if current_time - self.last_attack_time < self.fire_rate:
            return False
        
        distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        if distance <= self.attack_range:
            self.last_attack_time = current_time
            return True
        
        return False

class Projectile:
    def __init__(self, x, y, target_x, target_y, image, damage):
        self.x = x
        self.y = y
        self.image = image
        self.damage = damage
        
        dx = target_x - x
        dy = target_y - y
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        self.dx = (dx / distance) * PROJECTILE_SPEED
        self.dy = (dy / distance) * PROJECTILE_SPEED
        
        self.rect = pygame.Rect(x, y, 10, 10)
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def is_out_of_bounds(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)

class Level:
    def __init__(self, level_number, defense_count, images):
        self.level_number = level_number
        self.defenses = []
        self.create_defenses(defense_count, images)
    
    def create_defenses(self, count, images):
        for _ in range(count):
            defense_type = random.choice(['cannon', 'archer_tower'])
            
            if defense_type == 'cannon':
                x = random.randint(100, SCREEN_WIDTH - TILE_SIZE)
                y = random.randint(100, SCREEN_HEIGHT - TILE_SIZE)
                defense = Defense(x, y, images['cannon'], 'cannon', 200, 15, 1500)
            else:
                x = random.randint(100, SCREEN_WIDTH - TILE_SIZE)
                y = random.randint(100, SCREEN_HEIGHT - TILE_SIZE)
                defense = Defense(x, y, images['archer_tower'], 'archer_tower', 300, 10, 1000)
            
            self.defenses.append(defense)
    
    def is_completed(self):
        for defense in self.defenses:
            if not defense.is_destroyed():
                return False
        return True

class Game:
    def __init__(self):
        self.images = load_images()
        self.reset_game()
    
    def reset_game(self):
        self.player = Player(50, 50, self.images['player'])
        self.current_level = 1
        self.level = Level(self.current_level, 3, self.images)
        self.projectiles = []
        self.game_state = 'playing'
        self.level_transition_timer = 0
    
    def next_level(self):
        self.current_level += 1
        if self.current_level > 3:
            self.game_state = 'victory'
        else:
            self.level = Level(self.current_level, self.current_level + 2, self.images)
            self.player.health = min(self.player.max_health, self.player.health + 50)
            self.game_state = 'playing'
            self.player.x = 50
            self.player.y = 50
            self.player.update()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_state == 'level_complete':
                    if event.key == pygame.K_RETURN:
                        self.next_level()
                elif self.game_state == 'game_over' or self.game_state == 'victory':
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
    
    def update(self):
        if self.game_state != 'playing':
            return
        
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += PLAYER_SPEED
        self.player.move(dx, dy)
        
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            self.player.attack(current_time, self.level.defenses)
        
        current_time = pygame.time.get_ticks()
        for defense in self.level.defenses:
            if not defense.is_destroyed() and defense.should_attack(current_time, self.player):
                projectile = Projectile(
                    defense.x + TILE_SIZE//2, 
                    defense.y + TILE_SIZE//2,
                    self.player.x + TILE_SIZE//2,
                    self.player.y + TILE_SIZE//2,
                    self.images['projectile'],
                    defense.damage
                )
                self.projectiles.append(projectile)
        
        to_remove = []
        for i, projectile in enumerate(self.projectiles):
            projectile.update()
            
            if projectile.rect.colliderect(self.player.rect):
                self.player.health -= projectile.damage
                to_remove.append(i)
            
            if projectile.is_out_of_bounds():
                to_remove.append(i)
        
        for i in sorted(to_remove, reverse=True):
            if i < len(self.projectiles):
                self.projectiles.pop(i)
        
        if self.player.health <= 0:
            self.game_state = 'game_over'
        
        if self.level.is_completed():
            self.game_state = 'level_complete'
            self.level_transition_timer = pygame.time.get_ticks()
    
    def draw(self):
        screen.fill(WHITE)
        
        for defense in self.level.defenses:
            if not defense.is_destroyed():
                defense.draw(screen)
        
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        self.player.draw(screen)
        
        font = pygame.font.SysFont(None, 36)
        level_text = font.render(f"Level: {self.current_level}", True, BLACK)
        screen.blit(level_text, (10, 10))
        
        health_text = font.render(f"Health: {self.player.health}/{self.player.max_health}", True, BLACK)
        screen.blit(health_text, (10, 50))
        
        if self.game_state == 'level_complete':
            message = font.render("Level Complete! Press Enter to continue", True, GREEN)
            screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, SCREEN_HEIGHT//2))
        elif self.game_state == 'game_over':
            message = font.render("Game Over! Press Enter to restart", True, RED)
            screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, SCREEN_HEIGHT//2))
        elif self.game_state == 'victory':
            message = font.render("Victory! You completed all levels! Press Enter to play again", True, BLUE)
            screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, SCREEN_HEIGHT//2))
        
        pygame.display.flip()

def main():
    game = Game()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main()