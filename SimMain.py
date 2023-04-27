from Game import *
from Mahjong import *
from PlayerImpl import *
import logging
import pandas as pd
logging.basicConfig(level='WARNING')
#logging.basicConfig(level="INFO", filename='./gamelog/simgame.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

import numpy as np
#np.random.seed(53)

scores = []

def main():
    for i in range(50):
        print(f"Game {i+1}")
        east, south, west, north = CheatingPlayer(900), SimpleAIPlayer(101), SimpleAIPlayer(102), SimpleAIPlayer(103)
        game = Game(players=[east, south, west, north], verbose=False, observer=Observer())
        game.start()
        scores.append(dict(zip([p.id for p in game.players], [p.score for p in game.players]))) 
    score_df = pd.DataFrame(scores)
    total_df = score_df.sum()
    print(score_df)
    print(total_df)

if __name__ == "__main__":
    main()