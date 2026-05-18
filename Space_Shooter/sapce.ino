#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define BTN_MOVE 32
#define BTN_SHOOT 33
#define BUZZER_PIN 27

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// =====================================================
// GAME STATES
// =====================================================

enum GameState {
  START,
  PLAYING,
  GAMEOVER
};

GameState gameState = START;

// =====================================================
// LANES
// =====================================================

const int lanes[3] = {24, 64, 104};

int playerLane = 1;

// =====================================================
// OBJECTS
// =====================================================

struct Bullet {
  int x;
  int y;
  bool active;
};

struct Enemy {
  int lane;
  int y;
};

Bullet bullet;
Enemy enemy;

// =====================================================
// GAME VARIABLES
// =====================================================

int score = 0;
int highScore = 0;

unsigned long enemyTimer = 0;
unsigned long bulletTimer = 0;

bool enemyFlash = false;

// =====================================================
// BUTTONS
// =====================================================

bool lastMoveState = HIGH;
bool lastShootState = HIGH;

unsigned long lastMoveTime = 0;
unsigned long lastShootTime = 0;

const int debounceDelay = 45;

// =====================================================
// SOUND
// =====================================================

void beep(int freq, int duration)
{
  tone(BUZZER_PIN, freq, duration);
}

// =====================================================
// RESET GAME
// =====================================================

void resetGame()
{
  score = 0;

  playerLane = 1;

  bullet.active = false;

  enemy.lane = random(0, 3);
  enemy.y = 0;

  gameState = PLAYING;
}

// =====================================================
// STARS
// =====================================================

void drawStars()
{
  for (int i = 0; i < 12; i++)
  {
    int x = (millis() / 5 + i * 19) % SCREEN_WIDTH;
    int y = (i * 11) % SCREEN_HEIGHT;

    display.drawPixel(x, y, SSD1306_WHITE);
  }
}

// =====================================================
// PLAYER
// =====================================================

void drawPlayer()
{
  int x = lanes[playerLane];

  // Main ship
  display.fillTriangle(
    x,
    48,
    x - 8,
    62,
    x + 8,
    62,
    SSD1306_WHITE
  );

  // Wings
  display.drawLine(x - 8, 58, x - 14, 62, SSD1306_WHITE);
  display.drawLine(x + 8, 58, x + 14, 62, SSD1306_WHITE);

  // Cockpit
  display.fillCircle(x, 54, 2, SSD1306_BLACK);

  // Engine fire
  if ((millis() / 120) % 2 == 0)
  {
    display.drawLine(x, 63, x, 60, SSD1306_WHITE);
  }
}

// =====================================================
// BULLET
// =====================================================

void drawBullet()
{
  if (!bullet.active)
    return;

  display.fillRect(
    bullet.x - 1,
    bullet.y,
    3,
    7,
    SSD1306_WHITE
  );
}

// =====================================================
// ENEMY
// =====================================================

void drawEnemy()
{
  int x = lanes[enemy.lane];

  display.drawRoundRect(
    x - 8,
    enemy.y,
    16,
    12,
    3,
    SSD1306_WHITE
  );

  display.fillCircle(x - 4, enemy.y + 4, 1, SSD1306_WHITE);
  display.fillCircle(x + 4, enemy.y + 4, 1, SSD1306_WHITE);

  if (enemyFlash)
  {
    display.drawLine(
      x - 6,
      enemy.y + 11,
      x + 6,
      enemy.y + 11,
      SSD1306_WHITE
    );
  }
}

// =====================================================
// UPDATE ENEMY
// =====================================================

void updateEnemy()
{
  if (millis() - enemyTimer > 55)
  {
    enemy.y += 3;

    enemyTimer = millis();

    enemyFlash = !enemyFlash;
  }

  // Reached bottom
  if (enemy.y > 54)
  {
    if (enemy.lane == playerLane)
    {
      gameState = GAMEOVER;

      if (score > highScore)
        highScore = score;

      beep(250, 500);
    }
    else
    {
      enemy.y = 0;
      enemy.lane = random(0, 3);
    }
  }
}

// =====================================================
// UPDATE BULLET
// =====================================================

void updateBullet()
{
  if (!bullet.active)
    return;

  if (millis() - bulletTimer > 18)
  {
    bullet.y -= 6;

    bulletTimer = millis();
  }

  if (bullet.y < 0)
  {
    bullet.active = false;
  }

  int enemyX = lanes[enemy.lane];

  // Collision
  if (
    bullet.active &&
    abs(bullet.x - enemyX) < 10 &&
    bullet.y < enemy.y + 12 &&
    bullet.y > enemy.y
  )
  {
    bullet.active = false;

    score++;

    beep(1500, 40);

    enemy.y = 0;
    enemy.lane = random(0, 3);
  }
}

// =====================================================
// INPUT
// =====================================================

void handleInput()
{
  bool movePressed = digitalRead(BTN_MOVE);
  bool shootPressed = digitalRead(BTN_SHOOT);

  // MOVE
  if (
    movePressed == LOW &&
    lastMoveState == HIGH &&
    millis() - lastMoveTime > debounceDelay
  )
  {
    playerLane++;

    if (playerLane > 2)
      playerLane = 0;

    beep(900, 15);

    lastMoveTime = millis();
  }

  // SHOOT
  if (
    shootPressed == LOW &&
    lastShootState == HIGH &&
    millis() - lastShootTime > debounceDelay
  )
  {
    if (!bullet.active)
    {
      bullet.active = true;

      bullet.x = lanes[playerLane];
      bullet.y = 48;

      beep(1800, 10);
    }

    lastShootTime = millis();
  }

  lastMoveState = movePressed;
  lastShootState = shootPressed;
}

// =====================================================
// HUD
// =====================================================

void drawHUD()
{
  display.setTextSize(1);

  // SCORE LEFT
  display.setCursor(0, 0);
  display.print("S:");
  display.print(score);

  // HIGH SCORE RIGHT
  display.setCursor(78, 0);
  display.print("HI:");
  display.print(highScore);

  // Divider line
  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);
}

// =====================================================
// SETUP
// =====================================================

void setup()
{
  Serial.begin(115200);

  pinMode(BTN_MOVE, INPUT_PULLUP);
  pinMode(BTN_SHOOT, INPUT_PULLUP);

  pinMode(BUZZER_PIN, OUTPUT);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  {
    while (1);
  }

  randomSeed(analogRead(34));

  display.clearDisplay();
  display.display();

  beep(1000, 100);
}

// =====================================================
// MAIN LOOP
// =====================================================

void loop()
{
  display.clearDisplay();

  drawStars();

  switch (gameState)
  {
    // =================================================
    // START SCREEN
    // =================================================

    case START:

      display.setTextSize(2);

      display.setCursor(14, 10);
      display.print("SPACE");

      display.setCursor(30, 32);
      display.print("WAR");

      display.setTextSize(1);

      display.setCursor(18, 56);
      display.print("PRESS SHOOT");

      if (digitalRead(BTN_SHOOT) == LOW)
      {
        delay(120);

        resetGame();
      }

      break;

    // =================================================
    // PLAYING
    // =================================================

    case PLAYING:

      handleInput();

      updateEnemy();

      updateBullet();

      drawPlayer();

      drawEnemy();

      drawBullet();

      drawHUD();

      break;

    // =================================================
    // GAME OVER
    // =================================================

    case GAMEOVER:

      display.setTextSize(2);

      display.setCursor(12, 8);
      display.print("GAME");

      display.setCursor(18, 30);
      display.print("OVER");

      display.setTextSize(1);

      display.setCursor(8, 52);
      display.print("S:");
      display.print(score);

      display.setCursor(70, 52);
      display.print("HI:");
      display.print(highScore);

      display.setCursor(18, 0);
      display.print("PRESS SHOOT");

      if (digitalRead(BTN_SHOOT) == LOW)
      {
        delay(150);

        resetGame();
      }

      break;
  }

  display.display();
}