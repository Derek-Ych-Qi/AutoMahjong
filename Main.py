from Game import *
from Mahjong import *
from PlayerImpl import *
import logging
from collections import deque
logging.basicConfig(level="INFO")

import numpy as np
#np.random.seed(53)

scores = []
def main():
    seed = np.random.randint(0,2**31)
    print(f"Game 0, seed={seed}")
    for i in range(4):
        players = deque([CheatingPlayer(900), SimpleAIPlayer(101), RandomAIPlayer(102, 0.01), HumanPlayer('Catherine')])
        players.rotate(i)
        game = Game(players=list(players), verbose=False, observer=None, seed=seed)
        game.start()
        scores.append(dict(zip([p.id for p in game.players], [p.score for p in game.players]))) 
    score_df = pd.DataFrame(scores)
    total_df = score_df.sum()
    print(score_df)
    print(total_df)

if __name__ == "__main__":
    main()