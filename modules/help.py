import __builtin__
import curses
from datetime import datetime
from time import sleep
import innotop

def run(session, delay=1, back=False):
    
    # Setup curses and info to use in top bar
    stdscr, info = innotop.common.setup(curses, session)
    
    # Run the query and generate the report
    keep_running = True
    while keep_running:
        time = datetime.now()

        y,x = innotop.common.topbar(curses, stdscr, info)

        stdscr.addstr(2, 0, "Help:", curses.A_BOLD)
 
        # Print the rows in the result
        line = 4
        stdscr.addstr(line, 2, "Press 'q':", curses.A_BOLD )
        stdscr.addstr(line, 15, "to exit")
        line = line + 1
        stdscr.addstr(line, 2, "Press 'h':", curses.A_BOLD )
        stdscr.addstr(line, 15, "for help")
        line = line + 1
        stdscr.addstr(line, 2, "Press 'd':", curses.A_BOLD )
        stdscr.addstr(line, 15, "to see details of a query and the query explain plan")
        line = line + 1
        stdscr.addstr(line, 2, "Press 'k':", curses.A_BOLD )
        stdscr.addstr(line, 15, "to kill a query")
 
        stdscr.refresh()
        stdscr.move(y-1,0)
 
        # Wait until delay seconds have passed while listening for the q key
        while (datetime.now() - time).total_seconds() < delay:
            c = stdscr.getch()
            if c == ord("q"):
                keep_running = False
                if back == True:
                    innotop.session_processlist.run(session)
                break
 
    # Reset the cures behaviour and finish
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
