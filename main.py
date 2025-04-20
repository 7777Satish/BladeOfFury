import pygame

pygame.init()

# Window dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Blade of Fury")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Game title
title_text = title_font.render("Blade of Fury", True, white)
title_rect = title_text.get_rect(center=(width // 2, height // 4))

# Button dimensions
button_width = 200
button_height = 50

# Button positions
start_button_rect = pygame.Rect((width - button_width) // 2, height // 2, button_width, button_height)
options_button_rect = pygame.Rect((width - button_width) // 2, height // 2 + 75, button_width, button_height)
quit_button_rect = pygame.Rect((width - button_width) // 2, height // 2 + 150, button_width, button_height)

# Button text
start_text = font.render("Start Game", True, black)
options_text = font.render("Options", True, black)
quit_text = font.render("Quit", True, black)

start_text_rect = start_text.get_rect(center=start_button_rect.center)
options_text_rect = options_text.get_rect(center=options_button_rect.center)
quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                
                player_width = 50
                player_height = 50
                player_x = width // 2 - player_width // 2
                player_y = height - 2 * player_height
                
                player_speed = 5
                player_image = pygame.image.load('assets/player_move.gif')
                player_image = pygame.transform.scale(player_image, (player_width, player_height))
                player_rect = player_image.get_rect()
                player_rect.topleft = (player_x, player_y)
                
                in_game = True
                while in_game:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            in_game = False
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_LEFT:
                                player_x -= player_speed
                            if event.key == pygame.K_RIGHT:
                                player_x += player_speed
                            if event.key == pygame.K_UP:
                                player_y -= player_speed
                            if event.key == pygame.K_DOWN:
                                player_y += player_speed

                            player_x = max(0, min(player_x, width - player_width))
                            player_y = max(0, min(player_y, height - player_height))
                            player_rect.topleft = (player_x, player_y)

                    screen.fill(gray)
                    screen.blit(player_image, player_rect)
                    pygame.display.flip()


            if options_button_rect.collidepoint(event.pos):
                print("Options clicked")
            if quit_button_rect.collidepoint(event.pos):
                running = False

    screen.fill(gray)
    screen.blit(title_text, title_rect)

    pygame.draw.rect(screen, white, start_button_rect)
    pygame.draw.rect(screen, white, options_button_rect)
    pygame.draw.rect(screen, white, quit_button_rect)

    screen.blit(start_text, start_text_rect)
    screen.blit(options_text, options_text_rect)
    screen.blit(quit_text, quit_text_rect)

    pygame.display.flip()

pygame.quit()