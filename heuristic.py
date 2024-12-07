from backgammon import *

# this is a function that returns the best move according to the heuristic
def heuristic(board):
    #check for boards in a won state
    if board[WHITE_BEARING] == 15:
        return 2000

    if board[BLACK_BEARING] == 15:
        return -2000

    #final total score, value for spaces occupied, spaces with two blocks, beared off pieces and pieces out
    score = 0
    OCC_VAL = 1
    PROT_VAL = 3
    BEAR_VAL = 35
    OUT_VAL = -10
    ATTACK_VAL = -6

    score += BEAR_VAL*board[WHITE_BEARING]
    score -= BEAR_VAL*board[BLACK_BEARING]
    score += OUT_VAL*board[WHITE_OUT]
    score -= OUT_VAL*board[BLACK_OUT]
    #counter for number of two stacks in a row
    counter = 0

    for ind, val in enumerate(board[BOARD_SPLICE]):
        pos = ind + 1
        attack_prob = 0
        if val == 1:
            for dist, prob in enumerate(roll_dist):
                if pos+dist+1 > 24:
                    break
                if board[pos + dist+1] < 0:
                    attack_prob += prob
            score += attack_prob * ATTACK_VAL

        if val == -1:
            for dist, prob in enumerate(roll_dist):
                if pos-dist - 1 < 1:
                    break
                if board[pos - dist - 1] > 0:
                    attack_prob += prob
            score -= attack_prob * ATTACK_VAL

        #if space has white piece
        if val > 0:
            #checking if there is a four prime or greater for black
            if counter < -3:
                score -= counter * counter

            #resets counter if prime is of insufficient length
            if counter < 0: counter = 0

            #if there is a stack of two or greater
            if val > 1:
                score += OCC_VAL * PROT_VAL
                counter += 1
            #for single pieces
            else:
                score += OCC_VAL
                if counter > 3:
                    score += counter * counter
                counter = 0
            score += pos*val
        #black version of all above code
        elif val < 0:
            if counter > 3:
                score += counter * counter
            if counter > 0: counter = 0

            if val < -1:
                counter -= 1
                score -= OCC_VAL * PROT_VAL

            else:
                score -= OCC_VAL

                if counter < -3:
                    score -= counter * counter

                counter = 0

        #if space is empty, reset prime counter
        else:
            counter = 0

            score -= (24-pos) * val
    return score

def bestmove(legal_moves, white_turn = True):

    best = legal_moves[0] # the first one is the base one ot compare to
    best_rollout = heuristic(best[0]) # rollout value is its heuristic value

    for move in legal_moves: # go over all the moves and compare it

        temp = heuristic(move[0]) # get its heuristic value
        if white_turn and temp > best_rollout: # white wants to maximize the heuristic score

            best = move
            best_rollout = temp

        if not white_turn and temp< best_rollout: # black wants to minimize it

            best = move
            best_rollout = temp

    return best # return the best
