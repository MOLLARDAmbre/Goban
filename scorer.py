from enum import IntEnum

class Intersection(IntEnum):
    NONE = 0
    WHITE_STONE = 1
    WHITE_TERRITORY = 2
    BLACK_DEAD_STONE = 3
    BLACK_STONE = 4
    BLACK_TERRITORY = 5
    WHITE_DEAD_STONE = 6
    DAME = 7

def get_dead_version(stone):
    if (stone == Intersection.WHITE_STONE):
        return Intersection.WHITE_DEAD_STONE
    if (stone == Intersection.WHITE_DEAD_STONE):
        return Intersection.WHITE_STONE
    if (stone == Intersection.BLACK_STONE):
        return Intersection.BLACK_DEAD_STONE
    if (stone == Intersection.BLACK_DEAD_STONE):
        return Intersection.BLACK_STONE
    return Intersection.NONE

def is_a_stone(intersection):
    return intersection in [Intersection.WHITE_STONE, Intersection.WHITE_DEAD_STONE, Intersection.BLACK_STONE, Intersection.BLACK_DEAD_STONE]


class Scorer:
    def __init__(self, goban):
        from goban import Goban, Stone
        self.board = [[Intersection.NONE for i in range(goban.size)] for j in range(goban.size)]
        self.size = goban.size
        self.komi = goban.komi
        self.black_captures = goban.black_captures
        self.white_captures = goban.white_captures
        for i in range(goban.size):
            for j in range(goban.size):
                if (goban.board[i][j] == Stone.WHITE):
                    self.board[i][j] = Intersection.WHITE_STONE
                if (goban.board[i][j] == Stone.BLACK):
                    self.board[i][j] = Intersection.BLACK_STONE

    def kill(self, pos, col=None):
        x, y = pos
        if (x < 0 or x >= self.size or y < 0 or y >= self.size):
            return

        if (col == None):
            col = self.board[x][y]

        if (self.board[x][y] == col):
            self.board[x][y] = get_dead_version(self.board[x][y])
            self.kill([x+1, y], col)
            self.kill([x-1, y], col)
            self.kill([x, y-1], col)
            self.kill([x, y+1], col)

        return

    def prepare_scores(self, pos, col = None):
        x, y = pos
        if (x < 0 or x >= self.size or y < 0 or y >= self.size):
            return

        if (self.board[x][y] == Intersection.DAME):
            return
        if (is_a_stone(self.board[x][y]) and col != None):
            return
        if (self.board[x][y] == col):
            return

        if (col == None):
            if (self.board[x][y] == Intersection.WHITE_STONE or self.board[x][y] == Intersection.BLACK_DEAD_STONE):
                col = Intersection.WHITE_TERRITORY
            if (self.board[x][y] == Intersection.BLACK_STONE or self.board[x][y] == Intersection.WHITE_DEAD_STONE):
                col = Intersection.BLACK_TERRITORY

        if (self.board[x][y] == Intersection.NONE):
            self.board[x][y] = col

        if (col == Intersection.DAME or (self.board[x][y] == Intersection.WHITE_TERRITORY and col == Intersection.BLACK_TERRITORY) or (self.board[x][y] == Intersection.BLACK_TERRITORY and col == Intersection.WHITE_TERRITORY)):
            col = Intersection.DAME
            self.board[x][y] = col

        self.prepare_scores([x+1, y], col)
        self.prepare_scores([x-1, y], col)
        self.prepare_scores([x, y+1], col)
        self.prepare_scores([x, y-1], col)

        return

    def prepare_all_scores(self):
        for i in range(self.size):
            for j in range(self.size):
                if (is_a_stone(self.board[i][j])):
                    self.prepare_scores([i, j])

    def reset_scores(self):
        for i in range(self.size):
            for j in range(self.size):
                if (not is_a_stone(self.board[i][j])):
                    self.board[i][j] = Intersection.NONE


    def count_territory(self):
        self.prepare_all_scores()
        black = self.black_captures
        white = self.komi + self.white_captures
        for i in range(self.size):
            for j in range(self.size):
                if (self.board[i][j] == Intersection.WHITE_TERRITORY):
                    white += 1
                if (self.board[i][j] == Intersection.BLACK_TERRITORY):
                    black += 1
                if (self.board[i][j] == Intersection.WHITE_DEAD_STONE):
                    black += 2
                if (self.board[i][j] == Intersection.BLACK_DEAD_STONE):
                    white += 2
        if (black > white):
            return "Black wins by {}".format(black - white)
        return "White wins by {}".format(white - black)

    def display(self):
        from image_generator import ScoreGenerator
        ScoreGenerator(self).display()



def test():
    from goban import Goban, Stone
    g = Goban(5)
    g.play([0,0], Stone.WHITE)
    g.play([2,0], Stone.BLACK)
    g.play([3,0], Stone.WHITE)
    g.play([0,1], Stone.BLACK)
    g.play([1,1], Stone.BLACK)
    g.play([2,1], Stone.BLACK)
    g.play([3,1], Stone.WHITE)
    g.play([4,1], Stone.WHITE)
    g.play([0,2], Stone.WHITE)
    g.play([2,2], Stone.BLACK)
    g.play([3,2], Stone.WHITE)
    g.play([0,3], Stone.BLACK)
    g.play([1,3], Stone.BLACK)
    g.play([3,3], Stone.WHITE)
    g.play([1,4], Stone.BLACK)
    g.play([3,4], Stone.WHITE)
    g.play([4,4], Stone.BLACK)
    g.play([1,2], Stone.BLACK)
    g.play([1,0], Stone.BLACK)
    g.play([4,3], Stone.WHITE)
    scorer = Scorer(g)
    scorer.kill([0,0])
    scorer.kill([4,4])
    print(scorer.count_territory())
    scorer.display()
    import pdb; pdb.set_trace()

if __name__ == "__main__":
    test()
