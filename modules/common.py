import __builtin__
import curses
from datetime import datetime
from time import sleep
import innotop


def topbar(curses, stdscr, info):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(10, 166, curses.COLOR_WHITE)
    curses.init_pair(11, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(12, 23, curses.COLOR_WHITE)

    time = datetime.now()
    y,x = stdscr.getmaxyx()
    stdscr.addstr(0, 0, " " * x, curses.color_pair(10) )
    stdscr.addstr(0, 0, "My", curses.color_pair(12) )
    stdscr.addstr(0, 2, "SQL ", curses.color_pair(10) )
    stdscr.addstr(0, 6, "Shell | ", curses.color_pair(12) )
    stdscr.addstr(0, 14, info['comment'], curses.color_pair(10) )
    stdscr.addstr(0, 14+len(info['comment'])+1, info['version'], curses.color_pair(10) )
    length=len(time.strftime('%A %-d %B %H:%M:%S'))
    stdscr.addstr(0, (x-length)-1, time.strftime('%A %-d %B %H:%M:%S'),
                    curses.color_pair(11))
    return y,x

def setup(curses, session):
    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(10, 166, curses.COLOR_WHITE)
    curses.init_pair(11, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(12, 23, curses.COLOR_WHITE)

    curses.noecho()
    curses.cbreak()
    # Listing for 1/10th of second at a time
    curses.halfdelay(1)
    stdscr.keypad(True)
    stdscr.clear()
    session.set_current_schema('sys')
    query = session.sql("select @@version, @@version_comment, @@hostname, @@port")
    result = query.execute()
    info = {}
    for row in result.fetch_all():
        info['version'] = row[0]
        info['comment'] = row[1]
        info['hostname'] = row[2]
        info['port'] = row[3]
    return stdscr, info
