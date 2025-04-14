import time
import random
import curses 
from curses import wrapper

# Tomorrow: Improve documentation and add pre and endgame screen
class Snake_Node:
    """
    Basic linked list node implementation specialized for the body of the snake

    Attributes:
        position (tuple): the position of the body segment
        next (Snake_Node|None): a pointer to the next part of the snake
    """
    def __init__(self, position: tuple, next = None):
        self.position = position
        self.next = next

class Snake:
    """
    Controls the behavior of the snake using a queue-like structure based off of a singly linked list.

    This class manages movement, direction, and growth of the snake during gameplay.

    Attributes:
        Public:
            head (Snake_Node): The node at the front of the snake
            tail (Snake_Node): The node at the end of the snake
            direction (tuple): The direction of the snake in the form of (row_delta, col_delta)
                ex) (0, 1) -> Right, (-1, 0) -> Up
            length (int): The length of the snake            
            speed (float): The time to wait in between each frame; lower value = higher speed, vice versa
            nextPos (tuple|None): The next position of the head of the snake (if applicable)

        Private:
            growPending (bool): Tracks if the snake has eaten an apple, and subsequently needs to grow
    """
    def __init__(self, row, col, speed = 0.1):
        # Creates a new node at the specified position
        self.head = Snake_Node((row, col))
        self.tail = self.head

        # Starts direction going right
        self.direction = (0, 1)

        self.length = 1
        self.speed = speed
        self.nextPos = None

        self.__growPending = False

    def __contains__(self, position: tuple) -> bool:
        """
        Utilizes Python's "in" operator to see if a particular position is in the snake

        Args:
            position (tuple): the position to check for in the form (row, col)

        Returns:
            (bool): True if the specified position is in the snake, False if not
        """
        # Sets current to tail
        current = self.tail

        # Iterates through each node while checking if their positions are equal to the given position
        while current:
            if position == current.position:
                return True
            
            current = current.next

        return False
    
    def __enqueueHead(self, position: tuple) -> None:
        """
        Appends a new node to the front of the snake, then sets the head equal to the new front node

        Args:
            position (tuple): The position of the node to append
        """
        # Creates new head and appends to the front of the head
        new_node = Snake_Node(position)
        self.head.next = new_node

        # Sets the head to the new node (the front)
        self.head = self.head.next

        # Increments the length attribule of the snake
        self.length += 1

    def __dequeueTail(self) -> None:
        """
        Removes the tail node then sets the tail equal to the node in front of it
        """
        self.tail = self.tail.next

        # Decrements the length attribute
        self.length -= 1

    def setDirection(self, direction: tuple) -> None:
        """
        Sets the new direction of the snake

        Args:
            direction (tuple): the new direction of the snake
        """

        # Prevents the snake from moving 180 degrees in a single turn
        if (direction[0] == -self.direction[0] and direction[1] == -self.direction[1]):
            return
        
        # Stops vertical movement from appearing faster since characters are taller than they are wide
        if direction == (-1, 0) or direction == (1, 0):
            self.speed = 0.2
        else:
            self.speed = 0.1

        self.direction = direction

    def grow(self) -> None:
        """
        Called when the snake eats an apple, sets growPending to true
        """
        self.__growPending = True

    def move(self) -> None:
        """
        Moves the snake by adding a node to the front and removing one from the back
        """
        # Calculates the next head position based on direction
        self.nextPos = (self.head.position[0] + self.direction[0], self.head.position[1] + self.direction[1])

        # Appends a new head to the snake at the next position
        self.__enqueueHead(self.nextPos)
        
        # If the snake has eaten an apple then doesn't remove tail node, otherwise it is removed
        if self.__growPending:
            self.__growPending = False
        else:
            self.__dequeueTail()

class Apple: 
    """
    Attributes:
        postition (tuple): The position of the apple
    """
    def __init__(self, position: tuple):
        self.position = position
 
class Game:
    """
    Attributes:
        Private:
            height (int): The height(number of rows) of the board
            width (int): The width(number of columns) of the board
            walls (set[tuple]|None): A set containing the position of each wall in the form (row, col)
            snake (Snake|None): The snake object used for the game
            currentApple (Apple|None): The apple object that is currently on the board
    """
    def __init__(self, height, width):
        self.__height = height
        self.__width = width
        self.__walls = None
        self.__snake = None
        self.__currentApple = None

    def __renderWalls(self, stdscr) -> None:
        """
        Prints the walls to the screen

        Args:
            stdscr: The screen that the walls appear on
        """
        # Prints top boundary
        stdscr.addstr(0, 0, '+' + ('-' * (self.__width - 2)) + '+')
        
        # Prints bottom boundary
        stdscr.addstr(self.__height - 1, 0, '+' + ('-' * (self.__width - 2)) + '+')
        
        # Prints side boundaries
        for i in range(1, self.__height - 1):
            stdscr.addstr(i, 0, '|')
            stdscr.addstr(i, self.__width - 1, '|')

    def __renderSnake(self, stdscr) -> None:
        """
        Prints the snake to the screen

        Args:
            stdscr: The screen that the snake appears on
        """
        # Draw snake
        current = self.__snake.tail
        while current and current.next:
            stdscr.addstr(current.position[0], current.position[1], 'O') 
            current = current.next
        stdscr.addstr(current.position[0], current.position[1], 'X')

    def __renderApple(self, stdscr) -> None:
        """
        Prints the current apple to the screen

        Args:
            stdscr: The screen that the apple appears on
        """
        stdscr.addstr(self.__currentApple.position[0], self.__currentApple.position[1], '*')

    def __renderStartScr(self, stdscr) -> None:
        """
        Renders the start screen and displays a difficulty prompt

        Args:
            stdscr: The screen that the game is played on
        """
        # Render walls
        self.__renderWalls(stdscr)

        # Start screen content
        title = "🐍 Welcome to Snake 🐍"
        subtitle = "Choose your difficulty:"
        options = "[1] Easy   [2] Medium   [3] Hard"
        note = "Press 1, 2, or 3 to begin, or ESC to exit"

        # Centered print
        stdscr.addstr(self.__height // 2 - 2, (self.__width - len(title)) // 2, title)
        stdscr.addstr(self.__height // 2,     (self.__width - len(subtitle)) // 2, subtitle)
        stdscr.addstr(self.__height // 2 + 1, (self.__width - len(options)) // 2, options)
        stdscr.addstr(self.__height // 2 + 3, (self.__width - len(note)) // 2, note)
        stdscr.refresh()

    def __renderGame(self, stdscr) -> None:
        """
        Calls the previous rendering functions to render the game to the screen

        Args:
            stdscr: The screen that the game is played on
        """
        self.__renderWalls(stdscr)
        self.__renderSnake(stdscr)
        self.__renderApple(stdscr)

        stdscr.refresh()

    def __initializeWalls(self) -> None:
        """
        Uses the defined height and width attributes to add all wall coordinates to self.__walls
        """
        # Initializes the set
        self.__walls = set()

        for i in range(self.__height):
            # If i is at the top or bottom add the top and botton boundaries to the set
            if i == 0 or i == self.__height - 1:
                for j in range(self.__width):
                    self.__walls.add((i, j))
            # Adds the side boundaries to the set
            else:
                self.__walls.add((i, 0))
                self.__walls.add((i, self.__width - 1))
        
    def __createApple(self, row = None, col = None) -> None:
        """
        Creates a new apple object for the snake to eat

        Args:
            row (int|None): the row where the apple is going to be
            col (int|None): the column where the apple is going to be
        """
        position = ()
        # If the row and column are specified set those as the position
        if row and col:
            position = (row, col)
        # Generates a random position for the apple within the walls
        else:
            position = (random.randint(1, self.__height - 2), random.randint(1, self.__width - 2))
            # Makes sure the apple isnt placed in the snake
            while position in self.__snake:
                position = (random.randint(1, self.__height - 2), random.randint(1, self.__width - 2))

        # Initializes an Apple object at that position
        self.__currentApple = Apple(position)

    def __getInput(self, stdscr) -> None:
        """
        Handles player input and switches the snake's direction accordingly

        Args:
            stdscr: The screen to collect input from
        """
        key = stdscr.getch()
        if key == curses.KEY_DOWN:
            self.__snake.setDirection((1, 0))
        elif key == curses.KEY_UP:
            self.__snake.setDirection((-1, 0))
        elif key == curses.KEY_LEFT:
            self.__snake.setDirection((0, -1))
        elif key == curses.KEY_RIGHT:
            self.__snake.setDirection((0, 1))

    def __checkGameOver(self) -> bool:
        """
        Checks if the game is over by checking for collision

        Returns:
            bool: True if the snake has collided with itself or the wall, False if not
        """
        # Checks for collisions with snake
        current = self.__snake.tail
        while current and current.next:
            if current.position == self.__snake.head.position:
                return True
            current = current.next

        # Checks for collisions with wall
        return self.__snake.head.position in self.__walls
    
    def startMenu(self, stdscr) -> float:
        self.__renderStartScr(stdscr)
        difficulty_speeds = {ord('1'): 0.2, ord('2'): 0.1, ord('3'): 0.07}

        key = stdscr.getch()
        while key not in difficulty_speeds and key != 27:
            key = stdscr.getch()

        if key == 27:
            return -1

        return difficulty_speeds[key]        

    def initializeGame(self, stdscr, speed: float = 0.1) -> None:
        """
        Initializes the game window and instantiates necessary objects

        Args:
            stdscr: The screen that the game is played on
            speed (float): The speed of the snake based on the player's difficulty selection in the start menu
        """
        # Hides cursor and clears screen
        curses.curs_set(0)
        stdscr.clear()

        # Creates necessary objects
        self.__snake = Snake(self.__height // 2, 10, speed)
        self.__createApple((self.__height // 2), self.__width - 15)
        self.__initializeWalls()
        
        # Renders game to the screen
        self.__renderGame(stdscr)

    def startGame(self, stdscr) -> None:
        """
        Starts the game loop and runs until the game is over

        Args:
            stdscr: The screen that the game is played on
        """
        # Stops getInput() from halting the program waiting for input
        stdscr.nodelay(True)

        # Core game loop
        while not self.__checkGameOver():
            # Clear the previous frame
            stdscr.clear()
            self.__renderGame(stdscr)

            # Get user input
            self.__getInput(stdscr)
            
            # Snake grows if it eats the current apple
            if self.__snake.head.position == self.__currentApple.position:
                self.__snake.grow()
                self.__createApple()
            
            # Moves the snake
            self.__snake.move()
            
            # Refreshes the screen
            stdscr.refresh()

            # Slows time when player is about to collide for fairness
            if self.__snake.nextPos in self.__walls:
                time.sleep(self.__snake.speed * 2)
            else:
                time.sleep(self.__snake.speed)

        # Waits for input and then exits
        stdscr.nodelay(False)
        stdscr.getch()

def main(stdscr):
    game = Game(21, 50)
    snakeSpeed = game.startMenu(stdscr)

    if snakeSpeed == -1:
        return

    game.initializeGame(stdscr, snakeSpeed)
    game.startGame(stdscr)

wrapper(main)

  