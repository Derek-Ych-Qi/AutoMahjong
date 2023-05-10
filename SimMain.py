from Game import *
from Mahjong import *
from PlayerImpl import *
import logging
import pandas as pd
from collections import deque
logging.basicConfig(level='WARNING')
#logging.basicConfig(level="INFO", filename='./gamelog/simgame.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

import numpy as np
#np.random.seed(53)

scores = []

def main():
    for i in range(4):
        seed = np.random.randint(0,2**31)
        print(f"Game {i+1}, seed={seed}")
        for j in range(4):
            players = deque([CheatingPlayer(900), SimpleAIPlayer(101), RandomAIPlayer(102, 0.01), RandomAIPlayer(103, 0.1)])
            players.rotate(j)
            game = Game(players=list(players), verbose=False, observer=Observer(), seed=seed)
            game.start()
            scores.append(dict(zip([p.id for p in game.players], [p.score for p in game.players]))) 
    score_df = pd.DataFrame(scores)
    total_df = score_df.sum()
    print(score_df)
    print(total_df)

if __name__ == "__main__":
    main()