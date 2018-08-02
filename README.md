# Weblogic DMS Metric Collector

Weblogic DMS metric collector is a python utility that can be used to retrieve DMS metrics from Weblogic DMS Spy application. 
It reads a specified metric table and converts its data to CSV format according to a number of options. 

DMS is Weblogic Dynamic Monitoring Service providing a massive amount of sensors about Weblogic and application components performance.
It can be accessed in a number of ways, one being Weblogic Scripting Tool (wlst) and a DMS Spy application. DMS Spy is used to access DMS metric tables with a browser while DMS Spy endpoints also provide metric tables in XML format. ```dms-collector``` uses 
the endpoints to retrieve the desired information. It was originally developed as a probe for [Universal Metric Collector](https://github.com/rstyczynski/umc) but can be used independently on UMC.

Run ```dms-collector --help``` to get more information on how to use it. 

```
usage: dms-collector [-h] --count <num> --delay <seconds> --adminurl <url>
                     [--connect <u/p>] --table <tablename>
                     [--filter <python-expression>]
                     [--exclude <field1,field2,...>]
                     [--include <field1,field2,...>] [--printheader]
                     [--noheader] [--origheader] [--fieldstags]
                     [--timeformat <format>] [--datetimefield <name>]
                     [--timezonefield <name>]

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
  --timeformat <format>
                        Python time format for datetime field (default is
                        '%y-%m-%d %H:%M:%S')
  --datetimefield <name>
                        datetime header field name (default is 'datetime')
  --timezonefield <name>
                        time zone header field name (default is 'timezone')
```

In order to test ```dms-collector``` when you do not have an access to a running Weblogic server, you can use
a simple http server running in nodejs that simulates DMS Spy endpoints for sample metric tables. 
This server is available in the test directory of this repository. The server requires [nodejs](https://nodejs.org/en/) to be available in your system. 

In order to run the testing server, run the following command in the ```test/local-server``` directory:

```
node http-server.js 
```

The server uses HTTP basic authentication (the same as DMS Spy app deployed on Weblogic version 10.3.6) with username ```weblogic``` and a password ```password1``` and is listening on tcp/7031 by default. You can use this server to run the below tests.

In order to retrieve all rows from a DMS metric table called ```JDBC_DataSources```, run the following command:

```
dms-collector --count 1 --delay 1 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource
```
This will provide the following output:

```
atetime,timezone,Host,ServerName,ConnectionCreate_maxTime,ConnectionCreate_completed,ConnectionCreate_time,Process,ConnectionCreate_active,ConnectionCreate_maxActive,Name,ConnectionCreate_minTime,ConnectionOpenCount_count,ConnectionCreate_avg,ConnectionCloseCount_count,Parent
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,1019,3256,155858,WLS_SOA2:8061,0,4,SOADataSource-rac1,25,3256,47.86793611793612,3233,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,1038,3173,151602,WLS_SOA2:8061,0,5,SOADataSource-rac0,26,3173,47.77875827292783,3150,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,42,5,183,WLS_SOA2:8061,0,1,PortalEventSyncAQ1DS,33,5,36.6,0,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,450,280,12010,WLS_SOA2:8061,0,3,XrefDataSource-rac1,28,280,42.892857142857146,256,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,530,271,12211,WLS_SOA2:8061,0,3,XrefDataSource-rac0,27,271,45.05904059040591,243,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,58,5,244,WLS_SOA2:8061,0,1,OraclePIMDataSourceDS,40,5,48.8,0,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,30,1,30,WLS_SOA2:8061,0,1,EDNDataSource-rac1,30,1,30.0,1,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,32,1,32,WLS_SOA2:8061,0,1,EDNDataSource-rac0,32,1,32.0,1,/JDBC
```
 
In order to exclude fields ```Process``` and ```Parent``` from the output, run the following command:

```
dms-collector --count 1 --delay 1 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Process,Parent
```

In order to include rows that match a certain server name, run the following command:

```
dms-collector --count 1 --delay 1 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Parent,Process --filter "bool(re.match(r\"WLS_SOA[0-9]+\",str(ServerName)))"```
```

# License

free and free as a bird