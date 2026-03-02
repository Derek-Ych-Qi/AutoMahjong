"""
Terminal UI Player for AutoMahjong
Simple print/input based interaction with emoji tile display
"""
from Player import Player, cardsToStr
from Mahjong import Mahjong


class TUIPlayer(Player):
    """Terminal UI player - human interacts via console"""
    
    def __init__(self, name="Player"):
        super().__init__(name)
        self.id = name
    
    @staticmethod
    def tile_to_emoji(card):
        """Convert Mahjong tile to emoji character using built-in method"""
        if card is None:
            return ''
        
        # Use the built-in getUnicode() method
        return card.getUnicode()
    
    @staticmethod
    def format_hand(hand, numbered=False):
        """Format hand as emoji string"""
        if numbered:
            return ' '.join([f"{i+1}:{TUIPlayer.tile_to_emoji(c)}" for i, c in enumerate(hand)])
        else:
            return ' '.join([TUIPlayer.tile_to_emoji(c) for c in hand])
    
    @staticmethod
    def format_revealed(revealed):
        """Format revealed sets (pongs/kongs)"""
        result = []
        for ke in revealed:
            emojis = [TUIPlayer.tile_to_emoji(c) for c in ke]
            result.append(''.join(emojis))
        return ' '.join(result)
    
    def claimShortSuit(self):
        """Claim which suit to be missing"""
        print("\n" + "="*60)
        print(f"🀄 {self.id}'s Turn - Claim Short Suit")
        print("="*60)
        print(f"\nYour hand: {self.format_hand(self.hidden)}")
        print("\nSuit counts:")
        
        suit_counts = {'W': 0, 'S': 0, 'P': 0}
        for card in self.hidden:
            suit_counts[card.suit] = suit_counts.get(card.suit, 0) + 1
        
        suit_names = {'W': 'Characters (万)', 'S': 'Bamboo (条)', 'P': 'Dots (筒)'}
        for suit, count in suit_counts.items():
            marker = " ← RECOMMENDED" if count == min(suit_counts.values()) else ""
            print(f"  {suit_names[suit]}: {count}{marker}")
        
        while True:
            choice = input("\nChoose short suit [W/S/P]: ").strip().upper()
            if choice in ['W', 'S', 'P']:
                self.shortSuit = choice
                print(f"✓ Short suit set to {suit_names[choice]}")
                return choice
            print("Invalid choice. Please enter W, S, or P")
    
    def passThreeCards(self):
        """Pass 3 cards to another player (initial phase)"""
        print("\n" + "="*60)
        print(f"🀄 {self.id}'s Turn - Pass 3 Cards")
        print("="*60)
        print(f"\nYour hand: {self.format_hand(self.hidden, numbered=True)}")
        
        # Count suits
        suit_counts = {'W': 0, 'S': 0, 'P': 0}
        for card in self.hidden:
            suit_counts[card.suit] += 1
        
        # Find suit with most cards (min 3)
        passing_suit = None
        for suit in ['W', 'S', 'P']:
            if suit_counts[suit] >= 3:
                passing_suit = suit
                break
        
        if not passing_suit:
            passing_suit = max(suit_counts.keys(), key=lambda s: suit_counts[s])
        
        print(f"\nRecommended passing suit: {passing_suit}")
        
        while True:
            try:
                indices = input(f"Enter 3 tile numbers to pass (e.g., 1,5,9): ").strip()
                indices = [int(x.strip()) for x in indices.replace(',', ' ').split()]
                
                if len(indices) != 3:
                    print("Please enter exactly 3 numbers")
                    continue
                
                if any(i < 1 or i > len(self.hidden) for i in indices):
                    print(f"Numbers must be between 1 and {len(self.hidden)}")
                    continue
                
                # Get cards and remove from hand
                passed_cards = []
                for idx in sorted(indices, reverse=True):
                    card = self.hidden.pop(idx - 1)
                    passed_cards.append(card)
                
                print(f"✓ Passed: {self.format_hand(passed_cards)}")
                return passed_cards
                
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas")
    
    def anyActionSelf(self):
        """
        Player has just drawn a card
        Decide: HU, GANG, or NOTHING (then discard)
        """
        # Check available actions
        can_hu = self.hu() > 0
        can_gang = any(self.canGang(c, fromHand=True) for c in self.hidden)
        
        if not (can_hu or can_gang):
            return 'NOTHING'
        
        print("\n" + "="*60)
        print(f"🀄 {self.id}'s Turn - Action After Draw")
        print("="*60)
        print(f"\nYour hand: {self.format_hand(self.hidden)}")
        print(f"Revealed: {self.format_revealed(self.revealed)}")
        
        if self.tingList:
            ting_str = ', '.join([f"{t[0]}{t[1]}" for t in self.tingList[:5]])
            if len(self.tingList) > 5:
                ting_str += f"... (+{len(self.tingList)-5} more)"
            print(f"Waiting for: {ting_str}")
        
        print("\nAvailable actions:")
        if can_hu:
            print("  [H]U - Win! 🎉")
        if can_gang:
            print("  [G]ANG - Declare Kong")
        print("  [N]OTHING - Continue (discard)")
        
        while True:
            choice = input("\nYour action [H/G/N]: ").strip().upper()
            if choice in ['H', 'HU'] and can_hu:
                return 'HU'
            elif choice in ['G', 'GANG'] and can_gang:
                return 'GANG'
            elif choice in ['N', 'NOTHING', '']:
                return 'NOTHING'
            print("Invalid choice. Please try again.")
    
    def anyActionOther(self, card, source_player):
        """
        Another player played a card
        Decide: HU, PENG, GANG, or NOTHING
        """
        # Skip if card is in short suit
        if card.suit == self.shortSuit:
            return 'NOTHING'
        
        # Check available actions
        can_hu = self.hu() > 0
        can_peng = self.canPeng(card)
        can_gang = self.canGang(card, fromHand=False)
        
        if not (can_hu or can_peng or can_gang):
            return 'NOTHING'
        
        print("\n" + "="*60)
        print(f"🀄 {self.id}'s Turn - React to {source_player.id}'s Discard")
        print("="*60)
        print(f"\n{source_player.id} discarded: {self.tile_to_emoji(card)} ({card})")
        print(f"\nYour hand: {self.format_hand(self.hidden)}")
        print(f"Revealed: {self.format_revealed(self.revealed)}")
        
        if self.tingList:
            ting_str = ', '.join([f"{t[0]}{t[1]}" for t in self.tingList[:5]])
            print(f"Waiting for: {ting_str}")
        
        print("\nAvailable actions:")
        if can_hu:
            print(f"  [H]U - Win off {source_player.id}'s discard! 🎉")
        if can_peng:
            print(f"  [P]ENG - Form Pung with {card}")
        if can_gang:
            print(f"  [G]ANG - Form Kong with {card}")
        print("  [N]OTHING - Pass")
        
        while True:
            choice = input("\nYour action [H/P/G/N]: ").strip().upper()
            if choice in ['H', 'HU'] and can_hu:
                return 'HU'
            elif choice in ['P', 'PENG'] and can_peng:
                return 'PENG'
            elif choice in ['G', 'GANG'] and can_gang:
                return 'GANG'
            elif choice in ['N', 'NOTHING', '']:
                return 'NOTHING'
            print("Invalid choice. Please try again.")
    
    def discard(self):
        """
        Player must discard a card
        Returns the discarded Mahjong tile
        """
        print("\n" + "="*60)
        print(f"🀄 {self.id}'s Turn - Discard")
        print("="*60)
        print(f"\nYour hand: {self.format_hand(self.hidden, numbered=True)}")
        print(f"Revealed: {self.format_revealed(self.revealed)}")
        
        # Check if we have short suit tiles
        has_short = any(c.suit == self.shortSuit for c in self.hidden)
        
        if has_short:
            print(f"\n⚠️  You have tiles in short suit ({self.shortSuit})")
            print("Short suit tiles:", end=" ")
            for i, c in enumerate(self.hidden):
                if c.suit == self.shortSuit:
                    print(f"{i+1}:{self.tile_to_emoji(c)}", end=" ")
            print()
        
        while True:
            try:
                choice = input(f"\nEnter tile number to discard (1-{len(self.hidden)}): ").strip()
                idx = int(choice)
                
                if idx < 1 or idx > len(self.hidden):
                    print(f"Please enter a number between 1 and {len(self.hidden)}")
                    continue
                
                card = self.hidden.pop(idx - 1)
                print(f"✓ Discarded: {self.tile_to_emoji(card)} ({card})")
                return card
                
            except ValueError:
                print("Invalid input. Please enter a number.")
