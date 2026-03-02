# AutoMahjong Terminal UI

Terminal-based Mahjong game with emoji tile display.

## Quick Start

```bash
cd /Users/qiyuchen/Documents/AutoMahjong
python3 TUIGame.py
```

## Features

- **Emoji Tile Display**: All 108 Sichuan tiles displayed as emoji characters
  - Characters (万): 🀇🀈🀉🀊🀋🀌🀍🀎🀏
  - Bamboo (条): 🀙🀚🀛🀜🀝🀞🀟🀠🀡
  - Dots (筒): 🀩🀪🀫🀬🀭🀮🀯🀰🀱

- **Human Player at Bottom**: You always see your hand at the bottom of the screen

- **Simple Input**: Numbered tile selection (1-14) for discarding

- **3 AI Difficulties**: Easy, Medium, Hard

## Table Layout

```
                    [North - AI]
                    
    [West - AI]              [East - AI]
    
                    [South - YOU]
```

Your hand is displayed with numbers for easy selection:
```
Your Hand: 1:🀇 2:🀈 3:🀉 4:🀙 5:🀚 6:🀛 7:🀩 8:🀪 9:🀫...
```

## How to Play

1. **Start Game**: Run `python3 TUIGame.py`
2. **Enter Name**: Choose your player name
3. **Select Difficulty**: Choose AI difficulty (1=Easy, 2=Medium, 3=Hard)
4. **Claim Short Suit**: Choose which suit to discard (W/S/P)
5. **Play**: 
   - When it's your turn, the status bar turns red
   - Enter tile number (1-14) to discard
   - Use menu prompts for PENG/GANG/HU actions

## Controls

### Discard Phase
```
Enter tile number to discard (1-14): 5
```

### Action Phase
```
Your action [H/G/N]: H
  H = HU (win)
  G = GANG (kong)
  N = NOTHING (pass)
```

### React to Opponent
```
Your action [H/P/G/N]: P
  H = HU (win)
  P = PENG (pong)
  G = GANG (kong)
  N = NOTHING (pass)
```

## Files

- `TUIGame.py` - Main game entry point
- `TUIPlayer.py` - Terminal UI player class with emoji display
- `TUIObserver.py` - Table display observer (embedded in TUIGame.py)

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)
- Terminal with Unicode emoji support

## Tips

1. **Short Suit**: Always discard tiles from your short suit first
2. **Numbered Display**: Your hand shows numbers for easy tile selection
3. **AI Revealed**: You can see AI players' revealed sets (pongs/kongs)
4. **Game Log**: Recent actions shown at bottom of table

## Troubleshooting

### Emoji Not Showing
If you see boxes instead of emoji:
- Try a different terminal (iTerm2, Terminal.app on Mac)
- Ensure your terminal font supports emoji
- Set terminal encoding to UTF-8

### Screen Not Clearing
If the screen doesn't clear between turns:
- Some terminals don't support ANSI escape codes
- The game will still work, just with scrolling output

## Example Session

```
$ python3 TUIGame.py

======================================================================
           🀄 WELCOME TO AUTO MAHJONG - TERMINAL EDITION 🀄
======================================================================

Enter your name: John

Select AI difficulty:
  1. Easy (2 Random AI + 1 Simple AI)
  2. Medium (1 Random AI + 2 Simple AI)
  3. Hard (3 Simple AI)
Choose difficulty [1/2/3]: 2

Players: ['AI1', 'John', 'AI2', 'AI3']
You are seated at position 1 (South)

Press Enter to start the game...

[Table displays with emoji tiles]
[Game proceeds with interactive prompts]
```

## License

Part of the AutoMahjong project.
