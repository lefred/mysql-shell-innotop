MySQL Shell Innotop
===================

This is a Innotop like Python module for MySQL Shell.

How to use it:
--------------

```
 mysqlsh --py root@localhost

 import sys
 sys.path.append('/home/fred/workspace/mysql-shell-innotop')
 import innotop

 innotop.session_processlist.run(session)
``` 
