The program - 'pMerck.py' - runs on Python version 2.7.8 (Mac)

BD Flow-cytometers keep track of how often they are in use. Every month they create a
'.csv' file containing all the sessions that were used on a given cytometer.

I wrote this python program to be used in analyzing the user-login information contained
in those '.csv' files. My initial idea was to create a small table calculator that 
subtracted time in two different columns, but the project grew to cover a lot more. I added
more functions as the needs grew

The script is well commented. All arguments needed are file paths. Quotation marks are not
necessary when input names of files and file paths at the menu.

As is, it should run by direct execution. It displays a menu and one can analyze time 
usage based on user name, department, etc. Selecting an option on the main menu brings 
another menu. 

Outputs are in three formats; xml, csv and doc 

- 'csvFiles' contains samples of monthly login sessions put out by BD Flow Cytometers.
The names are made up and all sensitive information is altered.
- 'MBMX_flow sessions.csv' is a sample output when one selects to print a group's time.
- 'user1_flow sessions.csv' is a sample output when one selects to print a user's session.
- 'user8_flow sessions_2005-05-05__2015-07-12.csv' is a sample output when one selects to 
print user's sessions within a specified time range
- 'output_testCSV.csv' is a sample output when one selects to print the entire xml database
as a csv file
- 'LSRII_flow sessions_2005-05-05__2914-07-15.csv' is a sample output when one selects 
sessions on a given machine within a given time
- 'LSRII_flow sessions.csv' is a sample output when one selects to print all the time used
on a given machine