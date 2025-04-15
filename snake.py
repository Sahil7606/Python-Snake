import os
import random
import curses 
from curses import wrapper
from datetime import datetime

DO_NOT_TOUCH = False  # Not liable for broken egos or tear induced water damage to pc
endgame_messages = [  # Displayed if above bool is set to True
    "That's why she left you with a paragraph and a blocked number.",
    "The wall wasn’t the problem. It was you, like always.",
    "Your snake isn't the only thing that's short and disappointing.",
    "Even your reflection avoids eye contact.",
]

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
    def __init__(self, row, col, speed = 100):
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
            self.speed = int(self.speed * 1.5)
        else:
            self.speed = int(self.speed / 1.5)

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
            stdscr: The curses screen object used for display
    """
    def __init__(self, height, width, stdscr):
        self.__height = height
        self.__width = width
        self.__walls = None
        self.__snake = None
        self.__currentApple = None
        self.stdscr = stdscr

    def __renderWalls(self) -> None:
        """
        Prints the walls to the screen
        """
        # Prints top boundary
        self.stdscr.addstr(0, 0, '+' + ('-' * (self.__width - 2)) + '+')
        
        # Prints bottom boundary
        self.stdscr.addstr(self.__height - 1, 0, '+' + ('-' * (self.__width - 2)) + '+')
        
        # Prints side boundaries
        for i in range(1, self.__height - 1):
            self.stdscr.addstr(i, 0, '|')
            self.stdscr.addstr(i, self.__width - 1, '|')

    def __renderSnake(self) -> None:
        """
        Prints the snake to the screen
        """
        # Draw snake
        current = self.__snake.tail
        while current and current.next:
            self.stdscr.addstr(current.position[0], current.position[1], 'O') 
            current = current.next
        self.stdscr.addstr(current.position[0], current.position[1], 'X')

    def __renderApple(self) -> None:

        """
        Prints the current apple to the screen
        """
        self.stdscr.addstr(self.__currentApple.position[0], self.__currentApple.position[1], '*')

    def __renderScore(self) -> None:
        """
        Renders the current score to the screen
        """
        score = f"Score: {self.__snake.length}"
        self.stdscr.addstr(self.__height, (self.__width - len(score)) // 2, score)

    def __renderStartScr(self) -> None:
        """
        Renders the start screen and displays a difficulty prompt
        """
        self.stdscr.clear()

        # Render walls
        self.__renderWalls()

        # Start screen content
        title = "-- Welcome to Snake --"
        subtitle = "Choose your difficulty:"
        options = "[1] Easy   [2] Medium   [3] Hard"
        note = "Press 1, 2, or 3 to begin, or ESC to exit"

        # Centered print
        self.stdscr.addstr(self.__height // 2 - 2, (self.__width - len(title)) // 2, title)
        self.stdscr.addstr(self.__height // 2,     (self.__width - len(subtitle)) // 2, subtitle)
        self.stdscr.addstr(self.__height // 2 + 1, (self.__width - len(options)) // 2, options)
        self.stdscr.addstr(self.__height // 2 + 3, (self.__width - len(note)) // 2, note)
        self.stdscr.refresh()

    def __renderHighScores(self) -> None:
        """
        Renders the high score list to the screen.
        """
        scores = self.__readHighScores()
        self.stdscr.addstr(2, (self.__width - len("-- High Scores --")) // 2, "-- High Scores --")
        
        for i, entry in enumerate(scores):
            line = f"{i + 1}) {entry['score']} - {entry['date']}"
            self.stdscr.addstr(4 + i, (self.__width - len(line)) // 2, line)

    def __renderEndScr(self) -> None:
        """
        Renders the game over screen
        """
        self.stdscr.clear()
        self.__renderWalls()
        self.__renderHighScores()

        heading = "Game Over"
        score = f"Your score was {self.__snake.length}"
        note = "Press Enter to play again, or ESC to exit"

        self.stdscr.addstr(self.__height // 2, (self.__width - len(heading)) // 2, heading)
        self.stdscr.addstr(self.__height // 2 + 1, (self.__width - len(score)) // 2, score)
        self.stdscr.addstr(self.__height // 2 + 3, (self.__width - len(note)) // 2, note)

        if DO_NOT_TOUCH:
            roast = random.choice(endgame_messages)
            self.stdscr.addstr(self.__height - 3, (self.__width - len(roast)) // 2, roast)

    def __renderGame(self) -> None:
        """
        Calls the previous rendering functions to render the game to the screen
        """
        self.__renderWalls()
        self.__renderSnake()
        self.__renderApple()
        self.__renderScore()

        self.stdscr.refresh()

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

    def __getInput(self) -> None:
        """
        Handles player input and switches the snake's direction accordingly
        """
        key = self.stdscr.getch()
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
    
    def __readHighScores(self) -> list:
        """
        Reads and returns the top 5 high scores from a local file.

        Returns:
            list: A list of dictionaries in the form {'score': int, 'date': str}.
        """
        path = ".snake_data/highscores.txt"
        # Returns empty list if path doesnt exit
        if not os.path.exists(path):
            return []

        # Formats scores from file as dictionaries
        scores = []
        with open(path, "r") as file:
            for line in file:
                try:
                    parts = line.strip().split(" - ")
                    score = int(parts[0].split(") ")[1])
                    date = parts[1]
                    scores.append({"score": score, "date": date})
                except:
                    continue  # Skips malformed lines

        # Returns list of score dictionaries
        return scores

    def __writeHighScores(self, new_score: int) -> None:
        """
        Writes a new score to the high score file if it qualifies for the top 5.

        Args:
            new_score (int): The player's final score.
        """
        path = ".snake_data"
        # Creates path if it doesn't exist
        os.makedirs(path, exist_ok=True)

        current_date = datetime.now().strftime("%Y-%m-%d")
        scores = self.__readHighScores()

        # Appends and re-sorts scores
        scores.append({"score": new_score, "date": current_date})
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:5]  # Keep only top 5

        # Writes updated list to file
        with open(f"{path}/highscores.txt", "w") as file:
            for idx, entry in enumerate(scores, start=1):
                file.write(f"{idx}) {entry['score']} - {entry['date']}\n")
    
    def startMenu(self) -> float:
        """
        Handles logic for the start menu of the game

        Returns:
            float: The speed of the snake based on the selected difficulty, or -1 to escape
        """
        self.__renderStartScr()
        difficulty_speeds = {ord('1'): 200, ord('2'): 100, ord('3'): 70}

        key = self.stdscr.getch()
        while key not in difficulty_speeds and key != 27:
            key = self.stdscr.getch()

        if key == 27:
            return -1

        return difficulty_speeds[key]   

    def endMenu(self) -> bool:
        """
        Controls logic for the 'Game Over' screen

        Returns:
            bool: True if the user wants to play again, False if not
        """
        self.__renderEndScr()

        key = self.stdscr.getch() 
        while key != 27 and key != 10:
            key = self.stdscr.getch()

        return key == 10

    def initializeGame(self, speed: int = 100) -> None:
        """
        Initializes the game window and instantiates necessary objects

        Args:
            speed (float): The speed of the snake based on the player's difficulty selection in the start menu
        """
        # Hides cursor and clears screen
        curses.curs_set(0)
        self.stdscr.clear()

        # Creates necessary objects
        self.__snake = Snake(self.__height // 2, 10, speed)
        self.__createApple((self.__height // 2), self.__width - 15)
        self.__initializeWalls()
        
        # Renders game to the screen
        self.__renderGame()

    def startGame(self) -> None:
        """
        Starts the game loop and runs until the game is over
        """
        # Stops getInput() from halting the program waiting for input
        self.stdscr.nodelay(True)
        self.stdscr.timeout(self.__snake.speed)

        # Core game loop
        while not self.__checkGameOver():
            # Clear the previous frame
            self.stdscr.clear()
            self.__renderGame()

            # Get user input
            self.__getInput()
            
            # Snake grows if it eats the current apple
            if self.__snake.head.position == self.__currentApple.position:
                self.__snake.grow()
                self.__createApple()
            
            # Moves the snake
            self.__snake.move()
            
            # Refreshes the screen
            self.stdscr.refresh()

        # Waits for input and then exits
        self.stdscr.nodelay(False)
        self.__writeHighScores(self.__snake.length)

def main(stdscr):
    game = Game(21, 50, stdscr)

    while True:
        speed = game.startMenu()
        if speed == -1:
            break

        game.initializeGame(speed)
        game.startGame()

        
        if not game.endMenu():
            break

wrapper(main)

