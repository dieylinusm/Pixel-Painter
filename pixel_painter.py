import asyncio
import platform
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the game window
width = 600
height = 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pixel Painter")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow

# Player properties
brush_size = 10
brush_x = width // 2
brush_y = height // 2
brush_speed = 4
brush_color = random.choice(colors)

# Obstacle properties
obstacle_size = 15
obstacle_speed = 2
obstacles = []
spawn_rate = 0.03  # Probability of spawning per frame

# Game variables
score = 0
health = 3
game_time = 30  # Game duration in seconds
start_time = pygame.time.get_ticks() // 1000
running = True
painted_pixels = set()  # Track painted coordinates

# Function to create a new obstacle
def create_obstacle():
    x = random.randint(0, width - obstacle_size)
    y = random.randint(0, height - obstacle_size)
    return {'x': x, 'y': y}

# Setup function for initialization
def setup():
    global brush_x, brush_y, brush_color, obstacles, score, health, start_time, running, painted_pixels
    brush_x = width // 2
    brush_y = height // 2
    brush_color = random.choice(colors)
    obstacles = []
    score = 0
    health = 3
    start_time = pygame.time.get_ticks() // 1000
    running = True
    painted_pixels = set()
    window.fill(black)
    pygame.display.update()

# Update loop for game logic
async def update_loop():
    global brush_x, brush_y, brush_color, obstacles, score, health, running

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

    # Handle brush movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and brush_x > 0:
        brush_x -= brush_speed
    if keys[pygame.K_RIGHT] and brush_x < width - brush_size:
        brush_x += brush_speed
    if keys[pygame.K_UP] and brush_y > 0:
        brush_y -= brush_speed
    if keys[pygame.K_DOWN] and brush_y < height - brush_size:
        brush_y += brush_speed

    # Add painted pixels
    painted_pixels.add((int(brush_x), int(brush_y)))
    score = len(painted_pixels) // 10  # Score based on painted area

    # Spawn obstacles
    if random.random() < spawn_rate:
        obstacles.append(create_obstacle())

    # Update obstacle positions (move toward player)
    for obstacle in obstacles[:]:
        dx = brush_x - obstacle['x']
        dy = brush_y - obstacle['y']
        distance = math.hypot(dx, dy)
        if distance > 0:
            obstacle['x'] += (dx / distance) * obstacle_speed
            obstacle['y'] += (dy / distance) * obstacle_speed

    # Check for collisions
    brush_rect = pygame.Rect(brush_x, brush_y, brush_size, brush_size)
    for obstacle in obstacles[:]:
        obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], obstacle_size, obstacle_size)
        if brush_rect.colliderect(obstacle_rect):
            health -= 1
            obstacles.remove(obstacle)
            brush_color = random.choice(colors)  # Change color on hit
            if health <= 0:
                return False

    # Check time limit
    current_time = pygame.time.get_ticks() // 1000
    if current_time - start_time >= game_time:
        return False

    # Draw the screen
    window.fill(black)
    for pixel in painted_pixels:
        pygame.draw.rect(window, brush_color, (pixel[0], pixel[1], 1, 1))  # Draw painted pixels
    pygame.draw.rect(window, brush_color, (brush_x, brush_y, brush_size, brush_size))  # Draw brush
    for obstacle in obstacles:
        pygame.draw.rect(window, red, (obstacle['x'], obstacle['y'], obstacle_size, obstacle_size))  # Draw obstacles
    pygame.display.set_caption(f"Pixel Painter - Score: {score} | Health: {health} | Time: {game_time - (current_time - start_time)}")
    pygame.display.update()

    return True

# Main game loop
FPS = 60

async def main():
    setup()
    global running
    while running:
        running = await update_loop()
        await asyncio.sleep(1.0 / FPS)

    # Game over message
    font = pygame.font.Font(None, 36)
    text = font.render(f"Game Over - Score: {score}", True, white)
    window.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
    pygame.display.update()
    await asyncio.sleep(2)  # Wait 2 seconds
    pygame.quit()

# Run the game based on platform
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
