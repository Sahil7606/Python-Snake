import time
import random
import curses 
from curses import wrapper

# Tomorrow: Improve documentation and add pre and endgame screen
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
        self.direction = (0, 1)
        self.length = 1
        self.speed = 0.1
        self.next_pos = None

        self.__growPending = False

    def __contains__(self, position):
        current = self.tail
        while current:
            if position == current.position:
                return True
            current = current.next
        return False
    
    def __enqueueHead(self, position: tuple):
        new_node = Snake_Node(position)
        self.head.next = new_node
        self.head = self.head.next

        self.length += 1

    def __dequeueTail(self):
        removed_item = self.tail
        self.tail = self.tail.next
        removed_item = None

        self.length -= 1

    def setDirection(self, direction: tuple):
        self.direction = direction
        # Stops vertical movement from appearing faster
        if direction == (-1, 0) or direction == (1, 0):
            self.speed = 0.2
        else:
            self.speed = 0.1

    def grow(self):
        self.__growPending = True

    def move(self):
        self.next_pos = (self.head.position[0] + self.direction[0], self.head.position[1] + self.direction[1])
        self.__enqueueHead(self.next_pos)
        
        if self.__growPending:
            self.__growPending = False
        else:
            self.__dequeueTail()

class Apple: 
    """
    Attributes:
        postition (tuple)
    """
    def __init__(self, position: tuple):
        self.position = position
 
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
        self.__walls = None
        self.__snake = None
        self.__currentApple = None

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

    def __renderSnake(self, stdscr):
        # Draw snake
        current = self.snake.tail
        while current and current.next:
            stdscr.addstr(current.position[0], current.position[1], 'O') 
            current = current.next
        stdscr.addstr(current.position[0], current.position[1], 'X')

    def __renderApple(self, stdscr):
        stdscr.addstr(self.__currentApple.position[0], self.__currentApple.position[1], '*')

    def __renderGame(self, stdscr):
        self.__renderWalls(stdscr)
        self.__renderSnake(stdscr)
        self.__renderApple(stdscr)

    def __initializeWalls(self):
        self.walls = set()
        for i in range(self.height):
            if i == 0 or i == self.height - 1:
                for j in range(self.width):
                    self.walls.add((i, j))
            else:
                self.walls.add((i, 0))
                self.walls.add((i, self.width - 1))
        
    def __createApple(self, row = None, col = None):
        self.__currentApple = None
        position = None
        if row and col:
            position = (row, col)
        else:
            position = (random.randint(1, self.height - 2), random.randint(1, self.width - 2))
            while position in self.snake:
                position = (random.randint(1, self.height - 2), random.randint(1, self.width - 2))

        self.__currentApple = Apple(position)

    def __getInput(self, stdscr):
        # Handle input
        key = stdscr.getch()
        if key == curses.KEY_DOWN:
            self.snake.setDirection((1, 0))
        elif key == curses.KEY_UP:
            self.snake.setDirection((-1, 0))
        elif key == curses.KEY_LEFT:
            self.snake.setDirection((0, -1))
        elif key == curses.KEY_RIGHT:
            self.snake.setDirection((0, 1))

    def __checkGameOver(self):
        # Checks for collisions with body
        current = self.snake.tail
        while current and current.next:
            if current.position == self.snake.head.position:
                return True
            current = current.next

        return self.snake.head.position in self.walls
        
    def initializeGame(self, stdscr):
        # Hides cursor and clears screen
        curses.curs_set(0)
        stdscr.clear()

        self.snake = Snake(self.height // 2, 5)
        self.__createApple((self.height // 2), self.width - 7)
        self.__initializeWalls()
        
        self.__renderGame(stdscr)

        stdscr.refresh()

    def startGame(self, stdscr):
        stdscr.nodelay(True)
        while not self.__checkGameOver():
            # Clear the previous frame
            stdscr.clear()
            self.__renderGame(stdscr)
            
            self.__getInput(stdscr)

            if self.snake.head.position == self.__currentApple.position:
                self.snake.grow()
                self.__createApple()
            
            # Move snake
            self.snake.move()
            
            stdscr.refresh()
            if self.snake.next_pos in self.walls:
                time.sleep(self.snake.speed * 2)
            else:
                time.sleep(self.snake.speed)

        stdscr.nodelay(False)
        stdscr.getch()

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