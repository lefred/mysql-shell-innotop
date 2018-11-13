import __builtin__
import curses
from datetime import datetime
from time import sleep

def run(session, max_files=10, delay=1):
    # Define the output format
    fmt_header = "| {0:50s} | {1:12s} | {2:13s} | {3:13s} | {4:12s} " \
               + "| {5:13s} | {6:13s} | {7:13s} | {8:8s} |"
    header = fmt_header.format("File", "# Reads", "Bytes Read", "Avg. Read",
                               "# Writes", "Bytes Write", "Avg. Write",
                               "Bytes Total", "Write %")
    bar = "+" + "-" * 52 + "+" + "-" * 14 + "+" + "-" * 15 + "+" + "-" * 15 \
        + "+" + "-" * 14 + "+" + "-" * 15 + "+" + "-" * 15 + "+" + "-" * 15 \
        + "+" + "-" * 10 + "+"
    fmt_row = "| {0:50.50s} | {1:12d} | {2:13s} | {3:13s} | {4:12d} " \
            + "| {5:13s} | {6:13s} | {7:13s} | {8:8s} |"
    
    # Setup curses
    stdscr = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.noecho()
    curses.cbreak()
    # Listing for 1/10th of second at a time
    curses.halfdelay(1)
    stdscr.keypad(True)
 
    # Define the query
    sys_schema = session.get_schema("sys")
    table = sys_schema.get_table("io_global_by_file_by_bytes")
    query = table.select().limit(max_files)
    
    # Clear screen
    stdscr.clear()
    
    # Run the query and generate the report
    keep_running = True
    while keep_running:
        time = datetime.now()
        result = query.execute()
 
        stdscr.addstr(0, 0, time.strftime('%A %-d %B %H:%M:%S'), 
                      curses.color_pair(1))
        stdscr.addstr(2, 0, bar)
        stdscr.addstr(3, 0, header)
        stdscr.addstr(4, 0, bar)
 
        # Print the rows in the result
        line = 5
        for row in result.fetch_all():
            stdscr.addstr(line, 0, fmt_row.format(*row))
            line = line + 1
 
        stdscr.addstr(line, 0, bar)
        stdscr.refresh()
 
        # Wait until delay seconds have passed while listening for the q key
        while (datetime.now() - time).total_seconds() < delay:
            c = stdscr.getch()
            if c == ord("q"):
                keep_running = False
                break
 
    # Reset the cures behaviour and finish
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
