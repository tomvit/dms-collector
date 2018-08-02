# Weblogic DMS Metric Collector

Weblogic DMS metric collector is a python utility that can be used to retrieve DMS metrics from Weblogic DMS Spy application. 
It reads a specified metric table and converts its data to CSV format according to a number of options. 

DMS is Weblogic Dynamic Monitoring Service providing a massive amount of sensors about Weblogic and application components performance.
It can be accessed in a number of ways, one being Weblogic Scripting Tool (wlst) and a DMS Spy application. DMS Spy is used to access DMS metric tables with a browser while DMS Spy endpoints also provide metric tables in XML format. ```dms-collector``` uses 
the endpoints to retrieve the desired information. 

Run ```dms-collector --help``` to get more information on how to use it. 

```
usage: dms-collector [-h] --count <num> --delay <seconds> --adminurl <url>
                     [--connect <u/p>] --table <tablename>
                     [--filter <python-expression>]
                     [--exclude <field1,field2,...>]
                     [--include <field1,field2,...>] [--printheader]
                     [--noheader] [--origheader] [--fieldstags]

Weblogic DMS Spy table metric collector

optional arguments:
  -h, --help            show this help message and exit
  --count <num>         Number of runs the data will be retrieved from DMS
  --delay <seconds>     Delay in seconds between runs
  --adminurl <url>      Weblogic Admin server url where DMS Spy app us running
  --connect <u/p>       username/password to login to DMS Spy
  --table <tablename>   Name of a valid DMS table which data to be retrieved
  --filter <python-expression>
                        A condition that has to hold true for a row to be
                        included in the output.
  --exclude <field1,field2,...>
                        List of header fiedls to be excluded from the output
  --include <field1,field2,...>
                        List of header fiedls to be included in the output.
                        All fields are included by default.
  --printheader         Print the table header and exit
  --noheader            Suppress header in the output
  --origheader          Use original header in the output, no normalization
  --fieldstags          Print only header's fields and tags and exit
```

In order to test ```dms-collector``` when you do not have an access to a running Weblogic server, you can use
a simple http server running in nodejs that simulates DMS Spy endpoints for sample metric tables. 
This server is available in the test directory of this repository. The server requires nodejs is available in your system. 

In order to run the testing server, run the following command in the test directory:

```
node http-server.js 
```

The server uses HTTP basic authentication (the same as DMS Spy app deployed on Weblogic version 10.3.6) with username ```weblogic``` and a password ```password1``` and is listening on tcp/7031 by default. You can use this server to run the below tests.

In order to retrieve all rows from a DMS metric table called ```JDBC_DataSources```, run the following command:

```
dms-collector --count 1 --delay 1 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource
```
 
In order to exclude fields ```Process``` and ```Process``` from the output, run the following command:

```
dms-collector --count 1 --delay 1 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Process,Parent
```

In order to include rows that match a certain server name, run the following command:

```
dms-collector --count 1 --delay 1 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Parent,Process --filter "bool(re.match(r\"WLS_SOA[0-9]+\",str(ServerName)))"```
```

# License

free and free as a bird