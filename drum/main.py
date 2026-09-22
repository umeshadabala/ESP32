
import tkinter as tk
import serial
import threading
import math
import random
import time


# ============================================================
# SETTINGS
# ============================================================

PORT = "/dev/tty.usbserial-0001"
BAUD = 115200

WIDTH = 1000
HEIGHT = 700

# How strongly gyro movement moves the blade
MOVE_SPEED = 0.12

# Swing detection sensitivity
SWING_THRESHOLD = 180

# Fruit
FRUIT_RADIUS = 30
SPAWN_INTERVAL = 0.65

FRUIT_SPEED_MIN = 0.5
FRUIT_SPEED_MAX = 1

# Blade
TRAIL_LENGTH = 14
BLADE_LENGTH = 65

# ============================================================
# GLOBAL STATE
# ============================================================

ser = None

sensor_lock = threading.Lock()

gx = 0
gy = 0
gz = 0

blade_x = WIDTH / 2
blade_y = HEIGHT / 2

previous_blade_x = blade_x
previous_blade_y = blade_y

blade_points = []

fruits = []

score = 0
combo = 0
combo_timer = 0

running = True

last_swing_time = 0


# ============================================================
# SERIAL CONNECTION
# ============================================================

def serial_thread():
    global ser, gx, gy, gz

    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)

        print("Connected to:", PORT)

        time.sleep(2)

        while running:

            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if not line:
                    continue

                # Ignore ESP32 status messages
                if line == "READY":
                    print("ESP32 READY")
                    continue

                if line == "MPU6050_ERROR":
                    print("MPU6050 ERROR")
                    continue

                parts = line.split(",")

                if len(parts) != 6:
                    continue

                ax = float(parts[0])
                ay = float(parts[1])
                az = float(parts[2])

                new_gx = float(parts[3])
                new_gy = float(parts[4])
                new_gz = float(parts[5])

                with sensor_lock:
                    gx = new_gx
                    gy = new_gy
                    gz = new_gz

            except Exception:
                pass

    except Exception as e:
        print()
        print("Could not connect to ESP32.")
        print("Serial error:", e)
        print()
        print("Check that the port is:")
        print(PORT)


# ============================================================
# CREATE WINDOW
# ============================================================

root = tk.Tk()

root.title("⚔️ FRUIT SLASH")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(False, False)

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="#101018",
    highlightthickness=0
)

canvas.pack()


# ============================================================
# UI
# ============================================================

title_text = canvas.create_text(
    WIDTH // 2,
    35,
    text="⚔️ FRUIT SLASH",
    fill="white",
    font=("Helvetica", 26, "bold")
)

score_text = canvas.create_text(
    25,
    30,
    anchor="w",
    text="SCORE: 0",
    fill="white",
    font=("Helvetica", 20, "bold")
)

combo_text = canvas.create_text(
    WIDTH - 25,
    30,
    anchor="e",
    text="",
    fill="#ffd84d",
    font=("Helvetica", 20, "bold")
)

help_text = canvas.create_text(
    WIDTH // 2,
    HEIGHT - 25,
    text="Move the MPU6050 like a lightsaber ⚔️",
    fill="#777780",
    font=("Helvetica", 13)
)


# ============================================================
# FRUIT CLASS
# ============================================================

class Fruit:

    def __init__(self):

        self.x = random.randint(80, WIDTH - 80)

        self.y = HEIGHT + 50

        self.radius = random.randint(24, 34)

        self.speed = random.uniform(
            FRUIT_SPEED_MIN,
            FRUIT_SPEED_MAX
        )

        self.horizontal_speed = random.uniform(-1.2, 1.2)

        self.sliced = False

        self.rotation = random.randint(0, 360)

        self.color = random.choice([
            "#ff3b30",
            "#ff9500",
            "#ffd60a",
            "#34c759",
            "#30d5c8",
            "#0a84ff",
            "#af52de",
            "#ff375f"
        ])

        self.id = None

        self.draw()

    def draw(self):

        r = self.radius

        self.id = canvas.create_oval(
            self.x - r,
            self.y - r,
            self.x + r,
            self.y + r,
            fill=self.color,
            outline="white",
            width=2
        )

        # Small highlight
        canvas.create_oval(
            self.x - r * 0.45,
            self.y - r * 0.5,
            self.x - r * 0.15,
            self.y - r * 0.2,
            fill="white",
            outline=""
        )

    def update(self):

        self.x += self.horizontal_speed

        self.y -= self.speed

        self.rotation += 5

        if self.id:

            canvas.coords(
                self.id,
                self.x - self.radius,
                self.y - self.radius,
                self.x + self.radius,
                self.y + self.radius
            )

    def destroy(self):

        if self.id:

            canvas.delete(self.id)

            self.id = None


# ============================================================
# SPAWN FRUITS
# ============================================================

def spawn_fruit():

    if not running:
        return

    # Spawn exactly 1 fruit
    fruits.append(Fruit())


# ============================================================
# DISTANCE FROM POINT TO LINE SEGMENT
# ============================================================

def point_to_segment_distance(
    px,
    py,
    x1,
    y1,
    x2,
    y2
):

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:

        return math.hypot(
            px - x1,
            py - y1
        )

    t = (
        (px - x1) * dx +
        (py - y1) * dy
    ) / (dx * dx + dy * dy)

    t = max(0, min(1, t))

    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    return math.hypot(
        px - closest_x,
        py - closest_y
    )


# ============================================================
# SLICE FRUIT
# ============================================================

def slice_fruit(fruit):

    global score
    global combo
    global combo_timer

    if fruit.sliced:
        return

    fruit.sliced = True

    fruit.destroy()
    spawn_fruit()

    score += 10

    combo += 1

    combo_timer = time.time()

    canvas.itemconfig(
        score_text,
        text=f"SCORE: {score}"
    )

    if combo >= 2:

        canvas.itemconfig(
            combo_text,
            text=f"COMBO x{combo}"
        )

    # Explosion effect
    create_slice_effect(
        fruit.x,
        fruit.y,
        fruit.color
    )


# ============================================================
# SLICE EFFECT
# ============================================================

def create_slice_effect(x, y, color):

    particles = []

    for _ in range(10):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            2,
            7
        )

        px = x
        py = y

        particle = canvas.create_oval(
            px - 4,
            py - 4,
            px + 4,
            py + 4,
            fill=color,
            outline=""
        )

        particles.append([
            particle,
            px,
            py,
            math.cos(angle) * speed,
            math.sin(angle) * speed
        ])

    animate_particles(particles, 0)


def animate_particles(particles, frame):

    if frame > 20:

        for particle in particles:

            canvas.delete(particle[0])

        return

    for particle in particles:

        item = particle[0]

        particle[1] += particle[3]
        particle[2] += particle[4]

        particle[4] += 0.25

        x = particle[1]
        y = particle[2]

        size = max(
            1,
            4 - frame * 0.15
        )

        canvas.coords(
            item,
            x - size,
            y - size,
            x + size,
            y + size
        )

    root.after(
        30,
        lambda: animate_particles(
            particles,
            frame + 1
        )
    )


# ============================================================
# DRAW BLADE
# ============================================================

def draw_blade():

    # Delete old blade
    canvas.delete("blade")

    if len(blade_points) < 2:
        return

    # Draw the trail
    points = []

    for x, y in blade_points:

        points.extend([
            x,
            y
        ])

    canvas.create_line(
        *points,
        fill="#8fffff",
        width=5,
        smooth=True,
        capstyle=tk.ROUND,
        tag="blade"
    )

    # Bright center
    canvas.create_line(
        *points,
        fill="white",
        width=2,
        smooth=True,
        capstyle=tk.ROUND,
        tag="blade"
    )

    # Blade tip
    canvas.create_oval(
        blade_x - 8,
        blade_y - 8,
        blade_x + 8,
        blade_y + 8,
        fill="white",
        outline="#8fffff",
        width=3,
        tags="blade"
    )


# ============================================================
# CHECK BLADE COLLISION
# ============================================================

def check_collisions(
    old_x,
    old_y,
    new_x,
    new_y
):

    for fruit in fruits:

        if fruit.sliced:
            continue

        distance = point_to_segment_distance(
            fruit.x,
            fruit.y,
            old_x,
            old_y,
            new_x,
            new_y
        )

        # Larger hit area makes the game more fun
        hit_radius = fruit.radius + 18

        if distance <= hit_radius:

            slice_fruit(fruit)


# ============================================================
# UPDATE BLADE
# ============================================================

def update_blade():

    global blade_x
    global blade_y
    global previous_blade_x
    global previous_blade_y
    global last_swing_time

    with sensor_lock:

        current_gx = gx
        current_gy = gy
        current_gz = gz

    old_x = blade_x
    old_y = blade_y

    # --------------------------------------------------------
    # MPU6050 -> SCREEN MOVEMENT
    # --------------------------------------------------------

    blade_x += current_gz * MOVE_SPEED
    blade_y += current_gx * MOVE_SPEED

    # Keep blade inside screen
    blade_x = max(
        20,
        min(WIDTH - 20, blade_x)
    )

    blade_y = max(
        80,
        min(HEIGHT - 50, blade_y)
    )

    # --------------------------------------------------------
    # Store blade path
    # --------------------------------------------------------

    blade_points.append(
        (blade_x, blade_y)
    )

    if len(blade_points) > TRAIL_LENGTH:

        blade_points.pop(0)

    # --------------------------------------------------------
    # Calculate movement speed
    # --------------------------------------------------------

    movement = math.hypot(
        blade_x - old_x,
        blade_y - old_y
    )

    gyro_magnitude = math.sqrt(
        current_gx ** 2 +
        current_gy ** 2 +
        current_gz ** 2
    )

    # --------------------------------------------------------
    # Detect a strong swing
    # --------------------------------------------------------

    if (
        gyro_magnitude > SWING_THRESHOLD
        or movement > 18
    ):

        last_swing_time = time.time()

        # Check the recent blade path
        check_path_collisions()

    # --------------------------------------------------------
    # Check normal movement collision too
    # --------------------------------------------------------

    check_collisions(
        old_x,
        old_y,
        blade_x,
        blade_y
    )

    previous_blade_x = old_x
    previous_blade_y = old_y

    draw_blade()


# ============================================================
# CHECK WHOLE BLADE TRAIL
# ============================================================

def check_path_collisions():

    if len(blade_points) < 2:
        return

    # Check every segment of recent blade movement

    for i in range(
        len(blade_points) - 1
    ):

        x1, y1 = blade_points[i]

        x2, y2 = blade_points[i + 1]

        check_collisions(
            x1,
            y1,
            x2,
            y2
        )


# ============================================================
# UPDATE FRUITS
# ============================================================

def update_fruits():

    for fruit in fruits[:]:

        fruit.update()

        # Fruit missed the bottom/top boundary
        # IMPORTANT: No lives are lost.

        if (
            fruit.y < -80
            or fruit.x < -100
            or fruit.x > WIDTH + 100
        ):

            fruit.destroy()

            if fruit in fruits:

                fruits.remove(fruit)
                spawn_fruit()


# ============================================================
# COMBO TIMER
# ============================================================

def update_combo():

    global combo

    if combo > 0:

        elapsed = time.time() - combo_timer

        if elapsed > 1.5:

            combo = 0

            canvas.itemconfig(
                combo_text,
                text=""
            )


# ============================================================
# MAIN GAME LOOP
# ============================================================

def game_loop():

    if not running:
        return

    update_blade()

    update_fruits()

    update_combo()

    root.after(
        16,
        game_loop
    )


# ============================================================
# KEYBOARD CONTROLS
# ============================================================

def keyboard_move(event):

    global blade_x
    global blade_y

    speed = 35

    if event.keysym == "Left":
        blade_x -= speed

    elif event.keysym == "Right":
        blade_x += speed

    elif event.keysym == "Up":
        blade_y -= speed

    elif event.keysym == "Down":
        blade_y += speed

    blade_x = max(
        20,
        min(WIDTH - 20, blade_x)
    )

    blade_y = max(
        80,
        min(HEIGHT - 50, blade_y)
    )


root.bind(
    "<Left>",
    keyboard_move
)

root.bind(
    "<Right>",
    keyboard_move
)

root.bind(
    "<Up>",
    keyboard_move
)

root.bind(
    "<Down>",
    keyboard_move
)


# ============================================================
# CLEAN EXIT
# ============================================================

def close_game():

    global running

    running = False

    try:

        if ser:

            ser.close()

    except Exception:
        pass

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_game
)


# ============================================================
# START
# ============================================================

print()
print("================================")
print("       FRUIT SLASH")
print("================================")
print()
print("Controls:")
print("  Move MPU6050 = Move blade")
print("  Fast movement = Slash")
print("  Arrow keys = Test blade")
print()
print("Unlimited lives: ON")
print("No game over.")
print()
print("Connecting to ESP32...")
print()


# Start serial reader
thread = threading.Thread(
    target=serial_thread,
    daemon=True
)

thread.start()


# Start fruit spawning
root.after(
    1000,
    spawn_fruit
)


# Start game loop
root.after(
    100,
    game_loop
)


# Start Tkinter
root.mainloop()
