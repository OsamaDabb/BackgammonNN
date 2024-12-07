import numpy as np
import random
import math
from board_display import *
import time

# The following are the indices in our backgammon array that store the respective information

WHITE_BEARING = 25
BLACK_BEARING = 0
WHITE_OUT = 26
BLACK_OUT = 27
WHITE_TURN = 28
BOARD_SPLICE = slice(1, 25)
starting_board = np.zeros(29, dtype=int)

#Creates a starting board with the traditional piece positions, also randomly selects a starting player
def starting_board():
    #white_turn = random.random() > 0.5
    return np.array([0,2,0,0,0,0,-5,0,-3,0,0,0,5,-5,0,0,0,3,0,5,0,0,0,0,-2,0,0,0,True])

#Rolls die, handles the case of double rolls. Also allows you to reroll in case
#of doubles by setting first_turn=True (which is necessary on the first turn)
def roll(first_turn=False):
    roll_1 = random.randint(1,6)
    roll_2 = random.randint(1,6)
    if roll_1 == roll_2:
        if first_turn:
            return roll(first_turn=True)
        return np.full(4,roll_1)
    else:
        return np.array([roll_1,roll_2])

#Function that gives all possible single moves given a board state and set of rolls
def possible_moves(board, rolls):
    #options is an array of all possible moves given as:
    #(new board_state (array), string clarifying move taken (str), roll used to make that move (int))
    options = []
    #Creates the variable can_bear, which is true only if the conditions for bearing
    #for the current player are met
    if board[WHITE_TURN]:
        can_bear = not np.any([x > 0 for x in board[1:19] + [board[WHITE_OUT]]])
    else:
        can_bear = not np.any([x < 0 for x in board[7:25] + [board[BLACK_OUT]]])

    #Branch of logic assuming white players turn
    if board[WHITE_TURN]:
        #Branch of logic assuming there is a piece that needs to be brought into the game
        if board[WHITE_OUT]:
            for roll in rolls:
                #only considers option if the space you rolled to is a valid landing spot
                if board[roll] >= -1:
                    possible_move = board.copy()
                    if possible_move[roll] == -1:
                        possible_move[roll] = 0
                        possible_move[BLACK_OUT] += 1
                    possible_move[roll] += 1
                    possible_move[WHITE_TURN] = len(rolls) != 1
                    possible_move[WHITE_OUT] -= 1
                    options.append((possible_move, f'Bring in white piece to position {roll}',roll))

        #Assuming no pieces need to be brought back on board
        else:
            #Iterate over every space on the board
            for ind, space in enumerate(board[BOARD_SPLICE]):
                #position used instead of index since board is one_indexed
                pos = ind + 1
                #checking only spaces where there are white pieces (value at space > 0)
                if space > 0:
                    #checking possible move for piece given the rolls
                    for roll in rolls:
                        #creates option of moving piece to totally empty space
                        if (pos + roll) < 25 and board[pos + roll] >= 0:
                            possible_move = board.copy()
                            possible_move[pos + roll] += 1
                            possible_move[WHITE_TURN] = len(rolls) != 1
                            possible_move[pos] -= 1
                            options.append((possible_move, f'Move piece {roll} steps from position {pos} to position {pos + roll}.',roll))
                        #create option if the space has a blot to be captured
                        elif (pos + roll) < 25 and board[pos + roll] == -1:
                            possible_move = board.copy()
                            possible_move[pos + roll] = 1
                            possible_move[BLACK_OUT] += 1
                            possible_move[WHITE_TURN] = len(rolls) != 1
                            possible_move[pos] -= 1
                            options.append((possible_move, f'Move piece {roll} steps from position {pos} to capture opponents piece at {pos + roll}.',roll))

                        #create option if the player can legally bear and has rolled a high enough number to bear
                        elif can_bear and (pos + roll) >= 25:
                            #small logic block due to specific rules of bearing
                            #i.e. you can only bear a piece where space != roll if no higher value pieces can be moved
                            if pos == 19:
                                no_alt = True
                            else:
                                no_alt = np.all([x < 1 for x in board[19:pos]])
                            #To bear off a piece, you must be exactly (roll) steps from goal
                            #or this is the
                            if roll + pos == 25 or no_alt:
                                possible_move = board.copy()
                                possible_move[WHITE_BEARING] += 1
                                possible_move[WHITE_TURN] = len(rolls) != 1
                                possible_move[pos] -= 1
                                options.append((possible_move, f'Bear off piece from position {pos} using {roll} steps.',roll))

    #The below code block is identical to the above, but is from the perspective
    #of the black piece player
    else:
        if board[BLACK_OUT]:
            for roll in rolls:
                if board[25-roll] <= 1:
                    possible_move = board.copy()
                    if possible_move[25-roll] == 1:
                        possible_move[25-roll] = 0
                        possible_move[WHITE_OUT] += 1
                    possible_move[25-roll] -= 1
                    possible_move[WHITE_TURN] = len(rolls) == 1
                    possible_move[BLACK_OUT] -= 1
                    options.append((possible_move, f'Bring in black piece to position {roll}',roll))

        else:
            for ind, space in enumerate(board[BOARD_SPLICE]):
                pos = ind + 1
                if space < 0:
                    for roll in rolls:
                        #Check if the space is empty
                        if (pos - roll) > 0 and board[pos - roll] <= 0:
                            possible_move = board.copy()
                            possible_move[pos - roll] -= 1
                            possible_move[WHITE_TURN] = len(rolls) == 1
                            possible_move[pos] += 1
                            options.append((possible_move, f'Move piece {roll} steps from position {pos} to position {pos - roll}.',roll))
                        #Check if the space has a blot to be captured
                        elif (pos - roll) > 0 and board[pos - roll] == 1:
                            possible_move = board.copy()
                            possible_move[pos - roll] = -1
                            possible_move[WHITE_OUT] += 1
                            possible_move[WHITE_TURN] = len(rolls) == 1
                            possible_move[pos] += 1
                            options.append((possible_move, f'Move piece {roll} steps from position {pos} to capture opponents piece at {pos - roll}.',roll))
                        #check if the player can bear off their piece
                        elif can_bear and (pos - roll) <= 0:
                            if pos == 6:
                                no_alt = True
                            else:
                                no_alt = np.all([x > -1 for x in board[pos+1:7]])
                            if pos - roll == 0 or no_alt:
                                possible_move = board.copy()
                                possible_move[BLACK_BEARING] += 1
                                possible_move[WHITE_TURN] = len(rolls) == 1
                                possible_move[pos] += 1
                                options.append((possible_move, f'Bear off piece from position {pos} using {roll} steps.',roll))

    #Handles the case where no moves are available to the player
    if not options:
        new_board = board
        new_board[WHITE_TURN] = not board[WHITE_TURN]
        return [(new_board, "No possible moves", None)]

    return options

#Function for giving the set of moves that use all given rolls for a user
def full_step(board, rolls):
    #branch handling a four roll turn
    if len(rolls) == 4:
        #creates branching tree of all possible 4 move combinations by calling
        #possible_moves recursively on its own children
        curr_turn = board[WHITE_TURN]
        rolls = np.asarray(rolls[0:2])
        options = possible_moves(board, rolls)
        for i in range(3):
            if options[0][2] == None:
                break
            new_options = []
            for option in options:
                next_moves = possible_moves(option[0], rolls)
                move_descriptions = [option[1] + "\nThen " + x[1].lower() for x in next_moves]
                new_options += [(next_moves[i][0], move_descriptions[i], next_moves[i][2]) for i in range(len(next_moves))]
            options = new_options

        #removes duplicate boards from the set before returning them as a list
        seen_boards = [[0]*29]
        filtered_options = []
        for ind, val in enumerate(options):
            if val[0].tolist() not in seen_boards:
                seen_boards.append(val[0].tolist())
                filtered_options.append(val)

        for option in filtered_options:
            option[0][WHITE_TURN] = not curr_turn


        return filtered_options

    else:
        #For cases of two dice rolls, calls possible_moves twice
        #first using both rolls as the input, then again using only the roll not
        #used by the program in each case as the input
        options = possible_moves(board, rolls)
        curr_turn = board[WHITE_TURN]

        full_options = []
        for option in options:
            if options[0][2] == None:
                full_options = options
                break
            rem_roll = [x for x in rolls if x != option[2]]
            second_moves = possible_moves(option[0], rem_roll)
            move_descriptions = [option[1] + " Then " + x[1] for x in second_moves]
            full_options += [(second_moves[i][0], move_descriptions[i], second_moves[i][2]) for i in range(len(second_moves))]

        #removes duplicate moves
        seen_boards = [[0]*29]
        filtered_options = []
        for ind, val in enumerate(full_options):
            if val[0].tolist() not in seen_boards:
                seen_boards.append(val[0].tolist())
                filtered_options.append(val)

        for i in filtered_options:
            i[0][WHITE_TURN] = not curr_turn

        return filtered_options

# This cell sets up the code that allows a person to play a game with the AI

import sys

def game_over(board): # as soon one of the players has all of their pieces beared off then they win

    return board[BLACK_BEARING] == 15 or board[WHITE_BEARING] == 15


def find_winner(board):

    ''' Assumes that the game is over
    Return which player won the game'''

    if board[BLACK_BEARING] == 15:

        return 'Black'

    else:

        return 'White'


def play_move(board, index, roll, pieces, mult): # modifies the board based on the move

    board[index - roll] -= mult*pieces
    board[index] += mult*pieces

def print_rolls(rolls): # prints the rolls

    printout = 'Dice rolls are '
    for roll in rolls:

        printout += str(roll) + ' '

    return print(printout)


def get_player_move(board, rolls, moves): # this move gets the player move

    '''Provides a set of options of possible moves to the user and gets them to choose'''
    print('Here is a list of possible moves: ')
    counter = 1 # checks how many options they have

    for move in moves: # go over the different options and print them for the user

        print(f'Option {counter} is :')
        print(BoardPrinter(move[0]))
        print(move[1])
        print()
        counter += 1

    choice = 0 # stores the user choice
    while True: # this makes sure the user makes a legal move

        choice = input('Which move do you prefer? ')

        time.sleep(3)
        if choice == 'quit':

            sys.exit('Game has been ended')

        if not choice.isnumeric() or not 0 < int(choice) < counter:

            print('Please enter a valid option number')
            continue

        choice = int(choice)
        break

    return moves[choice-1] # send the chosen choice back


# this block of code calculates the probability of getting each possible number from a dice roll
# the result is stored in an array for later use
roll_dist = [0] * 12
for i in range(1,7):
    for j in range(1,7):
        if i == j:
            for k in range(1,5):
                if i*k-1 < 13:
                    roll_dist[i*k-1] += 1
        else:
            roll_dist[i-1] += 1
            roll_dist[j-1] += 1
            roll_dist[i+j-1] += 1
roll_dist = [x/36 for x in roll_dist]
