import time
import curses 
from curses import wrapper

# Tomorrow: get the snake to move

class Snake:
    """
    Attributes:
        head_position (tuple)
        length (int)
        speed (float)
        body (set)
    """
    def __init__(self, row, col):
        self.head_position = (row, col)
        self.length = 2
        self.speed = 0.2
        self.body = set((row, col - 1)) # Creates body part behind head

    def setDirection(self, direction):
        pass

    def grow(self, amount = 1):
        pass

class Apple: 
    """
    Attributes:
        postition (tuple)
    """
    def __init__(self, x, y):
        self.position = (x, y)
 
class Game:
    """
    Attributes:
        height (int)
        width (int)
        walls (set|None)
        snake (Snake|None)
    """
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.walls = None
        self.snake = None

    def renderWalls(self, stdscr):  # Do I really need this?
        # Top boundary
        stdscr.addstr(0, 0, '+' + ('-' * (self.width - 2)) + '+')
        
        # Bottom boundary
        stdscr.addstr(self.height - 1, 0, '+' + ('-' * (self.width - 2)) + '+')
        
        # Side boundaries
        for i in range(1, self.height - 1):
            stdscr.addstr(i, 0, '|')
            stdscr.addstr(i, self.width - 1, '|')
        
        stdscr.refresh()

    def createWalls(self):
        self.walls = set()
        for i in range(self.height):
            if i == 0 or i == self.height - 1:
                for j in range(self.width):
                    self.walls.add((i, j))
            else:
                self.walls.add((i, 0))
                self.walls.add((i, self.width - 1))

    def initializeGame(self, stdscr):
        self.renderWalls(stdscr)
        self.createWalls()

        self.snake = Snake(self.height // 2, 5)
        stdscr.addstr(self.snake.head_position[0], self.snake.head_position[1], 'X')
        stdscr.addstr(self.snake.head_position[0], self.snake.head_position[1] - 1, 'O')

    def startGame(self):
        pass

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    game = Game(21, 50)  # Wider board (20 columns) for safety
    game.initializeGame(stdscr)
    stdscr.refresh()
    stdscr.getch()  # Wait for keypress

wrapper(main)