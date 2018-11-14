import __builtin__
import curses
from datetime import datetime
from time import sleep
import innotop

def run(session, thd_id, delay=1, back=False):
    
    # Setup curses and info to use in top bar
    stdscr, info = innotop.common.setup(curses, session)
    
    # Run the query and generate the report
    keep_running = True
    while keep_running:
        time = datetime.now()
        query = session.sql("select * from sys.processlist p1 join performance_schema.threads pps on pps.thread_id = p1.thd_id where thd_id=%s" % thd_id);
        result = query.execute()
        if not result.has_data():
            keep_running = False
            break

        y,x = innotop.common.topbar(curses, stdscr, info)

        stdscr.addstr(2, 0, "Query Details:", curses.A_BOLD)
 
        # Print the rows in the result
        line = 4
        query_text = None
        for row in result.fetch_all():
            stdscr.addstr(line, 0, "Query:", curses.A_BOLD )
            query_text = str(row[38])
            stdscr.addstr(line, 8, query_text)
            line = line + 2
            stdscr.addstr(line, 0, "Thread ID:", curses.A_BOLD )
            stdscr.addstr(line, 11, str(row[0]))
            stdscr.addstr(line, 20, "Conn ID:", curses.A_BOLD )
            stdscr.addstr(line, 29, str(row[1]))
            stdscr.addstr(line, 47, "PID:", curses.A_BOLD )
            stdscr.addstr(line, 52, str(row[26]))
            stdscr.addstr(line, 63, "User:", curses.A_BOLD )
            stdscr.addstr(line, 69, str(row[2]))
            stdscr.addstr(line, 90, "DB:", curses.A_BOLD )
            stdscr.addstr(line, 94, str(row[3]))
            line = line + 1
            stdscr.addstr(line, 2, "Command:", curses.A_BOLD )
            stdscr.addstr(line, 11, str(row[4]))
            stdscr.addstr(line, 42, "Progress:", curses.A_BOLD )
            stdscr.addstr(line, 52, str(row[9]))
            stdscr.addstr(line, 60, "AutoCom:", curses.A_BOLD )
            stdscr.addstr(line, 69, str(row[25]))
            stdscr.addstr(line, 85, "TxState:", curses.A_BOLD )
            stdscr.addstr(line, 94, str(row[24]))
            line = line + 1
            stdscr.addstr(line, 1, "LockTime:", curses.A_BOLD )
            stdscr.addstr(line, 11, str(row[10]))
            stdscr.addstr(line, 22, "LastStTime:", curses.A_BOLD )
            stdscr.addstr(line, 34, str(row[18]))
            stdscr.addstr(line, 43, "TrxTime:", curses.A_BOLD )
            stdscr.addstr(line, 52, str(row[23]))
            stdscr.addstr(line, 64, "Mem:", curses.A_BOLD )
            stdscr.addstr(line, 69, str(row[19]))
            stdscr.addstr(line, 83, "Conn Type:", curses.A_BOLD )
            stdscr.addstr(line, 94, str(row[43]))
            line = line + 1
            stdscr.addstr(line, 4, "State:", curses.A_BOLD )
            stdscr.addstr(line, 11, str(row[5]))
            line = line + 1
            stdscr.addstr(line, 5, "ROWS:", curses.A_BOLD )
            line = line + 1
            stdscr.addstr(line, 11, "Examined:", curses.A_BOLD )
            stdscr.addstr(line, 21, str(row[11]))
            stdscr.addstr(line, 32, "Sent:", curses.A_BOLD )
            stdscr.addstr(line, 38, str(row[12]))
            stdscr.addstr(line, 49, "Affected:", curses.A_BOLD )
            stdscr.addstr(line, 59, str(row[13]))
            stdscr.addstr(line, 74, "ResourceGroup:", curses.A_BOLD )
            stdscr.addstr(line, 89, str(row[45]))
            line = line + 1
            stdscr.addstr(line, 5, "Tables:", curses.A_BOLD )
            line = line + 1
            stdscr.addstr(line, 15, "Temp:", curses.A_BOLD )
            stdscr.addstr(line, 21, str(row[14]))
            stdscr.addstr(line, 32, "TempDisk:", curses.A_BOLD )
            stdscr.addstr(line, 42, str(row[15]))
            stdscr.addstr(line, 49, "FullScan:", curses.A_BOLD )
            stdscr.addstr(line, 59, str(row[16]))
            
        line = line + 2
        if query_text:
            query = session.sql("EXPLAIN %s" % query_text);
            result = query.execute()
            if not result.has_data():
                keep_running = False
                break
        stdscr.addstr(line, 5, "EXPLAIN:", curses.A_BOLD )
        line = line + 1
        fmt_row = " {0:4} {1:6} {2:6} {3:10} {4:6} {5:10} {6:8} {7:6} {8:6} {9:9} {10:5} {11:30}"
        header = fmt_row.format("  id", "select", "table", "partitions", "type", "poss keys", "key", "k len", "ref", "     rows", "filt ", "extra")
        stdscr.addstr(line, 0, header, curses.A_BOLD)


        for row in result.fetch_all():
            line = line + 1
            stdscr.addstr(line, 0, fmt_row.format(*row))
 
        stdscr.refresh()
        stdscr.move(y-1,0)
 
        # Wait until delay seconds have passed while listening for the q key
        while (datetime.now() - time).total_seconds() < delay:
            c = stdscr.getch()
            if c == ord("q"):
                keep_running = False
                break
            if c == ord("h"):
                    innotop.help.run(session, back=True)
    
    if not back:
        # Reset the cures behaviour and finish
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin
