import curses 
from curses import wrapper

class Snake:
    """
    Attributes:
        head_position (tuple)
        length (int)
    """
    pass

class Apple: 
    """
    Attributes:
        postition (tuple)
    """
    pass
 
class Game:
    """
    Attributes:
        height (int)
        width (int)
        board_matrix (lst[lst])
    """
    pass

def main(stdscr):
    stdscr.clear()
    stdscr.addstr(10, 20, "hello snake")
    
    # stdscr.refresh()
    stdscr.getch()

wrapper(main)