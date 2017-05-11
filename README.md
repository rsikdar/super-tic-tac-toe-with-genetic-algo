# Super-tic-tac-toe-with-genetic-algo
Developing strategies for super tic-tac-toe using genetic algorithms (DEAP library).


## Game rules

Taken from the wikipedia article: https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe

Super tic-tac-toe is a board game composed of nine tic-tac-toe boards arranged in a 3-by-3 grid. Players take turns playing in the smaller tic-tac-toe boards until one of them wins in the larger tic-tac-toe board. Each small 3-by-3 tic-tac-toe board is referred to as a local board, and the larger 3-by-3 board is referred to as the global board.

The game starts with X playing wherever he wants in any of the 81 empty spots. This move 'sends' his opponent to its relative location. For example, if X played in the middle of his local board, then O needs to play next in the local board in the middle of the global board.
If a move is played so that it is to win a local board by the rules of normal tic-tac-toe, then it wins that local board. If a player is sent to a board that is completely full, they may move in any local board. When one player has won 3 local boards in a line, they have won the game.

## Computability

Search space analysis of super tic-tac-toe:

The first move of the game has 81 different possibilities. After that the moves are constrained to a single board. There will be 8 boards (the first board has one filled in already) that have 9 choices when you first arrive. After that there will 9 board with 8 choices, 9 with 7 choices, 9 with 6, etc, until you are forced to move in the last spot. So at the beginning of the game there will be: 81*9^8*8^9*7^9*6^9*5^9*4^9*3^9*2^9 = 9.8*10^50 ways to randomly fill in the whole board. Many paths will win the game early, so the actual search space will be less than this, but as you can see the number would still be way to big to brute force.

Taken from Khan Academy: https://www.khanacademy.org/computer-programming/tic-tac-toe-ception/1676336506

## Strategies implemented
There are 4 strategies implemented:
* A randomized strategy that give a game state, picks from all valid moves with equal probability. 
* Monte Carlo Algorithm

    Every turn, for every valid move we play out 5 games from the current state against a random strategy. Each game is scored by its win, loss, tie, and the number of steps it took to finish the game. The idea behind this is that too prefer games that let us win sooner, and wins over ties over losses.
    The Monte Carlo plays extremely well against a randomized strategy, although it takes sometime to run. It's win-rate over a 100 games was 0.88 wins, 0.01 losses, and 0.11 ties. Because of this, for testing our genetic algorithms we train on the randomized strategy and do final evaluation on both a randomized strategy as well as a Monte Carlo strategy.
* Weighted Positions Genetic Algorithm 

    Each individual is given 81 features. Each feature corresponds to a different box. For each turn, we evaluate all valid moves and pick the one with the highest weight. This idea was inspired from a paper on using genetic algorithms for playing Othello: http://www.genetic-programming.org/sp2003/Cunningham.pdf. I originally expected this strategy to perform poorly, as it doesn't take into account the game state at any point. However, this strategy was able to achieve a win rate of 0.79 wins, 0.16 losses, and 0.05 ties against a randomized_strategy over 100 games, and won all 100 games against the Monte Carlo algorithm. Initially, the trained algorithm performed poorly. By raising the mutation rate from 0.1 to 0.4, the results drastically improved. This is most likley because the inital population sample was quite small, and there weren't enough variety in values to achieve good results through mating and selection alone. The picture below has a colored diagrams of the trained weights. While some symmetric points do have similar weight values, many don't. This might be due to only running 40 generations with a population of 25, due to computation limits. If ran for longer, I would expect points that are rotations of each other to have similar weights.
  ![Alt text](/weighted_pos.JPG?raw=true "Weighted Positions")
* Weighted Heuristic Algorithm

    I developed three heuristics, and trained 3 features that represented the importance of each heuristic. The first heuristic ranked all valid moves by the amount of different moves the opposing player would have. The second ranked all valid moves by whether they would end the game, and who the winner would be. The third heuristic ranked all valid moves by whether or not the move was in the same position on the local board as was the local board to the big board ex. middle box in the middle local board. A sample training of these weights was [0.5481969638432325, 1.1622564564783708, 0.08596681111602267]. This strategy had slightly lower win rates against a randomized strategy; 0.76 wins, 0.08 Losses, 0.16 Ties. Against the monte carlo strategy it performed almost identically, with 0.98 wins 0 losses, and 0.02 ties. I originally expected this strategy to work better than the other algorithm, as it utilizes the game state before making decisions. 
    
## Competing the genetic algorithm structures against each other, and the importance of going first

Over a 100 games, the weighted positions strategy won all games it went first, and tied all 100 games when it went second. While the win_rates against the other strategies weren't too different, weighted strategies performed significantly better. The difference being able to not win a single game however while going second suggests the idea that the weights are based on the opening gambit. The strategy will always make the same opening move in all situations. Once the strategy is not able to force the opponent into a set options of move, its ability to win diminishes significantly. To test this, I then ran both trained strategies against a randomized strategy and monte carlo, but with the genetic algorithms as second:

Random  vs Weighted Heuristic  
Random - Wins: 0.000000, Losses: 0.000000, Ties: 1.000000

Random vs Weighted Positions  
Random - Wins: 0.290000, Losses: 0.620000, Ties: 0.090000

Monte Carlo  vs Weighted Heuristic  
Monte Carlo - Wins: 0.450000, Losses: 0.220000, Ties: 0.330000

Monte Carlo  vs Weighted Positions  
Monte Carlo - Wins: 0.800000, Losses: 0.070000, Ties: 0.130000

Weighted positions strategy did extremeley poorly when going second against Monte Carlo, and did worse than weighted heuristics in both cases. This is in line with how it did significantly worse when it went second against the weighted heuristics. This suggests that it is overfitted for going first, and that is weighted heuristics is better as a general solution.

One way to train against overfitting to the turn is by having the genetic algorithms not pick the highest move, but pick each move according to probabiliy of their weights. Another option would be to randomize whether it is player 1 or player 2 during training. Due to the time constraints, I did not get around to testing these ideas. 

## Future Improvements

A found a paper that analyzed the structure of the game and discusses formalizing and reducing it to other problems (Group Actions on Winning Games of Super Tic-Tac-Toe: https://arxiv.org/pdf/1606.04779.pdf). However, I came across the paper pretty late, and didn't have time to implement the ideas of reducing the total number of states to rotations and reflections of other states. I think this would have helped greatly in both genetic algorithms, and could lead to new heuristic functions that better capture the game state.  



