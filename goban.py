"""
TODOs :
    -> Make a nice interactive loop
    -> Link with Discord API
    -> Add SGF export
"""


from enum import IntEnum

class Stone(IntEnum):
    """
    Enum representing a state of one intersection
    """
    NONE = 0
    BLACK = 1
    WHITE = 2
    KO_1 = 3  # Ko not to be removed at the end of the turn (fresh one we just created)
    KO_0 = 4  # 'old' ko, to be removed at the end of the turn

def get_opponent(col):
    """
    Utility function to get the opponent
    :param col: Current player
    :return: Stone.BLACK if the current player is Stone.WHITE, and vice versa
    """
    if(col == Stone.BLACK):
        return Stone.WHITE
    if (col == Stone.WHITE):
        return Stone.BLACK
    return Stone.NONE


class Goban:
    """
    Basic go board. Support custom size and komis
    """
    def __init__(self, size, komi=7.5):
        """
        Creates the board
        :param size: The size of the go board
        :param komi: The custom value of the komi
        """
        self.board = [[Stone.NONE for i in range(size)] for j in range(size)]
        self.size = size
        self.komi = komi
        self.black_captures = 0
        self.white_captures = 0

    def play(self, pos, stone):
        """
        Plays a stone onto the go board
        Also clears up the board afterwards
        :return: True if the move was allowed and played, if th emove is illegal, returns False and does not play it
        """
        x, y = pos
        if (x < 0 or y < 0 or x >= self.size or y >= self.size):
            print("Invalid move, out of goban's bounds")
            return False

        if (self.board[x][y] == Stone.NONE):
            self.board[x][y] = stone
        else:
            return False
        self.clean_no_liberties(pos, col=get_opponent(stone))
        if (self.get_liberties(pos) == 0):
            self.board[x][y] = Stone.NONE
            return False
        else:
            self.remove_kos()  # Each time a stone is placed we remove kos. They have 2 'lives' for that reason
            return True

    def get_liberties(self, pos, seen_pos=None, color=None):
        """
        Counts the number of liberties of the group placed at position pos
        :return: int the number of liberties of the group
        """
        if (seen_pos == None):
            seen_pos = []
        x, y = pos
        curr_count = 0
        if (color == None):
            color = self.board[x][y]
        if (x < 0 or x >= self.size):
            return 0
        if (y < 0 or y >= self.size):
            return 0
        if (self.board[x][y] == Stone.NONE):
            return 1
        if (self.board[x][y] == Stone.KO_0):
            return 1
        if (self.board[x][y] == Stone.KO_1):
            return 1
        if (self.board[x][y] != color):
            return 0
        if (self.board[x][y] == color):
            seen_pos += [pos]
            if ([x-1, y] not in seen_pos):
                up = self.get_liberties([x-1, y], seen_pos, color)
                seen_pos += [[x-1, y]]
                curr_count += up
            if ([x+1, y] not in seen_pos):
                down = self.get_liberties([x+1, y], seen_pos, color)
                seen_pos += [[x+1, y]]
                curr_count += down
            if ([x, y-1] not in seen_pos):
                left = self.get_liberties([x, y-1], seen_pos, color)
                seen_pos += [[x, y-1]]
                curr_count += left
            if ([x, y+1] not in seen_pos):
                right = self.get_liberties([x, y+1], seen_pos, color)
                seen_pos += [[x, y+1]]
                curr_count += right
            return curr_count

    def clean_no_liberties(self, pos, col):
        """
        Checks if we need to capture the stones of color col after playing in position pos
        :param col: The color of the stones to remove
        :return: None but removes the stones that need to be removed
        """
        x, y = pos
        if (x - 1 >= 0):
            if (self.get_liberties([x-1, y]) == 0 and self.board[x-1][y] != Stone.NONE):
                self.capture([x-1, y], color=col)
        if (x + 1 < self.size):
            if (self.get_liberties([x+1, y]) == 0 and self.board[x+1][y] != Stone.NONE):
                self.capture([x+1, y], color=col)
        if (y - 1 >= 0):
            if (self.get_liberties([x, y-1]) == 0 and self.board[x][y-1] != Stone.NONE):
                self.capture([x, y-1], color=col)
        if (y + 1 < self.size):
            if (self.get_liberties([x, y+1]) == 0 and self.board[x][y+1] != Stone.NONE):
                self.capture([x, y+1], color=col)


    def add_capture(self, col):
        if (col == Stone.WHITE):
            self.black_captures += 1
        else:
            self.white_captures += 1

    def capture(self, pos, color, already_removed=False):
        """
        Captures the group of color col at the given position
        """
        x, y = pos
        if (x < 0 or x >= self.size):
            return
        if (y < 0 or y >= self.size):
            return
        if (self.board[x][y] == color):
            if (already_removed):
                self.remove_kos()
                self.board[x][y] = Stone.NONE
                self.add_capture(color)
            else:
                self.board[x][y] = Stone.KO_1
                self.add_capture(color)
                already_removed = True
            self.capture([x-1, y], color, already_removed)
            self.capture([x+1, y], color, already_removed)
            self.capture([x, y-1], color, already_removed)
            self.capture([x, y+1], color, already_removed)
        return

    def remove_kos(self):
        """
        Sanitizes the board by removing KO flags when not valid any more
        """
        for i in range(self.size):
            for j in range(self.size):
                if (self.board[i][j] == Stone.KO_0):
                    self.board[i][j] = Stone.NONE
                if (self.board[i][j] == Stone.KO_1):
                    self.board[i][j] = Stone.KO_0
        return

    def display(self):
        """
        Generates and display an image of the goban
        """
        from image_generator import Generator
        Generator(self).display()

    def save_as_json(self):
        from json import dump
        file = open("test.json", 'w')
        dump({'board' : self.board, 'komi' : self.komi, 'black_captures' : self.black_captures, 'white_captures' : self.white_captures}, file)

    def load_from_json(self, file):
        from json import load
        file = open("test.json", 'r')
        d = load(file)
        self.board = d['board']
        self.size = len(self.board)
        self.komi = d['komi']
        self.black_captures = d['white_captures']
        self.white_captures = d['white_captures']

if __name__ == "__main__":
    g = Goban(5)
    g.play([2,2], Stone.BLACK)
    g.save_as_json()
    g.display()
    f = Goban(3)
    f.play([0,0], Stone.WHITE)
    f.load_from_json("test.json")
    f.display()

if __name__ == "__main__":
    """
    Game loop. Will need to be cleared up later
    """
    player = 0  # reprensents black
    g = Goban(9)
    g.display()
    while(True):
        x = int(input())
        y = int(input())
        if (player == 0):
            while(not g.play([x, y], Stone.BLACK)):
                print("Illegal move, please try again")
                x = int(input())
                y = int(input())
        else:
            while(not g.play([x, y], Stone.WHITE)):
                print("Illegal move, please try again")
                x = int(input())
                y = int(input())
        g.display()
        player = 1 - player
