# Space War OLED Game 🚀

A retro-style OLED space shooter game built using an ESP32, SSD1306 OLED display, two push buttons, and a buzzer.

The player controls a spaceship that moves across 3 lanes and shoots incoming enemy ships.

---

# Features

- Animated spaceship
- Enemy spawning
- Shooting mechanics
- Score system
- High score tracking
- Sound effects
- Game over screen
- Retro arcade visuals
- Smooth controls
- Lightweight and fast

---

# Components Required

| Component | Quantity |
|---|---|
| ESP32 Dev Board | 1 |
| SSD1306 OLED Display (128x64 I2C) | 1 |
| Push Buttons | 2 |
| Breadboard | 1 |
| Jumper Wires | Some |
| Passive Buzzer | 1 |

---

# Hardware Connections

## OLED Display Connections

| OLED Pin | ESP32 Pin |
|---|---|
| GND | GND |
| VCC | 3V3 |
| SCL | GPIO 22 |
| SDA | GPIO 21 |

---

## Button Connections

| Button | ESP32 Pin |
|---|---|
| Move Button | GPIO 32 |
| Shoot Button | GPIO 33 |

### Important

Each button should connect:

- One side → GPIO pin
- Other side → GND

The project uses:

```cpp
INPUT_PULLUP
```

So external resistors are NOT required.

---

## Buzzer Connections

| Buzzer Pin | ESP32 Pin |
|---|---|
| Positive | GPIO 27 |
| Negative | GND |

---

# Circuit Diagram

![Circuit Diagram](https://img.notionusercontent.com/s3/prod-files-secure%2F755a6ed0-2ab1-488b-a789-291b2d1e1c78%2Fbe3ab6cc-3d79-4c27-82aa-1fe956ad9fda%2Fimage.png/size/w=2000?exp=1779165998&sig=vEFVxRmz94yPqy51s2MYF1dYfwWX3sENMYxFltScWn8&imgBuildSrc=presignImageUrl&id=34173863-7494-80df-b61c-c55a0d9c62e9&table=block&mtd=so)

---

# Controls

| Button | Action |
|---|---|
| Move Button | Change lane |
| Shoot Button | Fire bullet / Start game |

---

# Gameplay

- The player ship moves between 3 lanes.
- Enemies spawn randomly from the top.
- Shoot enemies before they collide with your ship.
- Every destroyed enemy increases your score.
- High score is saved during runtime.
- Collision with an enemy causes game over.

---

# Installing Libraries

Install the following libraries from Arduino Library Manager.

## Required Libraries

### Adafruit GFX

By Adafruit

### Adafruit SSD1306

By Adafruit

---

# Arduino IDE Setup

## Board Selection

Select:

```text
ESP32 Dev Module
```

---

## Recommended Settings

| Setting | Value |
|---|---|
| Upload Speed | 921600 |
| Flash Frequency | 80MHz |
| Partition Scheme | Default |
| PSRAM | Disabled |

---

# Upload Instructions

1. Connect ESP32 via USB
2. Open Arduino IDE
3. Install required libraries
4. Paste the game code
5. Select correct COM port
6. Upload code
7. Press SHOOT button to start

---

# Pin Configuration

```cpp
#define BTN_MOVE 32
#define BTN_SHOOT 33
#define BUZZER_PIN 27
```

---

# OLED Specifications

| Property | Value |
|---|---|
| Resolution | 128x64 |
| Interface | I2C |
| Address | 0x3C |

---

# Troubleshooting

## OLED Not Turning On

Check:

- SDA → GPIO 21
- SCL → GPIO 22
- I2C address is `0x3C`

---

## Buttons Not Working

Make sure buttons connect to:

- GPIO pin
- GND

NOT 3.3V.

---

## Random Inputs

Increase debounce value:

```cpp
const int debounceDelay = 45;
```

Try:

```cpp
80
```

or:

```cpp
120
```

---

# Future Improvements

Possible upgrades:

- Multiple enemies
- Boss fights
- Power-ups
- Health system
- Laser weapons
- Explosions
- Sprite animations
- EEPROM high score saving
- Multiplayer
- Difficulty scaling

---

# License

Open-source project for learning embedded systems, retro game development, and ESP32 graphics programming.
