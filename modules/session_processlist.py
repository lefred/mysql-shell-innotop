import __builtin__
import curses
from datetime import datetime
from time import sleep
import innotop

def run(session, max_files=10, delay=1):
    # Define the output format
    fmt_header = "{0:7s} {1:5s} {2:5s} {3:5s} {4:15s} {5:20s} {6:12s}" \
            + " {7:10s} {8:10s} {9:65s}"
    header = fmt_header.format("Cmd", "  Thd", " Conn", "  Pid", "State", "User", "Db",
                                "Time", "Lock Time", "Query")
    fmt_row = "{0:7s} {1:5} {2:5} {3:5} {4:15s} {5:20s}" \
            + " {6:12s} {8:10s} {9:10s} {7:65s}"
    main_loop = True

     # Setup curses and info to use in top bar
    stdscr, info = innotop.common.setup(curses, session)

    while main_loop:
        curses.noecho()
        curses.cbreak()
        # Listing for 1/10th of second at a time
        curses.halfdelay(1)
        stdscr.keypad(True)
        # Clear screen
        stdscr.clear()
        # Define the query
        sys_schema = session.get_schema("sys")
        table = sys_schema.get_table("session")
        #query = table.select("thd_id","conn_id","pid","user","db",
        #        "current_statement","statement_latency","lock_latency",
        #        "trx_latency","rows_examined"
        #        ).order_by("statement_latency desc").limit(max_files)
        session.set_current_schema('sys')
        query = session.sql("select `pps`.`PROCESSLIST_COMMAND` AS `command`, `pps`.`THREAD_ID` AS `thd_id`,`pps`.`PROCESSLIST_ID` AS `conn_id`, `conattr_pid`.`ATTR_VALUE` AS `pid`, `pps`.`PROCESSLIST_STATE` AS `state`, if((`pps`.`NAME` in ('thread/sql/one_connection','thread/thread_pool/tp_one_connection')),concat(`pps`.`PROCESSLIST_USER`,'@',`pps`.`PROCESSLIST_HOST`),replace(`pps`.`NAME`,'thread/','')) AS `user`,`pps`.`PROCESSLIST_DB` AS `db`,`sys`.`format_statement`(`pps`.`PROCESSLIST_INFO`) AS `current_statement`,if(isnull(`esc`.`END_EVENT_ID`),`sys`.`format_time`(`esc`.`TIMER_WAIT`),NULL) AS `statement_latency`, `sys`.`format_time`(`esc`.`LOCK_TIME`) AS `lock_latency`, if(isnull(`esc`.`END_EVENT_ID`),`esc`.`TIMER_WAIT`,0) AS `sort_time`  from (((((((`performance_schema`.`threads` `pps` left join `performance_schema`.`events_waits_current` `ewc` on((`pps`.`THREAD_ID` = `ewc`.`THREAD_ID`))) left join `performance_schema`.`events_stages_current` `estc` on((`pps`.`THREAD_ID` = `estc`.`THREAD_ID`))) left join `performance_schema`.`events_statements_current` `esc` on((`pps`.`THREAD_ID` = `esc`.`THREAD_ID`))) left join `performance_schema`.`events_transactions_current` `etc` on((`pps`.`THREAD_ID` = `etc`.`THREAD_ID`))) left join `x$memory_by_thread_by_current_bytes` `mem` on((`pps`.`THREAD_ID` = `mem`.`thread_id`))) left join `performance_schema`.`session_connect_attrs` `conattr_pid` on(((`conattr_pid`.`PROCESSLIST_ID` = `pps`.`PROCESSLIST_ID`) and (`conattr_pid`.`ATTR_NAME` = '_pid')))) left join `performance_schema`.`session_connect_attrs` `conattr_progname` on(((`conattr_progname`.`PROCESSLIST_ID` = `pps`.`PROCESSLIST_ID`) and (`conattr_progname`.`ATTR_NAME` = 'program_name')))) where `pps`.`PROCESSLIST_ID` is not null and `pps`.`PROCESSLIST_COMMAND` <> 'Daemon' and user <> 'sql/event_scheduler' order by sort_time desc limit %d" % max_files)
        
        
        # Run the query and generate the report
        keep_running = True
        main_loop = True
        while keep_running:
            time = datetime.now()
            result = query.execute()
            
            y,x = innotop.common.topbar(curses, stdscr, info)
            
            stdscr.addstr(2, 0, header, curses.A_BOLD)
     
            # Print the rows in the result
            line = 3
            for row in result.fetch_all():
                if long(row[10]) > 60000000000000:
                    # > 60 sec goes red
                    stdscr.addstr(line, 0, fmt_row.format(*row),curses.color_pair(4))
                elif long(row[10]) > 30000000000000:
                    # > 30 sec goes green
                    stdscr.addstr(line, 0, fmt_row.format(*row),curses.color_pair(3))
                elif long(row[10]) > 10000000000000:
                    # > 10 sec goes cyan
                    stdscr.addstr(line, 0, fmt_row.format(*row),curses.color_pair(2))
                else:
                    stdscr.addstr(line, 0, fmt_row.format(*row))
                line = line + 1
     
            stdscr.refresh()
            stdscr.move(y-1,0)
     
            # Wait until delay seconds have passed while listening for the q key
            while (datetime.now() - time).total_seconds() < delay:
                c = stdscr.getch()
                if c == ord("q"):
                    keep_running = False
                    main_loop = False
                    break
                if c == ord("h"):
                    innotop.help.run(session, back=True)
                    
                if c == ord("k"):
                    stdscr.addstr(y-1, 0, "Enter a thd_id to kill: ")
                    curses.echo()
                    thd = stdscr.getstr()
                    curses.noecho()
                    q=session.sql("select conn_id from sys.processlist where thd_id=%s" % thd)
                    res=q.execute()
                    conn_id = res.fetch_one()[0]
                    q=session.sql("kill query %s" % conn_id)
                    res=q.execute()
                    keep_running = False
                    break

                if c == ord("d"):
                    stdscr.addstr(y-1, 0, "Enter a thd_id: ")
                    keep_running = False
                    main_loop = False
                    curses.echo()
                    thd = stdscr.getstr()
                    curses.noecho()
                    innotop.thread_info.run(session, thd, back=True)
     
    # Reset the cures behaviour and finish
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
