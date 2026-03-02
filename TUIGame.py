"""
Terminal UI for AutoMahjong
Displays mahjong table with emoji tiles, human player always at bottom
"""
import sys
from PlayerImpl import SimpleAIPlayer, RandomAIPlayer
from Game import Game, Observer
from TUIPlayer import TUIPlayer


class TUIObserver(Observer):
    """Terminal UI observer - displays game state after each action"""
    
    def __init__(self, human_player):
        super().__init__()
        self.human_player = human_player
        self.last_event = None
    
    def tile_to_emoji(self, card):
        """Convert tile to emoji using built-in getUnicode() method"""
        if card is None:
            return ''
        return card.getUnicode()
    
    def format_hand_row(self, hand, face_down=False):
        """Format a row of tiles"""
        if face_down:
            return '🀪 ' * len(hand)
        return ' '.join([self.tile_to_emoji(c) for c in hand])
    
    def format_revealed(self, revealed):
        """Format revealed sets"""
        if not revealed:
            return ''
        sets = []
        for ke in revealed:
            emojis = ''.join([self.tile_to_emoji(c) for c in ke])
            sets.append(f"[{emojis}]")
        return ' '.join(sets)
    
    def get_player_name(self, player):
        """Get player name or direction"""
        if player is None:
            return ''
        if hasattr(player, 'direction') and player.direction:
            return player.direction
        if hasattr(player, 'id') and player.id:
            return str(player.id)
        return str(player)
    
    def display_table(self, game):
        """Display the full mahjong table"""
        # Clear screen and move cursor to top
        print("\033[2J\033[H", end="")
        
        players = game.players
        deck_count = len(game.deck)
        
        # Find human player index
        human_idx = players.index(self.human_player) if self.human_player in players else -1
        
        # Get positions relative to human (human always at bottom)
        # Order: Top, Left, Right, Bottom
        top_idx = (human_idx + 2) % 4 if human_idx >= 0 else 0
        left_idx = (human_idx + 1) % 4 if human_idx >= 0 else 1
        right_idx = (human_idx + 3) % 4 if human_idx >= 0 else 3
        bottom_idx = human_idx if human_idx >= 0 else 0
        
        top = players[top_idx]
        left = players[left_idx]
        right = players[right_idx]
        bottom = players[bottom_idx]
        
        # Table width
        width = 70
        
        print("=" * width)
        print("🀄 AUTO MAHJONG - SICHUAN BLOOD FLOW 🀄".center(width))
        print("=" * width)
        
        # Top player (North)
        print()
        print(f"{self.get_player_name(top)}".center(width))
        print(f"Score: {top.score}".center(width))
        print(f"Hand: {self.format_hand_row(top.hidden, face_down=True)}".center(width))
        if top.revealed:
            print(f"Revealed: {self.format_revealed(top.revealed)}".center(width))
        print(f"Discarded: {len(top.discardedList)} tiles".center(width))
        print()
        
        # Middle row: Left player, Center info, Right player
        print("-" * width)
        print()
        
        # Left player (West)
        left_lines = []
        left_lines.append(f"{self.get_player_name(left)}")
        left_lines.append(f"Score: {left.score}")
        left_lines.append(f"Hand: {self.format_hand_row(left.hidden, face_down=True)}")
        if left.revealed:
            left_lines.append(f"Revealed: {self.format_revealed(left.revealed)}")
        
        # Right player (East)
        right_lines = []
        right_lines.append(f"{self.get_player_name(right)}")
        right_lines.append(f"Score: {right.score}")
        right_lines.append(f"Hand: {self.format_hand_row(right.hidden, face_down=True)}")
        if right.revealed:
            right_lines.append(f"Revealed: {self.format_revealed(right.revealed)}")
        
        # Calculate padding
        left_width = max(len(line) for line in left_lines) if left_lines else 0
        right_width = max(len(line) for line in right_lines) if right_lines else 0
        center_width = width - left_width - right_width - 10
        
        # Print middle section line by line
        max_lines = max(len(left_lines), len(right_lines), 4)
        for i in range(max_lines):
            left_line = left_lines[i] if i < len(left_lines) else ''
            right_line = right_lines[i] if i < len(right_lines) else ''
            
            if i == 0:
                # Game info in center
                center_line = f"Deck: 🀪[{deck_count}]".center(center_width)
            elif i == 1:
                # Last discard or round info
                if self.last_event:
                    player_name = self.get_player_name(self.last_event.get('player'))
                    center_line = f"Last: {self.last_event['type']} {player_name}".center(center_width)
                else:
                    center_line = "".center(center_width)
            else:
                center_line = "".center(center_width)
            
            print(f"{left_line:<{left_width}}   {center_line}   {right_line:>{right_width}}")
        
        print()
        print("-" * width)
        
        # Bottom player (Human - You)
        print()
        print(f"{self.get_player_name(bottom)} - YOU".center(width))
        print(f"Score: {bottom.score}".center(width))
        print(f"Short Suit: {bottom.shortSuit}".center(width))
        
        # Numbered hand for human
        if bottom.hidden:
            hand_str = ' '.join([f"{i+1}:{self.tile_to_emoji(c)}" for i, c in enumerate(bottom.hidden)])
            print(f"Your Hand: {hand_str}".center(width))
        else:
            print("Your Hand: (empty)".center(width))
        
        if bottom.revealed:
            print(f"Revealed: {self.format_revealed(bottom.revealed)}".center(width))
        
        print()
        
        # Recent events log - HIDE other players' draws
        print("-" * width)
        print("Recent Actions:")
        events = self.all_events[-5:] if len(self.all_events) >= 5 else self.all_events
        for event in events:
            event_type = event['type']
            
            # Skip draw events from other players (only show human's draws)
            if event_type == 'draw':
                event_player = event.get('player')
                if event_player != self.human_player:
                    continue
            
            player_name = self.get_player_name(event.get('player'))
            card = event.get('card', '')
            if card:
                card_str = str(card)
            else:
                card_str = ''
            
            event_str = f"  • {event_type.upper()}: {player_name} {card_str}"
            if event.get('score', 0):
                event_str += f" ({event['score']} pts)"
            print(event_str)
        print("=" * width)
    
    def processEvent(self, event):
        """Process game event and update display"""
        super().processEvent(event)
        self.last_event = event
        
        # Store game reference on first event
        if not hasattr(self, 'game') and 'player' in event:
            # Get game from player
            player = event.get('player')
            if player and hasattr(player, 'game'):
                self.game = player.game
        
        # Only display if it's not the initial deal
        if event['type'] in ['draw', 'play', 'peng', 'gang', 'hu']:
            # Pass self.game
            if hasattr(self, 'game'):
                self.display_table(self.game)
    
    def end(self):
        """Display final game state"""
        super().end()
        if hasattr(self, 'game'):
            self.display_table(self.game)
    
    @property
    def events(self):
        """Alias for all_events"""
        return getattr(self, 'all_events', [])


def get_ai_players(ai_config):
    """Create AI players based on config"""
    players = []
    for i, ai_type in enumerate(ai_config):
        if ai_type == 'simple':
            p = SimpleAIPlayer(f"AI{i+1}")
        elif ai_type == 'random':
            p = RandomAIPlayer(f"AI{i+1}", randomLambda=0.1)
        else:
            p = SimpleAIPlayer(f"AI{i+1}")
        players.append(p)
    return players


def run_tui_game():
    """Main function to run TUI mahjong game"""
    print("\n" + "="*70)
    print("🀄 WELCOME TO AUTO MAHJONG - TERMINAL EDITION 🀄".center(70))
    print("="*70)
    print("\nSichuan Blood Flow Rules - 108 Tiles")
    print("You play against 3 AI bots")
    print("="*70)
    
    # Get player name
    name = input("\nEnter your name: ").strip() or "Player"
    
    # Get AI difficulty
    print("\nSelect AI difficulty:")
    print("  1. Easy (2 Random AI + 1 Simple AI)")
    print("  2. Medium (1 Random AI + 2 Simple AI)")
    print("  3. Hard (3 Simple AI)")
    
    while True:
        diff = input("Choose difficulty [1/2/3]: ").strip()
        if diff == '1':
            ai_config = ['random', 'simple', 'random']
            break
        elif diff == '2':
            ai_config = ['random', 'simple', 'simple']
            break
        elif diff == '3':
            ai_config = ['simple', 'simple', 'simple']
            break
        print("Invalid choice. Please enter 1, 2, or 3")
    
    # Create players: [AI, Human, AI, AI]
    # Human at index 1 will always be displayed at bottom
    ai_players = get_ai_players(ai_config)
    human = TUIPlayer(name)
    
    # Insert human at position 1 (will be displayed at bottom)
    players = [ai_players[0], human, ai_players[1], ai_players[2]]
    
    print(f"\nPlayers: {[p.id for p in players]}")
    print(f"You are seated at position 1 (South)")
    input("\nPress Enter to start the game...")
    
    # Create game
    game = Game(players=players, verbose=False)
    
    # Create and set observer
    observer = TUIObserver(human)
    observer.game = game
    game.observer = observer
    
    print("\n🎮 GAME STARTING...")
    input("Press Enter to begin...")
    
    # Start game
    try:
        game.start()
        
        # Game over - show final results
        print("\n" + "="*70)
        print("🏆 GAME OVER 🏆".center(70))
        print("="*70)
        
        # Sort by score
        sorted_players = sorted(players, key=lambda p: p.score, reverse=True)
        
        print("\nFinal Rankings:\n")
        for i, p in enumerate(sorted_players, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            marker = " ← YOU" if p == human else ""
            print(f"  {medal} {i}. {p.id} ({p.direction}): {p.score} points{marker}")
        
        print("\n" + "="*70)
        
        # Ask to play again
        again = input("\nPlay again? [Y/n]: ").strip().lower()
        if again != 'n':
            run_tui_game()
        
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_tui_game()
