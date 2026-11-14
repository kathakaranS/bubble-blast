
import pygame
import math
import random
import sys

pygame.init()

# -------------------- GAME SETTINGS --------------------

WIDTH, HEIGHT = 850, 750
FPS = 60
TIME_LIMIT = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BUBBLE BLAST - Fruit Shooter")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 25, 40)
DARK_BLUE = (12, 22, 48)
BLUE = (40, 100, 190)
LIGHT_BLUE = (100, 190, 255)
GOLD = (255, 205, 65)
RED = (245, 65, 75)
GREEN = (65, 205, 100)

# Fonts
font = pygame.font.SysFont("arial", 23, bold=True)
small_font = pygame.font.SysFont("arial", 17)
big_font = pygame.font.SysFont("arial", 55, bold=True)

# Fruit types
FRUITS = ["apple", "orange", "strawberry", "green", "grapes"]

FRUIT_COLORS = {
    "apple": (225, 45, 55),
    "orange": (255, 145, 25),
    "strawberry": (240, 45, 100),
    "green": (105, 205, 65),
    "grapes": (145, 75, 205)
}

# Grid settings
RADIUS = 23
DIAMETER = RADIUS * 2
COLS = 16
ROWS = 14
GRID_TOP = 125
GRID_LEFT = 40
ROW_HEIGHT = 42
DANGER_LINE = 610

# Shooter
SHOOTER_X = WIDTH // 2
SHOOTER_Y = 680
BULLET_SPEED = 10

# -------------------- GAME VARIABLES --------------------

grid = []
particles = []
projectile = None

score = 0
level = 1
time_left = TIME_LIMIT

current_fruit = random.choice(FRUITS)
next_fruit = random.choice(FRUITS)

paused = False
game_over = False
won = False

# -------------------- HELPER FUNCTIONS --------------------

def text_center(text, font_obj, color, x, y):
    image = font_obj.render(str(text), True, color)
    rect = image.get_rect(center=(x, y))
    screen.blit(image, rect)


def get_position(row, col):
    x = GRID_LEFT + col * DIAMETER + RADIUS

    if row % 2 == 1:
        x += RADIUS

    y = GRID_TOP + row * ROW_HEIGHT

    return int(x), int(y)


def create_grid():
    board = []

    for row in range(7):
        line = []

        for col in range(COLS):
            line.append(random.choice(FRUITS))

        board.append(line)

    for row in range(7, ROWS):
        board.append([None] * COLS)

    return board


def get_neighbors(row, col):
    if row % 2 == 0:
        offsets = [
            (0, -1), (0, 1),
            (-1, -1), (-1, 0),
            (1, -1), (1, 0)
        ]
    else:
        offsets = [
            (0, -1), (0, 1),
            (-1, 0), (-1, 1),
            (1, 0), (1, 1)
        ]

    neighbors = []

    for dr, dc in offsets:
        nr = row + dr
        nc = col + dc

        if 0 <= nr < ROWS and 0 <= nc < COLS:
            neighbors.append((nr, nc))

    return neighbors


def find_matches(row, col, fruit):
    found = set()
    stack = [(row, col)]

    while stack:
        r, c = stack.pop()

        if (r, c) in found:
            continue

        if not (0 <= r < ROWS and 0 <= c < COLS):
            continue

        if grid[r][c] != fruit:
            continue

        found.add((r, c))

        for nr, nc in get_neighbors(r, c):
            if (nr, nc) not in found:
                stack.append((nr, nc))

    return found


def remove_floating():
    connected = set()
    stack = []

    for col in range(COLS):
        if grid[0][col] is not None:
            stack.append((0, col))

    while stack:
        row, col = stack.pop()

        if (row, col) in connected:
            continue

        if grid[row][col] is None:
            continue

        connected.add((row, col))

        for nr, nc in get_neighbors(row, col):
            if (nr, nc) not in connected:
                stack.append((nr, nc))

    removed = 0

    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] is not None and (row, col) not in connected:
                x, y = get_position(row, col)
                create_particles(x, y, FRUIT_COLORS[grid[row][col]])
                grid[row][col] = None
                removed += 1

    return removed


def create_particles(x, y, color):
    for _ in range(8):
        particles.append({
            "x": float(x),
            "y": float(y),
            "dx": random.uniform(-3, 3),
            "dy": random.uniform(-4, 2),
            "life": 30,
            "color": color
        })


def update_particles():
    for particle in particles[:]:
        particle["x"] += particle["dx"]
        particle["y"] += particle["dy"]
        particle["dy"] += 0.12
        particle["life"] -= 1

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_particles():
    for particle in particles:
        pygame.draw.circle(
            screen,
            particle["color"],
            (int(particle["x"]), int(particle["y"])),
            4
        )


# -------------------- FRUIT DRAWING --------------------

def draw_fruit(surface, fruit, x, y, radius):
    x = int(x)
    y = int(y)
    radius = int(radius)

    color = FRUIT_COLORS[fruit]

    # Fruit shadow
    pygame.draw.circle(
        surface,
        (15, 20, 35),
        (x + 3, y + 4),
        radius
    )

    # Main fruit body
    pygame.draw.circle(surface, color, (x, y), radius)

    # Fruit highlights
    pygame.draw.circle(
        surface,
        tuple(min(255, c + 55) for c in color),
        (x - radius // 3, y - radius // 3),
        max(3, radius // 4)
    )

    if fruit == "apple":
        pygame.draw.ellipse(
            surface,
            color,
            (x - radius + 3, y - radius // 2,
             radius * 2 - 6, radius + 8)
        )
        pygame.draw.line(
            surface, (100, 55, 25),
            (x, y - radius + 3),
            (x + 2, y - radius - 7), 4
        )
        pygame.draw.ellipse(
            surface, (70, 190, 70),
            (x + 1, y - radius - 7, 13, 8)
        )

    elif fruit == "orange":
        pygame.draw.circle(
            surface, (255, 190, 60),
            (x - 4, y - 4), radius // 2
        )
        pygame.draw.circle(
            surface, (80, 160, 65),
            (x, y - radius + 2), 5
        )

    elif fruit == "strawberry":
        pygame.draw.polygon(
            surface,
            color,
            [
                (x - radius + 3, y - radius // 3),
                (x + radius - 3, y - radius // 3),
                (x, y + radius)
            ]
        )

        for dx, dy in [(-8, 0), (7, 3), (0, 10), (-5, 12), (9, -7)]:
            pygame.draw.circle(
                surface, (255, 220, 120),
                (x + dx, y + dy), 2
            )

        pygame.draw.ellipse(
            surface, (65, 190, 75),
            (x - 10, y - radius - 3, 20, 10)
        )

    elif fruit == "green":
        pygame.draw.circle(
            surface, (145, 225, 90),
            (x - 5, y - 5), radius // 2
        )
        pygame.draw.line(
            surface, (100, 60, 25),
            (x, y - radius + 3),
            (x + 2, y - radius - 6), 4
        )
        pygame.draw.ellipse(
            surface, (50, 160, 65),
            (x + 1, y - radius - 7, 13, 8)
        )

    elif fruit == "grapes":
        for dx, dy in [
            (-8, -5), (7, -5), (-9, 7),
            (7, 8), (0, 2), (0, 14)
        ]:
            pygame.draw.circle(
                surface, color,
                (x + dx, y + dy), max(5, radius // 3)
            )

        pygame.draw.ellipse(
            surface, (70, 180, 70),
            (x - 5, y - radius - 5, 15, 8)
        )


# -------------------- BACKGROUND --------------------

def draw_background():
    for y in range(HEIGHT):
        amount = y / HEIGHT

        r = int(10 + amount * 15)
        g = int(20 + amount * 30)
        b = int(55 + amount * 45)

        pygame.draw.line(
            screen,
            (r, g, b),
            (0, y),
            (WIDTH, y)
        )

    # Decorative stars
    for x, y in [(40, 300), (790, 240), (760, 400),
                 (80, 480), (700, 520), (180, 250)]:
        pygame.draw.circle(screen, (65, 105, 160), (x, y), 2)

    text_center("BUBBLE BLAST", big_font, GOLD, WIDTH // 2, 38)

    pygame.draw.line(
        screen, (75, 115, 175),
        (20, 105), (WIDTH - 20, 105), 2
    )

    score_text = font.render(f"SCORE: {score}", True, WHITE)
    screen.blit(score_text, (25, 70))

    level_text = font.render(f"LEVEL: {level}", True, WHITE)
    screen.blit(level_text, (WIDTH - 145, 70))

    timer_color = RED if time_left <= 20 else WHITE
    timer_text = font.render(
        f"TIME: {int(time_left // 60):02d}:{int(time_left % 60):02d}",
        True, timer_color
    )
    timer_rect = timer_text.get_rect(center=(WIDTH // 2, 82))
    screen.blit(timer_text, timer_rect)


# -------------------- DRAW BUBBLE GRID --------------------

def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            fruit = grid[row][col]

            if fruit is not None:
                x, y = get_position(row, col)
                draw_fruit(screen, fruit, x, y, RADIUS)


def draw_danger_line():
    pygame.draw.line(
        screen,
        (240, 70, 75),
        (20, DANGER_LINE),
        (WIDTH - 20, DANGER_LINE),
        2
    )

    text_center(
        "DANGER LINE",
        small_font,
        (255, 100, 100),
        90,
        DANGER_LINE - 13
    )


# -------------------- AIMING --------------------

def get_aim_direction():
    mouse_x, mouse_y = pygame.mouse.get_pos()

    dx = mouse_x - SHOOTER_X
    dy = mouse_y - SHOOTER_Y

    distance = math.hypot(dx, dy)

    if distance == 0:
        return 0, -1

    dx /= distance
    dy /= distance

    # Prevent aiming below the cannon
    if dy > -0.15:
        dy = -0.15
        length = math.hypot(dx, dy)
        dx /= length
        dy /= length

    return dx, dy


def draw_aiming_guide():
    if projectile is not None or game_over or paused:
        return

    dx, dy = get_aim_direction()

    start_x = SHOOTER_X + dx * 95
    start_y = SHOOTER_Y + dy * 95

    for i in range(1, 9):
        distance = i * 24

        x = start_x + dx * distance
        y = start_y + dy * distance

        pygame.draw.circle(
            screen,
            (210, 230, 255),
            (int(x), int(y)),
            3
        )


# -------------------- ARCADE CANNON --------------------

def draw_shooter():
    dx, dy = get_aim_direction()

    angle = math.atan2(dy, dx)

    # Cannon barrel direction
    direction = pygame.Vector2(dx, dy)
    perpendicular = pygame.Vector2(-dy, dx)

    center = pygame.Vector2(SHOOTER_X, SHOOTER_Y)

    # Base platform
    pygame.draw.ellipse(
        screen, (8, 13, 28),
        (SHOOTER_X - 80, SHOOTER_Y + 25, 160, 28)
    )

    pygame.draw.ellipse(
        screen, (50, 105, 170),
        (SHOOTER_X - 65, SHOOTER_Y + 15, 130, 25)
    )

    pygame.draw.ellipse(
        screen, (120, 195, 255),
        (SHOOTER_X - 45, SHOOTER_Y + 15, 90, 12)
    )

    # Cannon rotating body
    pivot = center + direction * 30

    # Handle / grip
    handle_points = [
        pivot + perpendicular * 14 - direction * 5,
        pivot - perpendicular * 14 - direction * 5,
        pivot - perpendicular * 18 - direction * 65,
        pivot + perpendicular * 10 - direction * 65
    ]

    pygame.draw.polygon(
        screen, (20, 35, 65),
        [(int(p.x), int(p.y)) for p in handle_points]
    )

    pygame.draw.polygon(
        screen, (65, 105, 155),
        [
            (int((pivot + perpendicular * 8 - direction * 12).x),
             int((pivot + perpendicular * 8 - direction * 12).y)),
            (int((pivot - perpendicular * 8 - direction * 12).x),
             int((pivot - perpendicular * 8 - direction * 12).y)),
            (int((pivot - perpendicular * 12 - direction * 58).x),
             int((pivot - perpendicular * 12 - direction * 58).y)),
            (int((pivot + perpendicular * 5 - direction * 58).x),
             int((pivot + perpendicular * 5 - direction * 58).y))
        ]
    )

    # Grip stripes
    for i in range(4):
        p1 = pivot - direction * (25 + i * 8) + perpendicular * 9
        p2 = pivot - direction * (25 + i * 8) - perpendicular * 9

        pygame.draw.line(
            screen, (125, 175, 220),
            (int(p1.x), int(p1.y)),
            (int(p2.x), int(p2.y)), 2
        )

    # Main cannon barrel
    barrel_start = pivot - direction * 3
    barrel_end = pivot + direction * 90

    def polygon_at(start, end, width):
        return [
            start + perpendicular * width,
            start - perpendicular * width,
            end - perpendicular * width,
            end + perpendicular * width
        ]

    # Dark barrel outline
    outer = polygon_at(barrel_start, barrel_end, 20)

    pygame.draw.polygon(
        screen, (12, 23, 45),
        [(int(p.x), int(p.y)) for p in outer]
    )

    # Metallic barrel
    inner_start = pivot
    inner_end = pivot + direction * 88

    inner = polygon_at(inner_start, inner_end, 15)

    pygame.draw.polygon(
        screen, (105, 145, 185),
        [(int(p.x), int(p.y)) for p in inner]
    )

    # Silver highlight
    highlight = polygon_at(
        pivot + perpendicular * 5,
        pivot + direction * 82 + perpendicular * 5,
        4
    )

    pygame.draw.polygon(
        screen, (220, 235, 255),
        [(int(p.x), int(p.y)) for p in highlight]
    )

    # Barrel rings
    for distance in [20, 65]:
        point = pivot + direction * distance

        p1 = point + perpendicular * 17
        p2 = point - perpendicular * 17

        pygame.draw.line(
            screen, (35, 55, 85),
            (int(p1.x), int(p1.y)),
            (int(p2.x), int(p2.y)), 5
        )

        pygame.draw.line(
            screen, (190, 215, 240),
            (int(p1.x), int(p1.y)),
            (int(p2.x), int(p2.y)), 2
        )

    # Muzzle
    muzzle = pivot + direction * 90

    pygame.draw.circle(
        screen, (15, 25, 45),
        (int(muzzle.x), int(muzzle.y)), 20
    )

    pygame.draw.circle(
        screen, (140, 175, 210),
        (int(muzzle.x), int(muzzle.y)), 16
    )

    pygame.draw.circle(
        screen, (25, 40, 65),
        (int(muzzle.x), int(muzzle.y)), 10
    )

    pygame.draw.circle(
        screen, (190, 220, 250),
        (int(muzzle.x - 4), int(muzzle.y - 4)), 3
    )

    # Central rotating joint
    pygame.draw.circle(
        screen, (20, 35, 65),
        (SHOOTER_X, SHOOTER_Y), 27
    )

    pygame.draw.circle(
        screen, (90, 145, 205),
        (SHOOTER_X, SHOOTER_Y), 21
    )

    pygame.draw.circle(
        screen, (190, 220, 255),
        (SHOOTER_X, SHOOTER_Y), 12
    )

    pygame.draw.circle(
        screen, (40, 80, 135),
        (SHOOTER_X, SHOOTER_Y), 7
    )

    # Trigger detail
    trigger_point = pivot - direction * 22 - perpendicular * 17

    pygame.draw.arc(
        screen, (210, 220, 235),
        (
            int(trigger_point.x - 10),
            int(trigger_point.y - 5),
            20, 18
        ),
        math.pi, math.pi * 2, 3
    )

    # Loaded fruit
    draw_fruit(
        screen,
        current_fruit,
        int(muzzle.x),
        int(muzzle.y),
        11
    )


# -------------------- NEXT FRUIT PANEL --------------------

def draw_next_fruit():
    pygame.draw.rect(
        screen, (18, 35, 70),
        (700, 625, 125, 105),
        border_radius=14
    )

    pygame.draw.rect(
        screen, (90, 145, 205),
        (700, 625, 125, 105),
        2,
        border_radius=14
    )

    text_center(
        "NEXT FRUIT",
        small_font,
        WHITE,
        762,
        645
    )

    draw_fruit(
        screen,
        next_fruit,
        762,
        690,
        19
    )


# -------------------- SHOOTING --------------------

def shoot_fruit():
    global projectile

    if projectile is not None:
        return

    if game_over or paused:
        return

    dx, dy = get_aim_direction()

    # Start at the end of the cannon barrel
    start_x = SHOOTER_X + dx * 120
    start_y = SHOOTER_Y + dy * 120

    projectile = {
        "x": float(start_x),
        "y": float(start_y),
        "dx": dx * BULLET_SPEED,
        "dy": dy * BULLET_SPEED,
        "fruit": current_fruit
    }


def place_fruit(x, y, fruit):
    global score, level, won

    best_position = None
    best_distance = float("inf")

    # Find the closest empty grid position
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] is not None:
                continue

            px, py = get_position(row, col)
            distance = math.hypot(px - x, py - y)

            if distance < best_distance:
                best_distance = distance
                best_position = (row, col)

    if best_position is None:
        return

    row, col = best_position
    grid[row][col] = fruit

    matches = find_matches(row, col, fruit)

    if len(matches) >= 3:
        for r, c in matches:
            px, py = get_position(r, c)
            create_particles(px, py, FRUIT_COLORS[fruit])
            grid[r][c] = None

        score += len(matches) * 10

        floating = remove_floating()
        score += floating * 15

    level = 1 + score // 300

    # Check whether the board is empty
    if all(
        grid[row][col] is None
        for row in range(ROWS)
        for col in range(COLS)
    ):
        won = True


def update_projectile():
    global projectile, current_fruit, next_fruit, game_over

    if projectile is None:
        return

    projectile["x"] += projectile["dx"]
    projectile["y"] += projectile["dy"]

    x = projectile["x"]
    y = projectile["y"]

    # Bounce off side walls
    if x <= RADIUS + 5 or x >= WIDTH - RADIUS - 5:
        projectile["dx"] *= -1

    # Collision with ceiling
    collision = y <= GRID_TOP - 10

    # Collision with existing fruit
    if not collision:
        for row in range(ROWS):
            for col in range(COLS):
                fruit = grid[row][col]

                if fruit is None:
                    continue

                px, py = get_position(row, col)

                distance = math.hypot(px - x, py - y)

                if distance <= DIAMETER - 3:
                    collision = True
                    break

            if collision:
                break

    # Place fruit after collision
    if collision:
        place_fruit(x, y, projectile["fruit"])

        projectile = None

        current_fruit = next_fruit
        next_fruit = random.choice(FRUITS)

        return

    # Remove projectile if it leaves the screen
    if y < 0:
        projectile = None
        current_fruit = next_fruit
        next_fruit = random.choice(FRUITS)


def draw_projectile():
    if projectile is not None:
        draw_fruit(
            screen,
            projectile["fruit"],
            int(projectile["x"]),
            int(projectile["y"]),
            RADIUS
        )


# -------------------- GAME OVER CHECK --------------------

def check_game_over():
    global game_over

    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] is None:
                continue

            x, y = get_position(row, col)

            if y + RADIUS >= DANGER_LINE:
                game_over = True
                return


# -------------------- RESTART --------------------

def restart_game():
    global grid, particles, projectile
    global score, level, time_left
    global current_fruit, next_fruit
    global paused, game_over, won

    grid = create_grid()
    particles = []
    projectile = None

    score = 0
    level = 1
    time_left = TIME_LIMIT

    current_fruit = random.choice(FRUITS)
    next_fruit = random.choice(FRUITS)

    paused = False
    game_over = False
    won = False


# -------------------- PAUSE / END SCREEN --------------------

def draw_pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    text_center(
        "PAUSED",
        big_font,
        GOLD,
        WIDTH // 2,
        HEIGHT // 2 - 20
    )

    text_center(
        "Press P to continue",
        font,
        WHITE,
        WIDTH // 2,
        HEIGHT // 2 + 40
    )


def draw_end_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    screen.blit(overlay, (0, 0))

    if won:
        heading = "YOU WIN!"
        heading_color = GREEN
    else:
        heading = "GAME OVER"
        heading_color = RED

    text_center(
        heading,
        big_font,
        heading_color,
        WIDTH // 2,
        HEIGHT // 2 - 60
    )

    text_center(
        f"YOUR SCORE: {score}",
        font,
        WHITE,
        WIDTH // 2,
        HEIGHT // 2 + 5
    )

    text_center(
        "Click anywhere to play again",
        font,
        GOLD,
        WIDTH // 2,
        HEIGHT // 2 + 55
    )


# -------------------- MAIN GAME --------------------

def main():
    global paused, game_over, time_left, projectile

    restart_game()

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        # Events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_p and not game_over and not won:
                    paused = not paused

                if event.key == pygame.K_r:
                    restart_game()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    if game_over or won:
                        restart_game()

                    elif not paused:
                        shoot_fruit()

        # Update game
        if not paused and not game_over and not won:

            time_left -= dt

            if time_left <= 0:
                time_left = 0
                game_over = True

            if not game_over:
                update_projectile()
                update_particles()
                check_game_over()

        # Draw everything
        draw_background()
        draw_danger_line()
        draw_grid()
        draw_particles()
        draw_aiming_guide()
        draw_shooter()
        draw_projectile()
        draw_next_fruit()

        # Bottom instructions
        text_center(
            "AIM WITH MOUSE  |  CLICK TO SHOOT  |  P = PAUSE  |  R = RESTART",
            small_font,
            (190, 210, 240),
            WIDTH // 2,
            735
        )

        if paused and not game_over and not won:
            draw_pause_screen()

        if game_over or won:
            draw_end_screen()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()