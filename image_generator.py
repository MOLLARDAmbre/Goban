from PIL import Image, ImageDraw
from goban import Goban, Stone
from scorer import Scorer, Intersection
from numpy import sqrt

class Generator:
    """
    Class which will be tasked to generate the image representing a goban
    """
    def __init__(self, goban):
        """
        Initialisation
        :param goban: Goban the goban we want to display
        :return: None
        """
        self.bg_color = (193, 154, 107)
        self.size = goban.size  # Size of the goban
        self.goban = goban  # Where we will fetch the stones from
        self.MULT_FACT = 75  # Scales the image up
        self.img = self.create_image()
        self.writer = ImageDraw.Draw(self.img)

    def create_image(self):
        """
        Creates a blank image and initialises its color
        """
        w, h = self.size * self.MULT_FACT, self.size * self.MULT_FACT
        img = Image.new("RGB", (w, h))
        img.paste(self.bg_color, [0, 0, w, h])
        return img

    def make_goban(self):
        """
        Makes the lines and the labels for the image
        """
        for i in range(self.size):
            self.writer.line([(self.MULT_FACT / 2, self.MULT_FACT / 2 + self.MULT_FACT * i), (self.size * self.MULT_FACT - self.MULT_FACT / 2, self.MULT_FACT / 2 + self.MULT_FACT * i)], fill="black", width=1)  # Horizontal line
            self.writer.text((self.MULT_FACT / 4, self.MULT_FACT / 2 + self.MULT_FACT * i - 5), str(i), fill="black")  # Labels for horizontal lines
            self.writer.line([(self.MULT_FACT / 2 + self.MULT_FACT * i, self.MULT_FACT / 2), (self.MULT_FACT / 2 + self.MULT_FACT * i, self.size * self.MULT_FACT - self.MULT_FACT / 2)], fill="black", width=1)  # Vertical lines
            self.writer.text((self.MULT_FACT / 2 + self.MULT_FACT * i - 5, self.MULT_FACT / 4), str(i), fill="black")  # Labels for vertical lines

    def draw_one_stone(self, col, i, j):
        """
        Draws a single stone onto the image
        :param col: The color of the stone
        :param i: The ord value
        :param j: The abs value
        """
        self.writer.ellipse((self.MULT_FACT * (j + 0.5 - sqrt(2)/3),
                             self.MULT_FACT * (i + 0.5 - sqrt(2)/3),
                             self.MULT_FACT * (j + 0.5 + sqrt(2)/3),
                             self.MULT_FACT * (i + 0.5 + sqrt(2)/3)),
                             fill=col)
    def draw_stones(self):
        """
        Draw all the stones from the goban
        """
        for i in range(self.size):
            for j in range(self.size):
                if (i == 5 and j == 5):
                    # import pdb; pdb.set_trace()
                    pass
                if (self.goban.board[i][j] == Stone.BLACK):
                    self.draw_one_stone("black", i, j)
                if (self.goban.board[i][j] == Stone.WHITE):
                    self.draw_one_stone("white", i, j)


    def display(self):
        """
        Refreshes the image and displays it
        """
        self.img = self.create_image()
        self.writer = ImageDraw.Draw(self.img)
        self.make_goban()
        self.draw_stones()
        self.img.save("temp.png")


class ScoreGenerator(Generator):
    def __init__(self, scorer):
        super().__init__(scorer)

    def draw_territory(self, col, i, j):
        self.writer.rectangle((self.MULT_FACT * (j + 0.5 - sqrt(2)/8),
                             self.MULT_FACT * (i + 0.5 - sqrt(2)/8),
                             self.MULT_FACT * (j + 0.5 + sqrt(2)/8),
                             self.MULT_FACT * (i + 0.5 + sqrt(2)/8)),
                             fill=col)

    def draw_stones(self):
        """
        Draw all the stones and territory from the goban
        """
        for i in range(self.size):
            for j in range(self.size):
                if (i == 5 and j == 5):
                    # import pdb; pdb.set_trace()
                    pass
                if (self.goban.board[i][j] == Intersection.BLACK_STONE):
                    self.draw_one_stone("black", i, j)
                if (self.goban.board[i][j] == Intersection.WHITE_STONE):
                    self.draw_one_stone("white", i, j)
                if (self.goban.board[i][j] == Intersection.WHITE_DEAD_STONE):
                    col = (int(self.bg_color[0] * 0.55 + 115), int(self.bg_color[1] * 0.55 + 115), int(self.bg_color[1] * 0.55 + 115))
                    self.draw_one_stone(col, i, j)
                    self.draw_territory("black", i, j)
                if (self.goban.board[i][j] == Intersection.BLACK_DEAD_STONE):
                    col = (int(self.bg_color[0] * 0.55), int(self.bg_color[1] * 0.55), int(self.bg_color[1] * 0.55))
                    self.draw_one_stone(col, i, j)
                    self.draw_territory("white", i, j)
                if (self.goban.board[i][j] == Intersection.WHITE_TERRITORY):
                    self.draw_territory("white", i, j)
                if (self.goban.board[i][j] == Intersection.BLACK_TERRITORY):
                    self.draw_territory("black", i, j)
