import pygame
import random
import sys
import math

pygame.init()

# Screen size
SCREEN_WIDTH = 680
SCREEN_HEIGHT = 680

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()
FPS = 60

# Bird
bird_width = 50
bird_height = 35
bird_x = 60
gravity = 0.6
flap_strength = -10

# Pipes
pipe_width = 80
pipe_gap = 180
pipe_velocity = 4

# Sounds
flap_sound = pygame.mixer.Sound('Flappy Bird/Sounds/wing.ogg')
point_sound = pygame.mixer.Sound('Flappy Bird/Sounds/point.ogg')
hit_sound = pygame.mixer.Sound('Flappy Bird/Sounds/hit.ogg')
game_over_sound = pygame.mixer.Sound('Flappy Bird/Sounds/die.ogg')

# Pipe img
pipe_img = pygame.image.load('Flappy Bird/Sprites/pipe-green.png').convert_alpha()
pipe_img = pygame.transform.scale(pipe_img, (pipe_width, 500))

# Background img
bg_image = pygame.image.load('Flappy Bird/Sprites/background-day.png').convert()
bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Bird imgs
bird_imgs = [
    pygame.image.load('Flappy Bird/Sprites/yellowbird-upflap.png').convert_alpha(),
    pygame.image.load('Flappy Bird/Sprites/yellowbird-midflap.png').convert_alpha(),
    pygame.image.load('Flappy Bird/Sprites/yellowbird-downflap.png').convert_alpha()
]
bird_imgs = [pygame.transform.scale(img, (bird_width, bird_height)) for img in bird_imgs]

# Ground img
ground_height = 100
ground_img = pygame.image.load('Flappy Bird/Sprites/base.png').convert_alpha()
ground_img = pygame.transform.scale(ground_img, (SCREEN_WIDTH, ground_height))

# Number imgs
digit_imgs = {}
for i in range(10):
    img = pygame.image.load(f'Flappy Bird/Sprites/{i}.png').convert_alpha()
    img = pygame.transform.scale(img, (30, 45))
    digit_imgs[str(i)] = img

# Game Over img
gameover_img = pygame.image.load('Flappy Bird/Sprites/gameover.png').convert_alpha()
gameover_img = pygame.transform.scale(gameover_img, (300, 80))

# Message img
get_ready = pygame.image.load('Flappy Bird/Sprites/message.png').convert_alpha()
get_ready = pygame.transform.scale(get_ready, (300, 400))

# Restart button
restart_img = pygame.image.load('Flappy Bird/Sprites/PlayButton.png').convert_alpha()
restart_img = pygame.transform.scale(restart_img, (100, 60))

restart_rect = restart_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))

def create_pipe():
    height = random.randint(150, SCREEN_HEIGHT - pipe_gap - 150)
    top_rect = pygame.Rect(SCREEN_WIDTH, 0, pipe_width, height)
    bottom_rect = pygame.Rect(SCREEN_WIDTH, height + pipe_gap, pipe_width, SCREEN_HEIGHT)

    return (top_rect, True), (bottom_rect, False) 

def move_pipes(pipes):
    new_pipes = []
    for pipe, is_top in pipes:
        pipe.x -= pipe_velocity
        if pipe.right > 0:
            new_pipes.append((pipe, is_top))
    return new_pipes

    '''
    for pipe in pipes:
        pipe.x -= pipe_velocity
    return [pipe for pipe in pipes if pipe.right > 0]
    '''

def bird_rotation(image, velocity, force_angle = None):
    if force_angle is not None:
        angle = force_angle
    else:
        angle = max(min(-velocity * 3, 25), -90)
    return pygame.transform.rotate(image, angle)

def drawing(bird, pipes, score, bird_frame, bird_velocity, bg_x, ground_x, ground_y, show_score = True, force_bird_angle = None, flash_timer = 0, flash_duration = 8):
    # Background
    screen.blit(bg_image, (bg_x,0))
    screen.blit(bg_image, (bg_x + SCREEN_WIDTH, 0)) 

    # Pipes
    for pipe, is_top in pipes:
        if is_top:
            pipe_img_rotated = pygame.transform.flip(pipe_img, False, True)
            screen.blit(pipe_img_rotated, (pipe.x, pipe.bottom - pipe_img_rotated.get_height()))
        else:
            screen.blit(pipe_img, (pipe.x, pipe.y))

    # Bird
    #! screen.blit(bird_imgs[bird_frame], (bird.x, bird.y))
    rotate_bird = bird_rotation(bird_imgs[bird_frame], bird_velocity, force_angle = force_bird_angle)
    bird_rect = rotate_bird.get_rect(center = (bird.x + bird_width // 2, bird.y + bird_height // 2))
    screen.blit(rotate_bird, bird_rect.topleft)

    # Ground
    screen.blit(ground_img, (ground_x, ground_y))
    screen.blit(ground_img, (ground_x + SCREEN_WIDTH, ground_y))

    # Scoring
    if show_score:
        score_str = str(score)
        total_width = sum(digit_imgs[d].get_width() for d in score_str)
        x = SCREEN_WIDTH // 2 - total_width // 2
        for d in score_str:
            screen.blit(digit_imgs[d], (x, 30))
            x += digit_imgs[d].get_width()
    
    # Flash effect (when bird dies)
    if flash_timer > 0:
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        alpha = int((flash_timer / flash_duration) * 255)
        flash_surface.set_alpha(alpha)
        flash_surface.fill((255, 255, 255))
        screen.blit(flash_surface, (0, 0))

    pygame.display.update()

def game_over(score):
    screen.blit(gameover_img, (SCREEN_WIDTH // 2 - gameover_img.get_width() // 2, SCREEN_HEIGHT // 2 - 150))

    score_str = str(score)
    total_width = sum(digit_imgs[d].get_width() for d in score_str)
    x = SCREEN_WIDTH // 2 - total_width // 2
    for d in score_str:
        screen.blit(digit_imgs[d], (x, SCREEN_HEIGHT // 2 - 30))
        x += digit_imgs[d].get_width()

    screen.blit(restart_img, restart_rect.topleft)
    
    pygame.display.update()

def restart():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
        clock.tick(30)


def start():
    get_ready_img = get_ready
    idle_bird_img = bird_imgs[1]
    bird_x = 60
    bird_base_y = SCREEN_HEIGHT // 2 + 20

    ground_y = SCREEN_HEIGHT - ground_height
    ground_x = 0
    ground_speed = pipe_velocity

    bg_x = 0
    bg_speed = 0.5

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True, bg_x, ground_x
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True, bg_x, ground_x

        float_offset = 5 * math.sin(pygame.time.get_ticks() * 0.005)
        bird_y = bird_base_y + float_offset

        ground_x -= ground_speed
        if ground_x <= -SCREEN_WIDTH:
            ground_x = 0

        bg_x -= bg_speed
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0

        screen.blit(bg_image, (bg_x, 0))
        screen.blit(bg_image, (bg_x + SCREEN_WIDTH, 0))
        screen.blit(get_ready_img, (SCREEN_WIDTH // 2 - get_ready_img.get_width() // 2, 100))
        screen.blit(idle_bird_img, (bird_x, bird_y))
        screen.blit(ground_img, (ground_x, ground_y))
        screen.blit(ground_img, (ground_x + SCREEN_WIDTH, ground_y))

        pygame.display.update()
        clock.tick(60)


def main(initial_flap = False, bg_x = 0, ground_x = 0):
    bird_y = SCREEN_HEIGHT // 2
    bird_velocity = 0
    bird_frame = 0  
    frame_count = 0  
    bird = pygame.Rect(bird_x, bird_y, bird_width, bird_height)

    #!bg_x = 0
    bg_speed = 0.5

    #!ground_x = 0
    ground_y = SCREEN_HEIGHT - ground_height
    ground_speed = pipe_velocity 

    pipes = []
    passed_pipes = []
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1300)
    score = 0
    dead = False
    play_game_over_sound = False
    
    hit_ani_time = 50
    hit_bounce = False

    transition_angle = 50
    transition_duration = 20
    transition_frame = 0

    flash_duration = 8
    flash_timer = 0

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not dead:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    bird_velocity = flap_strength
                    flap_sound.play()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird_velocity = flap_strength
                        flap_sound.play()
            if event.type == SPAWNPIPE and not dead:
                pipes.extend(create_pipe())

        bird_velocity += gravity
        bird.y += int(bird_velocity)

        frame_count += 1
        if frame_count % 5 == 0:
            bird_frame = (bird_frame + 1) % 3

        if not dead:
            pipes = move_pipes(pipes)
            bg_x -= bg_speed
            if bg_x <= -SCREEN_WIDTH:
                bg_x = 0

            ground_x -= ground_speed
            if ground_x <= -SCREEN_WIDTH:
                ground_x = 0

            for pipe, _ in pipes:
                if bird.colliderect(pipe):
                    if not play_game_over_sound:
                        hit_sound.play()
                        game_over_sound.play()
                        play_game_over_sound = True
                    dead = True
                    hit_ani_time = 30
                    flash_timer = flash_duration
                    break

            if bird.bottom >= ground_y:
                if not play_game_over_sound:
                    hit_sound.play()
                    game_over_sound.play()
                    play_game_over_sound = True
                dead = True
                hit_ani_time = 0
                flash_timer = flash_duration

            for pipe, is_top in pipes:
                if pipe.right < bird.left and pipe not in passed_pipes:
                    passed_pipes.append(pipe)

                    if not is_top:
                        top_y = pipe.y - pipe_gap
                        bottom_y = pipe.y

                        if bird.top > top_y and bird.bottom < bottom_y:
                            score += 1
                            point_sound.play()
                        else:
                            if not play_game_over_sound:
                                hit_sound.play()
                                game_over_sound.play()
                                play_game_over_sound = True
                            dead = True
                            hit_ani_time = 0
                            flash_timer = flash_duration

        else:
            if hit_ani_time > 0:
                hit_ani_time -= 1
            else:
                bird_velocity += gravity
                bird.y += int(bird_velocity)

                if bird.bottom >= ground_y:
                    bird.bottom = ground_y
                    if flash_timer <= 0:
                        running = False
                pygame.time.delay(10)

        force_bird_angle = None
        if dead:
            if hit_ani_time > 0:
                progress = transition_frame / transition_duration
                ease = 1 - (1 - progress) ** 2
                force_bird_angle = (1 - ease) * transition_angle
                transition_frame += 1
                hit_ani_time -= 1

                if not hit_bounce:
                    bird_velocity = -5
                    bird.y += int(bird_velocity)
                    hit_bounce = True

            else:
                force_bird_angle = None
                bird_velocity += gravity
                bird.y += int(bird_velocity)

                if bird.bottom >= ground_y:
                    bird.bottom = ground_y
                    if flash_timer <= 0:
                        running = False

        if initial_flap:
            bird_velocity = flap_strength
            flap_sound.play()
            initial_flap = False

        if flash_timer > 0:
            flash_timer -= 1

        drawing(bird, pipes, int(score), bird_frame, bird_velocity, bg_x, ground_x, ground_y, show_score = True, force_bird_angle=force_bird_angle, flash_timer=flash_timer, flash_duration=flash_duration)
        
    # Game over
    drawing(bird, pipes, int(score), bird_frame, bird_velocity, bg_x, ground_x, ground_y, show_score = False, force_bird_angle=force_bird_angle, flash_timer=flash_timer, flash_duration=flash_duration)
    game_over(int(score))
    if restart():
        flap_requested, bg_x, ground_x = start()
        main(initial_flap = flap_requested, bg_x = bg_x, ground_x = ground_x)

if __name__ == "__main__":
    while True:
        flap_requested, bg_x, ground_x = start()
        main(initial_flap = flap_requested, bg_x = bg_x, ground_x = ground_x)

