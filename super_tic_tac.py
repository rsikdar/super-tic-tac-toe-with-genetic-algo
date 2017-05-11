import random
import copy
import sys
sys.path.append('C:\Python34\Lib\site-packages')

import simplejson
from deap import creator, base, tools, algorithms

#Counter class adapted from util.py in CS 188 projects
#A dictionary with some extra methods
class Counter(dict):
	def __getitem__(self, idx):
		self.setdefault(idx, 0)
		return dict.__getitem__(self, idx)

	def totalCount(self):
		return sum(self.values())

	def normalize(self):
		total = float(self.totalCount())
		if total == 0: return
		for key in self.keys():
			self[key] = self[key] / total

	def maxKey(self):
		v=list(self.values())
		k=list(self.keys())
		return k[v.index(max(v))]

#Object for a local board
#1 is player 1, -1 is player 2.
#Position index of the board attribute
# 0 1 2
# 3 4 5
# 6 7 8
class Mini_Board():
	def __init__(self):
		self.board = [0 for x in range(9)]
		self.winner = 0
		self.is_tied = False

	#returns winner if there is one.
	#Once there is a winner, repeated calls will return
	#first winner
	def check_winner(self):
		if self.winner != 0 or self.is_tied == True:
			return self.winner
		#check rows
		b = self.board
		for i in range(3):
			if abs(sum(b[3*i:3*i+3])) == 3:
				self.winner = b[3*i]
				return self.winner
		#check col
		for i in range(3):
			if abs(b[i] + b[i+3] + b[i+6]) == 3:
				self.winner = b[i]
				return self.winner
		#check diagonals
		if abs(b[0] + b[4] + b[8]) == 3 or abs(b[2] + b[4] + b[6]) == 3:
			self.winner = b[4]
			return self.winner
		#no winner, is the game board full
		if self.is_full():
			self.is_tied = True
		return 0

	def is_full(self):
		for i in self.board:
			if i == 0:
				return False;
		return True

	def move(self, player, pos):
		assert(self.board[pos] == 0)
		self.board[pos] = player
		return self.check_winner()

#Object for the 9x9 board. Comprised of 9 Mini_Board objects
#1 is player 1, -1 is player 2.
# 0 1 2
# 3 4 5
# 6 7 8
class Board():
	def __init__(self, strategy1, strategy2):
		self.board = [Mini_Board() for x in range(9)]
		self.winner = 0
		self.player_turn = 1
		self.players = {1 : strategy1, -1 : strategy2}
		self.game_over = False
		self.next_board = None
		self.steps = 0

	#returns winner if there is one.
	#Once there is a winner, repeated calls will return first winner.
	#Unlike Mini_board.Uses game_over attribute instead of is_tied attribute
	def check_winner(self):
		if self.winner != 0 or self.game_over == True:
			return self.winner
		#check rows
		b = self.board
		for i in range(3):
			if abs(sum([j.check_winner() for j in b[3*i:3*i+3]])) == 3:
				self.winner = b[3*i].winner
				self.game_over = True 
				return self.winner
		#check col
		for i in range(3):
			if abs(b[i].check_winner() + b[i+3].check_winner() + b[i+6].check_winner()) == 3:
				self.winner = b[i].check_winner()
				self.game_over = True 
				return self.winner
		#check diagonals
		if abs(b[0].check_winner() + b[4].check_winner() + b[8].check_winner()) == 3\
				or abs(b[2].check_winner() + b[4].check_winner() + b[6].check_winner()) == 3:
			self.winner = b[4].check_winner()
			self.game_over = True 
			return self.winner
		#no winner, is it a tie game?
		self.game_over = True
		for s in b:
			if not s.is_full():
				self.game_over = False
		return 0

	#Prints the board in a nice format
	def print_board(self):
		def printHelper(shift):
			for i in range(9):
				b = self.board[i % 3 + shift]
				start = 3 * (i // 3)
				to_print = b.board[start:start + 3]
				for j in to_print:
					print("  " + str(j).ljust(4), end = '')
				print("  |  ", end='')
				if i % 3 == 2:
					print('  ')

		printHelper(0)
		print("-"*70)
		printHelper(3)
		print("-"*70)
		printHelper(6)

	#Prints only the winner of each Mini_Board
	def print_board_simple(self):
		for i in range(9):
			b = self.board[i]
			print("  " + str(b.winner).ljust(3) + " | ", end='')
			if i % 3 == 2 and i != 8:
				print('  ')
				print("-"*24)

	#Makes a move on the board for the given player
	#board num only used if next_board is not set
	def player_move(self, player, board_num, pos):
		if (self.next_board != None):
			board_num = self.next_board
		had_winner = self.board[board_num].winner
		has_winner = self.board[board_num].move(player, pos)
		self.next_board = pos
		#checking that there is a valid move possible
		if self.board[self.next_board].is_full():
			self.next_board = None
		self.player_turn = player * -1
		winner = self.check_winner()
		return winner

	#executes a turn in the game. 
	#Looks up which strategy to call, and executes the move it returns
	def game_move(self):
		board_num, pos = self.players[self.player_turn](self)
		self.player_move(self.player_turn, board_num, pos)
		self.steps += 1

	#Returns a list of all valid moves for the current game state
	def possible_moves(self):
		possible_moves = []
		next_board_num = self.next_board
		if next_board_num == None:
			#all possible moves
			for i in range(len(self.board)):
				mini_board = self.board[i]
				for j in range(len(mini_board.board)):
					if mini_board.board[j] == 0:
						possible_moves.append((i, j))
		else:
			next_board = self.board[self.next_board]
			for j in range(len(next_board.board)):
				if next_board.board[j] == 0:
					possible_moves.append((next_board_num, j))
		assert(len(possible_moves) != 0)
		return possible_moves

	#Changes the strategy of the given player for future moves
	def set_strategy(self, player, strategy):
		self.players[player] = strategy

	#Plays the game out. Will stop after steps if given
	#Otherwise, only 81 steps are needed before the game must end
	def simulate(self, steps=90):
		while not self.game_over and steps > 0:
			self.game_move()
			steps -= 1
		return self.check_winner(), self.steps;

#Plays a game iterations many times between s1 and s2
def start(s1, s2, iterations):
	win_rate = Counter()
	for _ in range(iterations):
		game = Board(s1, s2)
		winner, steps = game.simulate()
		win_rate[winner] += 1
	win_rate.normalize()
	return (win_rate[1], win_rate[-1], win_rate[0])

#Given a game, will return what move to make
#Picks a move at random
def random_strat(game):
	return random.choice(game.possible_moves())

#Given a game, will return what move to make
#Plays iterations number of simulations for each possible move,
#and picks the one with the highest score
def monte_carlo_strat(game):
	iterations = 5
	lossPenalty = 10 
	#for each possible move, we copy, make the move 
	#and play out a random simulation
	possible_moves = game.possible_moves() 
	win_rates = Counter()
	curr_steps = game.steps
	for _ in range(iterations):
		for move in possible_moves:
			gameCopy = copy.deepcopy(game)
			def strategy(game):
				if game.steps == curr_steps:
					return move
				else:
					return random_strat(game)

			gameCopy.set_strategy(game.player_turn, strategy)
			gameCopy.set_strategy(game.player_turn * -1, random_strat)
			winner, end_steps = gameCopy.simulate()
			#we add weighting such that the less move solutions are preferred
			#81 is the max number of steps
			weight = (81 - end_steps) / (81 - curr_steps)
			if winner == -1:
				weight *= lossPenalty
			win_rates[move] += weight * winner
	return win_rates.maxKey()

#Trains a genetic algorithm, given feature size, and an eval function
def run_GA(IND_SIZE, eval_func):
	creator.create("FitnessMulti", base.Fitness, weights=(1, -2.0, 0.5))
	creator.create("Individual", list, fitness=creator.FitnessMulti)

	toolbox = base.Toolbox()
	toolbox.register("attr_float", random.random)
	toolbox.register("individual", tools.initRepeat, creator.Individual,
	                 toolbox.attr_float, n=IND_SIZE)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("mate", tools.cxTwoPoint)
	toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("evaluate", eval_func)
	population = toolbox.population(n=25)

	NGEN=40
	for gen in range(NGEN):
	    offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.4)
	    fits = toolbox.map(toolbox.evaluate, offspring)
	    for fit, ind in zip(fits, offspring):
	        ind.fitness.values = fit
	    population = toolbox.select(offspring, k=len(population))
	top = tools.selBest(population, k=1)
	return top

#Trains a GA with each position as a feature
#returns the trained weights
#board will be numbered as follows
#0 1 2 |  9 10 11 | 18 19 20
#3 4 5 | 12 13 14 | 21 22 23
#6 7 8 | 15 16 17 | 24 25 26
#----------------------------
#27 28 29....and so on
def run_weighted_GA():
	#we have the solution play against a random bot
	def eval_weights(individual):
		def weighted_strategy(game):
			possible_moves = game.possible_moves()
			#assigning weights to all positions, and pick the highest
			pos_weights = Counter()
			for move in possible_moves:
				board, pos = move
				pos_weights[move] = individual[board*9 + pos]
			return pos_weights.maxKey()
		return start(weighted_strategy, random_strat, 5)
	top = run_GA(81, eval_weights)
	f = open('weighted_strategy', 'w')
	simplejson.dump(top[0], f)
	f.close();
	def final_weighted(game):
		possible_moves = game.possible_moves()
		#assigning weights to all positions, and pick the highest
		pos_weights = Counter()
		for move in possible_moves:
			board, pos = move
			pos_weights[move] = top[0][board*9 + pos]
		return pos_weights.maxKey()
	win_rate = start(final_weighted, random_strat, 100)
	print("weighted strategy vs random")
	print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))
	win_rate = start(final_weighted, monte_carlo_strat, 100)
	print("weighted strategy vs monte carlo")
	print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))
	return top[0]


#heuristic that will return a move given a game state
#moves that restrict the opponents next move given higher rank
#gives a score for every move 
def opponent_move_heuristic(game):
	move_rank = Counter()
	for move in game.possible_moves():
		board, pos = move	
		rank = 0
		for i in game.board[pos].board:
			if i == 0:
				rank -= 1
		move_rank[move] = rank	+ 9
		if rank == 0:
			move_rank[move] = 0
		#having no spots is high count
	move_rank.normalize()
	return move_rank

#heuristic that will return a move given a game state
#ranking of 4 if we win, 2 if we tie or have not ended, and 1 if we lose
def game_ending_heuristic(game):
	win_val = 4
	tie_val = 2
	ongoing_val = 2
	loss_val = 1
	move_rank = Counter()
	curr_steps = game.steps
	for move in game.possible_moves():
		gameCopy = copy.deepcopy(game)
		#simulation should end before 2nd move
		def strategy(game):
			if game.steps == curr_steps:
				return move
			else:
				assert("game should have ended")
				s = 1/0
				return move

		gameCopy.set_strategy(game.player_turn, strategy)
		gameCopy.set_strategy(game.player_turn * -1, random_strat)
		winner, end_steps = gameCopy.simulate(2)
		if (gameCopy.game_over):
			if winner == 1:
				move_rank[move] = win_val 
			if winner == -1:
				move_rank[move] = loss_val 
			if winner == 0:
				move_rank[move] = tie_val
		else:
			move_rank[move] = ongoing_val
	move_rank.normalize()
	return move_rank

#heuristic that will return a move given a game state
#rank of 1 if board_number = position number
#ex. middle box in middle board has a rank of 1
def same_pos_board_heuristic(game):
	move_rank = Counter()
	for move in game.possible_moves():
		if move[0] == move[1]:
			move_rank[move] = 1
		else:
			move_rank[move] = 0
	move_rank.normalize()
	return move_rank

#Trains weights for using opponent_move_heuristic,
#game_ending_heuristic, and same_pos_board_heuristic
#returns the trained weights
def run_heuristic_GA():
	#we have the solution play against a random bot
	def eval_heuristic_weights(individual):
		def heuristic_strategy(game):	
			possible_moves = game.possible_moves()
			opponent_move_ranks = opponent_move_heuristic(game)
			game_ending_ranks = game_ending_heuristic(game)
			same_pos_ranks = same_pos_board_heuristic(game)
			heuristics = [opponent_move_ranks, game_ending_ranks, same_pos_ranks]
			#assigning weights to all positions, and pick the highest
			pos_weights = Counter()
			for move in possible_moves:
				for i in range(3):
					pos_weights[move] += individual[i] * heuristics[i][move]
			return pos_weights.maxKey()
		return start(heuristic_strategy, random_strat, 5)
	top = run_GA(3, eval_heuristic_weights)
	f = open('heuristic_strategy', 'w')
	simplejson.dump(top[0], f)
	f.close();
	def final_strat(game):
		possible_moves = game.possible_moves()
		opponent_move_ranks = opponent_move_heuristic(game)
		game_ending_ranks = game_ending_heuristic(game)
		same_pos_ranks = same_pos_board_heuristic(game)
		heuristics = [opponent_move_ranks, game_ending_ranks, same_pos_ranks]
		#assigning weights to all positions, and pick the highest
		pos_weights = Counter()
		for move in possible_moves:
			for i in range(3):
				pos_weights[move] += top[0][i] * heuristics[i][move]
		return pos_weights.maxKey()
	win_rate = start(final_strat, random_strat, 100)
	print("heuristic strategy vs random")
	print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))
	win_rate = start(final_strat, monte_carlo_strat, 100)
	print("heuristic strategy vs monte carlo")
	print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))
	return top[0]

s1 = run_heuristic_GA()
s2 = run_weighted_GA()
def final_strat_heuristic(game):
	possible_moves = game.possible_moves()
	opponent_move_ranks = opponent_move_heuristic(game)
	game_ending_ranks = game_ending_heuristic(game)
	same_pos_ranks = same_pos_board_heuristic(game)
	heuristics = [opponent_move_ranks, game_ending_ranks, same_pos_ranks]
	#assigning weights to all positions, and pick the highest
	pos_weights = Counter()
	for move in possible_moves:
		for i in range(3):
			pos_weights[move] += s1[i] * heuristics[i][move]
	return pos_weights.maxKey()

def final_weighted(game):
		possible_moves = game.possible_moves()
		#assigning weights to all positions, and pick the highest
		pos_weights = Counter()
		for move in possible_moves:
			board, pos = move
			pos_weights[move] = s2[board*9 + pos]
		return pos_weights.maxKey()

win_rate = start(final_weighted, final_strat_heuristic, 100)
print("random_strat  vs final_strat_heuristic")
print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))
win_rate = start(random_strat, final_weighted, 100)
print("random_strat vs final_strat_heuristic ")
print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))

win_rate = start(monte_carlo_strat, final_strat_heuristic, 100)
print("monte_carlo_strat  vs final_strat_heuristic")
print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))
win_rate = start(monte_carlo_strat, final_weighted, 100)
print("monte_carlo_strat vs weighted_strategy ")
print("P1 - Wins: %f, Losses: %f, Ties: %f" % (win_rate[0], win_rate[1], win_rate[2]))