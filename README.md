# Super Jin - Enhanced Edition v2.1.0

A fully-featured 2D platformer built from scratch in Python with pygame. Features endless procedurally-generated levels with parkour, boss battles, flying enemies, collectible coins, themed parallax backgrounds, a complete menu/settings system, and persistent high scores — all with zero external assets (graphics and music are synthesized at runtime).

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![pygame](https://img.shields.io/badge/pygame--ce-2.5%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

### 🎮 Gameplay
- **Endless Progression**: Procedurally-generated levels that scale in difficulty as you advance
- **Long Parkour Runways**: Levels are roughly twice as long as a classic stage and grow each level, filled with floating platforms, gaps, and pipes to traverse
- **Boss Battles**: Fight a unique boss every 4th level (levels 4, 8, 12...) in enclosed arenas
- **Collectible Coins**: Coins scattered along the path — many placed in hard-to-reach spots (over gaps, atop parkour platforms) — boost your score
- **Enemies**: Goombas, Koopas (with kickable shells), and flying **Birds** you must duck under, jump over, or stomp
- **Dual Control Schemes**: Play with Arrow keys or WASD (both work simultaneously)
- **Dynamic Obstacles**: Gaps, spikes, pipes, and environmental hazards
- **Power-ups**: Mushrooms for growth, coins for score, block-breaking when big
- **Responsive Movement**: Coyote time, buffered jumps, double-jump, variable jump height, and a crouch that shrinks your hitbox to slip under birds

### 🎨 Graphics & Presentation
- **4 Themed Worlds**: Overworld, Sunset, Night, and Cavern — each with unique palettes
- **Parallax Backgrounds**: Multi-layer scrolling with animated clouds, mountains, hills, sun/moon, and stars
- **Procedural Pixel Art**: All sprites (player, enemies, tiles, boss) rendered via code — no image files
- **Animated UI**: Hover-scaling buttons, sliders, health bars, particle effects, and fireworks

### 🎵 Audio
- **Synthesized Sound Effects**: Jump, coin pickup, stomp, powerup, death, menu navigation, and more
- **Dynamic Background Music**: Original looping melodies (4 themes) generated on-the-fly
- **Volume Control**: Separate sliders for music and SFX, plus a music ON/OFF toggle

### 💾 Persistence
- **High Score Tracking**: Your best score is saved to `highscore.json` and displayed on the home screen
- **New Record Detection**: Flashing "NEW HIGH SCORE!" message when you beat your personal best

### ⚙️ Menus & Settings
- **Home Screen**: Play or Exit with animated title and controls guide
- **Pause Menu** (Esc): Resume, Settings, or return to Main Menu
- **Settings Panel**: Adjust music/SFX volume live, toggle music on/off
- **Game Over Screen**: Shows your score, high score, and new record status
- **Level Intro Cards**: Brief pre-level splash with world name, theme, level number, and lives

---

## 📁 Project Structure

```
2D_pygame.py/
├── main.py                 # Entry point
├── game.py                 # Core game loop, state machine, collision, rendering
├── constants.py            # Screen dimensions, physics constants, color palette
├── settings.py             # Global settings (music/SFX volume)
├── highscore.py            # Persistent high-score save/load
├── levels.py               # Procedural level + boss arena generators
├── sounds.py               # Synthesized audio (SFX + background music)
├── sprites.py              # Pixel-art data for all sprites
├── spritesheet.py          # Sprite surface cache + boss renderer
├── ui.py                   # Button and Slider widgets
├── entities/
│   ├── __init__.py
│   ├── player.py           # Player movement, jump, duck (shrinks hitbox), animation
│   ├── enemy.py            # Goomba, Koopa (shell kick), Bird (flying enemy)
│   ├── boss.py             # Boss + Fireball projectiles
│   ├── item.py             # Mushroom, coin (from blocks)
│   ├── coin.py             # Collectible pathway coins
│   ├── tile.py             # Ground, brick, question block, pipe, spike
│   └── particle.py         # Debris, score popups, fireworks
├── Play_Mario.bat          # Windows launcher script
├── .gitignore
└── README.md
```

---

## 🚀 Installation & Running

### Requirements
- **Python 3.12+** (tested on 3.12.10)
- **pygame-ce 2.5+**

### Setup
```bash
# Clone the repository
git clone https://github.com/jinsungj27-collab/Pygame.git
cd Pygame

# Install pygame-ce (if not already installed)
pip install pygame-ce

# Run the game
python main.py

# OR on Windows, double-click:
Play_Mario.bat
```

No additional assets are required — all graphics and audio are generated at runtime.

---

## 🎮 Controls

| Action       | Keys                        |
|--------------|-----------------------------|
| Move Left    | `←` / `A`                   |
| Move Right   | `→` / `D`                   |
| Jump         | `Space` / `↑` / `W`         |
| Duck         | `↓` / `S`                   |
| Pause        | `Esc`                       |
| Menu Select  | `Enter` or click buttons    |

---

## 🎯 How to Play

1. **Start**: Launch the game and click **PLAY** (or press Enter)
2. **Level Intro**: A splash card shows your world, level number, and lives
3. **Play**: Navigate obstacles, stomp enemies, collect coins and power-ups
4. **Boss Battle** (every 4th level): Stomp the boss's head to damage it; defeat it to advance
5. **Stage Clear**: Reach the flag (normal levels) or defeat the boss (boss levels) to continue
6. **Lives**: You start with 3 lives; lose a life when you take damage while small or fall into a pit
7. **Game Over**: When all lives are lost, your score is saved if it beats your high score

### Tips
- **Stomp enemies** by landing on their heads (jump + fall onto them)
- **Duck** (`S` / `↓`) to slip under low-flying birds, or jump over / stomp them
- **Mushrooms** make you big (allowing you to break bricks and take one hit)
- **Koopa shells** can be kicked to take out other enemies
- **Collect coins** along the path for extra points — the trickier ones over gaps and on parkour platforms are worth chasing for a high score
- **Boss fireballs** damage you — dodge or jump over them
- **Gaps** require precise jumps — use the double-jump if needed
- **Spikes** hurt you even when big — avoid them entirely

---

## 🔧 Technical Highlights

- **Procedural Generation**: Levels are built algorithmically with scaling difficulty (enemy count/speed, gaps, spikes, time limit)
- **No Asset Files**: All sprites are defined as character grids (`sprites.py`) and rendered into pygame Surfaces; music is synthesized from frequency lists
- **State Machine Architecture**: Clean separation of game states (Menu, Intro, Playing, Paused, Settings, Clear, Game Over)
- **Parallax Scrolling**: Multi-layer background with independent scroll speeds (0.1x for clouds, 0.2x for mountains, 0.3x for hills)
- **Responsive Physics**: Coyote time (6 frames of grace after leaving ground), jump buffering (8 frames), variable jump height
- **Boss AI**: Patrols arena, hops periodically, shoots arcing fireballs toward player position

---

## 🐛 Known Issues / Future Enhancements

- **Double-jump** is currently enabled by default, making gaps/obstacles easier than intended (toggle coming soon)
- **No checkpoints** — dying restarts the entire level
- **Limited enemy variety** — only Goomba and Koopa currently
- **No fire-flower or invincibility star** power-ups yet
- **Boss patterns** are basic (patrol + hop + shoot); could add phases or special attacks

Planned features: checkpoints, more power-ups, additional enemy types, fire-flower projectile combat, gamepad support.

---

## 📜 Version History

### v2.1.0 (Current)
- Renamed to **Super Jin**
- Runways roughly doubled in length with procedural **parkour** (floating platforms)
- **Collectible coins** along the path, many in hard-to-reach spots, worth score
- New flying **Bird** enemy — duck under it, jump over, or stomp it (makes the crouch useful)
- Crouch now shrinks the player hitbox to slip under birds
- Boss battles every 4th level with HP scaling
- Persistent high score with new record detection
- WASD control scheme added
- Enhanced game over screen with high score display

### v2.0 (Enhanced Edition)
- Multi-level endless progression with procedural generation
- 4 themed parallax backgrounds (Overworld, Sunset, Night, Cavern)
- Full menu system (Home, Pause, Settings)
- Live volume sliders for music and SFX
- Animated UI with hover effects
- Synthesized background music (4 original themes)
- Spike hazards, gaps in the ground
- Difficulty scaling (enemy count/speed, time limit, obstacles)
- Firework effects on stage clear

### v1.0 (Original)
- Basic single-level Mario clone
- Player, Goomba, Koopa, coin, mushroom
- Brick/question blocks, pipes, staircases
- Flag-based level clear

---

## 👤 Author

**Jinsung** ([@jinsungj27-collab](https://github.com/jinsungj27-collab))

---

## 📄 License

MIT License - feel free to use, modify, and distribute. Attribution appreciated but not required.

---

## 🙏 Acknowledgments

- Inspired by the original *Super Mario Bros.* by Nintendo
- Built with [pygame-ce](https://github.com/pygame-community/pygame-ce) (Community Edition)
- All code, graphics, and music created from scratch for this project
