class BoardPrinter: # this class just has a string function that is used to print the board in a reasonable fashion
    def __init__(self, board):

        self.board = board #array representation of board state

    def __str__(self):

        answer = " "
        for num in range(1,25):

            answer += str(num) + " "

        rows = max(max(self.board), abs(min(self.board)))
        temp = self.board.copy()
        for row in range(rows):

            answer += '\n'
            counter = 1
            for i in range(1, 25):

                answer += " " * len(str(counter))
                if temp[i] == 0:

                    answer += ' '

                elif temp[i] > 0:

                    answer += 'X'
                    temp[i] -= 1

                elif temp[i] < 0:

                    answer += 'O'
                    temp[i] += 1

                counter += 1

        answer += '\n'
        WHITE_BEARING = 25
        BLACK_BEARING = 0
        WHITE_OUT = 26
        BLACK_OUT = 27
        answer += f'White pieces beared off: {self.board[WHITE_BEARING]}'
        answer += '\n'
        answer += f'Black pieces beared off: {self.board[BLACK_BEARING]}'
        answer += '\n'
        answer += f'White pieces out: {self.board[WHITE_OUT]}'
        answer += '\n'
        answer += f'Black pieces out: {self.board[BLACK_OUT]}'
        answer += '\n'
        return answer