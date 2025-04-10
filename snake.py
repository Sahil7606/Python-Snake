import time
import curses 
from curses import wrapper

# Tomorrow: get the snake to move 
class Snake_Node:
    def __init__(self, position: tuple, next = None):
        self.position = position
        self.next = next

class Snake:
    """
    Attributes:
        head_position (tuple)
        length (int)
        speed (float)
        direction (str)
    """
    def __init__(self, row, col):
        self.head = Snake_Node((row, col))
        self.tail = self.head
        self.direction = (1, 0)
        self.length = 1

        self.__growPending = False

    def __enqueue_head(self, position: tuple):
        new_node = Snake_Node(position)
        self.head.next = new_node
        self.head = self.head.next

        self.length += 1

    def __dequeue_tail(self):
        removed_item = self.tail
        self.tail = self.tail.next
        removed_item = None

        self.length -= 1

    def setDirection(self, direction: tuple):
        self.direction = direction

    def grow(self):
        self.__growPending = True

    def move(self):
        next_pos = (self.head.position[0] + self.direction[0], self.head.position[1] + self.direction[1])
        self.__enqueue_head(next_pos)
        
        if not self.__growPending:
            self.__dequeue_tail()

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

    def __renderWalls(self, stdscr):
        # Top boundary
        stdscr.addstr(0, 0, '+' + ('-' * (self.width - 2)) + '+')
        
        # Bottom boundary
        stdscr.addstr(self.height - 1, 0, '+' + ('-' * (self.width - 2)) + '+')
        
        # Side boundaries
        for i in range(1, self.height - 1):
            stdscr.addstr(i, 0, '|')
            stdscr.addstr(i, self.width - 1, '|')
        
        stdscr.refresh()

    def __createWalls(self):
        self.walls = set()
        for i in range(self.height):
            if i == 0 or i == self.height - 1:
                for j in range(self.width):
                    self.walls.add((i, j))
            else:
                self.walls.add((i, 0))
                self.walls.add((i, self.width - 1))

    def initializeGame(self, stdscr):
        # Hides cursor and clears screen
        curses.curs_set(0)
        stdscr.clear()

        self.__renderWalls(stdscr)
        self.__createWalls()

        self.snake = Snake(self.height // 2, 5)

        stdscr.refresh()

    def startGame(self, stdscr):
        stdscr.nodelay(True)
        while True:
            # Clear the previous frame
            stdscr.clear()
            self.__renderWalls(stdscr)
            
            # Handle input
            key = stdscr.getch()
            if key == curses.KEY_DOWN:
                self.snake.setDirection((1, 0))  # DOWN increases row
            elif key == curses.KEY_UP:
                self.snake.setDirection((-1, 0))  # UP decreases row
            elif key == curses.KEY_LEFT:
                self.snake.setDirection((0, -1))
            elif key == curses.KEY_RIGHT:
                self.snake.setDirection((0, 1))

            # Move snake
            self.snake.move()
            
            # Draw snake
            current = self.snake.tail
            while current:
                stdscr.addstr(current.position[0], current.position[1], 'O') 
                current = current.next
            
            stdscr.refresh()
            time.sleep(0.1)  # Reduced sleep time for smoother movement


def main(stdscr):
    game = Game(21, 50)
    game.initializeGame(stdscr)

    # Gets user input to start game
    key = stdscr.getch()
    while key != 10 and key != 27:
        key = stdscr.getch()

    if key == 27:
        return
    
    game.startGame(stdscr)
    
wrapper(main)