import argparse
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

BOARDS = ['debug', 'n00b', 'l33t', 'error'] # Availiable sudoku boards
MARGIN = 20 # Pixels around the board
SIDE = 50 # Width of every board cell

WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9 # Width and Height of the whole board

class SudokuError(Exception):
    """
    An application specific error.
    """
    pass

def parse_arguments():
    """
    Parses arguments of the form:
        sudoku.py <board name>
    Where `board name` must be in the `BOARD` list
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help="Desired board name",
                            type=str,
                            choices=BOARDS,
                            required=True
                            )
    args = vars(arg_parser.parse_args())
    return args['board']

class SudokuBoard(object):
    """
    Sudoku Board representation
    """
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    def __create_board(self, board_file):
        # create an initial matrix, or list of a list
        board = []

        # iterate over each line
        for line in board_file:
            line = line.strip()

            # raise error if line is longer or shorter than 9 characters
            if len(line) != 9:
                board = []
                raise SudokuError(
                    "Each line in the sudoku puzzle must be 9 chars long."
                )

            # create a list for the line
            board.append([])

            # then iterate over each character
            for c in line:
                # raise an error if the character is not an integer
                if not c.isdigit():
                    raise SudokuError(
                        "Valid characters for sudoky must be in 0-9"
                    )
                # Add to the latest list for the line
                board[-1].append(int(c))
        # Raise an error if there are not 9 lines
        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")

        # Return the constructed board
        return board

class SudokuGame(object):
    """
    A sudoku game, in charge of storing the state of the board nad checking wheter the pizzle is completed.
    """

    def __init__(self, board_file):
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in xrange(9):
            self.puzzle.append([])
            for j in xrange(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

    def check_win(self):
        for row in xrange(9):
            if not self.__check_row(row):
                return False
        for column in xrange(9):
            if not self.__check_column(column):
                return False
        for row in xrange(3):
            for column in xrange(3):
                if not self.__check_square(row, column):
                    return False

        self.game_over = True
        return True

    def __check_block(self, block):
        return set(block) == set(range(1, 10))

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])

    def __check_column(self, column):
        return self.__check_block(
            [self.puzzle[row][column] for row in xrange(9)]
        )

    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in xrange(row * 3, (row + 1) * 3)
                for c in xrange(column * 3, (column + 1) * 3)
            ]
        )

class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """

    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        Frame.__init__(self, parent)

        self.row, self.col = 0, 0

        self.__initUI()

    def __initUI(self):
        # set the parent title which is our main/only window
        self.parent.title("Sudoku")

        # Frame attribute that organizes the frames geometry relative to the parent, this is filling the entire frame, fill=BOTH mean fill both horizontally and vertically, other options include NONE, X or Y
        self.pack(fill=BOTH, expand=1)

        # canvas is a general pupose widget we use to display the board
        self.canvas = Canvas(self,
                                width=WIDTH,
                                height = HEIGHT)
        # setting pack, where the puzzle will fill the space and be pulled to the top part of the window.
        self.canvas.pack(fill=BOTH, side=TOP)

        # below the canvas, is the button to clear answers. We create button with Button, giving it text and the command for the button to call when it's pressed. here we set the command to __clear_answers.

        # Like canvas we will set pack for the butoon to fill the space and have the button sit at the bottom of the window
        clear_button = Button(self,
                                text="Clear answers",
                                command=self.__clear_answers)
        clear_button.pack(fill=BOTH, side=BOTTOM)

        # Two helper methods ...
        self.__draw_grid()
        self.__draw_puzzle()

        # Binding left mouse button click a callback, the bind method will pass the x y location of the cursor, whcih in __cell_clicked we will turn into actual cells of the puzzle.
        self.canvas.bind("<Button-1>", self.__cell_clicked)

        # Binding <Key> to the callback function __key_pressed. This binds the key a user pressed (e.g. the guessed number) to the __key_pressed method.
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in xrange(10):
            color = "blue" if i % 3 == 0 else "gray"
            # create the vertical lines
            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            # create the horizontal lines
            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in xrange(9):
            for j in xrange(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "sea green"
                    self.canvas.create_text(
                        x, y, text = answer, tags="numbers", fill=color
                    )

    def __clear_answers(self):
        # reset puzzle to original state
        self.game.start()
        # delete the previous victory status/tag
        self.canvas.delete("victory")
        # re-draw the puzzle with the original puzzlepyth
        self.__draw_puzzle()

    # callback for button-1
    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        x,y = event.x, event.y
        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

        # get row and col numbers from x,y coordinates
        row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE

        # if cell was selected already - deselect it
        if (row, col) == (self.row, self.col):
            self.row, self.col = -1, -1
        elif self.game.puzzle[row][col] == 0:
            self.row, self.col = row, col

        self.__draw_cursor()

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()
    
    def __draw_victory(self):
        # create an ovl (which will actually be a circle)
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange"
        )
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(
            x,y,
            text="You Win!", tags="winner",
            fill="white", font=("Arial", 32)
        )
            
if __name__ == '__main__':
    board_name = parse_arguments()

    with open('%s.sudoku' % board_name, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
        root.mainloop()
