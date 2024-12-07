import numpy as np
from backgammon import *
from heuristic import *

def winner_score(board):

    if board[WHITE_BEARING] == 15:
        return 2000

    if board[BLACK_BEARING] == 15:
        return -2000

class ChanceNode: # holds chance nodes

    def __init__(self, board): # takes in the board

        self.board = board # assigns the board
        self.chance = True # declares that this is a chance node


    def __equal__(self, other): # this compares if two chance nodes are equal

        return other.chance and other.board == self.board


class DecisionNode: # holds decision nodes

    def __init__(self, board, rolls): # similar to chance nodes but it also holds the roll that got it here

        self.board = board
        self.chance = False # declares that this is not a chance node
        self.rolls = rolls # the rolls that brought it here

    def __equal__(self, other): # compares two decision nodes and ensures the same roll brought them to the same board state

        return other.chance and other.board == self.board and self.rolls == other.rolls


def sample(tree, T_chance, T_decision, chance_mapper, V, m = 10, model = None, white_turn = True): # sampling method which does both exploration and expansion

    if not m: # if you don't have any more layers to discover then return

        return 0

    elif tree.chance: # if this is a chance node

        rolled = roll() # find a random roll
        r = 0 # for now, the reward for this roll is the sum of the dice normalized
        hor = DecisionNode(tree.board, rolled) # build the decision node for this roll
        if hor not in T_decision: # if it isn't already in T, then add it to it

            T_decision[hor] = 0

        reward = r + sample(hor, T_chance, T_decision, chance_mapper, V, m-1, model, not white_turn) # find the net reward by going down a layer

    elif not T_decision.get(tree,0): # if it is an unexplored decision node then explore it

        T_decision[tree] = 0
        reward = rollout(1, tree.board) # expects the reward from the rollout function

    else: # if it an explored decision node

        if game_over(tree.board):

            reward = winner_score(tree.board)

        else:
            a = select_action(tree, T_chance, T_decision, chance_mapper, V, m,white_turn = white_turn) # find the board for the corresponding best action
            if str(a) not in chance_mapper:

                ha = ChanceNode(a) # make a chance node out of this
                chance_mapper[str(a)] = ha

            else:

                ha = chance_mapper[str(a)]
            reward = sample(ha, T_chance, T_decision, chance_mapper, V, m) # carry out the rest from the chance node


    T = T_chance if tree.chance else T_decision # declare T based on tree's type to make next line simpler
    V[tree] = (reward + T.get(tree, 0) * V.get(tree, 0))/(T.get(tree, 0) + 1) # update the value of the utility of this node
    T[tree] = T.get(tree, 0) + 1 # increment the number of times we have seen this node
    return reward # return the net reward


def select_action(tree, T_chance, T_decision, chance_mapper, V, m , C = math.sqrt(2), white_turn = True): # takes in a decision tree and returns the best action

    A = full_step(tree.board, tree.rolls) # returns the possibilities from this roll

    U = [] # stores the unexplored children
    for a in A: # for every turn for this roll check if it has been seen

        if str(a[0]) in chance_mapper:

            ha = chance_mapper[str(a[0])]

        else:

            ha = ChanceNode(a[0]) # construct the chance node
            chance_mapper[str(a[0])] = ha

        if not T_chance.get(ha, 0): # if it has not been explored, then just append it

            U.append(a[0])

    if U: # if there are unexplored nodes then return a random one

        a = random.choice(U)
        return a

    else: #otherwise find the one with the best UCB value

        max_node = A[0][0]
        max_val = float('-inf')

        for a in A: # go over all the explored nodes

            if str(a[0]) in chance_mapper:

                ha = chance_mapper[str(a[0])]

            else:

                ha = ChanceNode(a[0]) # construct the chance node
                chance_mapper[str(a[0])] = ha

            val = V[ha]/(2*m) + C * math.sqrt(math.log(T_decision[tree])/ T_chance[ha]) # using formula from the research paper
            if white_turn and val > max_val:

                max_val = val
                max_node = a[0]

            if not white_turn and val < max_val:

                max_val = val
                max_node = a[0]

        return max_node # return board with max value


TIME = 250 # this variable is the spread factor on our MCTS algorithm
def pUCT(board, roll, legal_moves, iterations):

    T_chance = {} # this is the T dict for chance nodes
    T_decision = {} #this is the T dict for decision nodes
    V = {} # this is the utility dict for all nodes
    chance_mapper = {}

    start_node = DecisionNode(board, roll)
    for i in range(TIME):
        sample(start_node, T_chance, T_decision, chance_mapper, V, iterations)
    # We look for the start node that has the most playouts -
    # not win % because this way favors nodes that have been tried quite a bit
    # (and are also good, or they wouldn't have been tried
    highest_utility = (0,float('-inf'))
    for i in range(len(legal_moves)):

        #x = ChanceNode(legal_moves[i][0])
        x = chance_mapper.get(str(legal_moves[i][0]), None)
        if V.get(x,float('-inf')) > highest_utility[1]:
            highest_utility = (i, V.get(x,float('-inf')))

    return legal_moves[highest_utility[0]]

def rollout(choice, board):

    return heuristic(board)

