# Weblogic DMS Metric Collector

Weblogic DMS metric collector is a python utility that can be used to retrieve DMS metrics from Weblogic DMS Spy application. 
It reads a specified metric table data and converts them to CSV format. 

DMS is Weblogic Dynamic Monitoring Service providing a massive amount of sensors about Weblogic and application components performance.
It can be accessed in a number of ways, such as Weblogic Scripting Tool (wlst), Java API or DMS Spy application. DMS Spy is used to access DMS metric tables by using a browser while it also provides endpoints to retrieve metric tables in XML format. ```dms-collector``` uses the endpoints to retrieve the desired information.

Run ```dms-collector --help``` to get more information on how to use it. 

```
usage: dms-collector --url <url> [--connect <u/p>] --count <num> [--delay <seconds>] [--table <tablename>] [--nodelayadjust] [--nodelayperc <perc>]
                   [--filter <python-expression>] [-ex <field1,field2,...>] [-in <field1,field2,...>] [--csvdelimiter <char>] [--noheader]
                   [--origheader] [--timeformat <format>] [--datetimefield <name>] [--timezonefield <name>] [--nostrinquotes] [-h] [-V]
                   [--noversioncheck] [--readtimeout <secs>] [--basicauth]

Weblogic DMS Spy table metric collector

required arguments:
  --url <url>           Weblogic admin server url where DMS Spy is running
  --connect <u/p>       username/password to login to DMS Spy
  --count <num>         number of runs the data will be retrieved from DMS
  --delay <seconds>     delay between runs
  --table <tablename>   name of a valid DMS table which data to be retrieved

optional delay adjustments arguments:
  --nodelayadjust       disables delay time adjustment
  --nodelayperc <perc>  when response time is more than this percantage of elapsed time then the delay will be disabled

optional filtering arguments:
  --filter <python-expression>
                        a condition that has to hold true for a row to be included in the output
  -ex <field1,field2,...>, --exclude <field1,field2,...>
                        list of header fiedls to be excluded from the output
  -in <field1,field2,...>, --include <field1,field2,...>
                        list of header fiedls to be included in the output (all fields are included by default)

optional formatting arguments:
  --csvdelimiter <char>
                        CSV delimiter
  --noheader            suppress header in the output
  --origheader          use original header in the output, no normalization
  --timeformat <format>
                        Python time format for datetime field (default is '%y-%m-%d %H:%M:%S')
  --datetimefield <name>
                        datetime header field name (default is 'datetime')
  --timezonefield <name>
                        time zone header field name (default is 'timezone')
  --nostrinquotes       do not place string values in quotes

optional other arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --noversioncheck      do not check tbml version
  --readtimeout <secs>  htto read timeout, default is 30 seconds
  --basicauth           use basic authentication instead of form login. This is required for earlier versions of DMS SPy.
```

## Basic Usage

In order to retrieve all rows from a DMS metric table called ```JDBC_DataSources``` 10 times with a delay of 30 seconds between data retrievals, run the following command:

```
dms-collector --count 10 --delay 30 --url http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource
```
This will provide the following output:

```
datetime,timezone,Host,ServerName,ConnectionCreate_maxTime,ConnectionCreate_completed,ConnectionCreate_time,Process,ConnectionCreate_active,ConnectionCreate_maxActive,Name,ConnectionCreate_minTime,ConnectionOpenCount_count,ConnectionCreate_avg,ConnectionCloseCount_count,Parent
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,1019,3256,155858,WLS_SOA2:8061,0,4,SOADataSource-rac1,25,3256,47.86793611793612,3233,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,1038,3173,151602,WLS_SOA2:8061,0,5,SOADataSource-rac0,26,3173,47.77875827292783,3150,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,42,5,183,WLS_SOA2:8061,0,1,PortalEventSyncAQ1DS,33,5,36.6,0,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,450,280,12010,WLS_SOA2:8061,0,3,XrefDataSource-rac1,28,280,42.892857142857146,256,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,530,271,12211,WLS_SOA2:8061,0,3,XrefDataSource-rac0,27,271,45.05904059040591,243,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,58,5,244,WLS_SOA2:8061,0,1,OraclePIMDataSourceDS,40,5,48.8,0,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,30,1,30,WLS_SOA2:8061,0,1,EDNDataSource-rac1,30,1,30.0,1,/JDBC
18-08-02 20:01:03,+0200,server2.local,WLS_SOA2,32,1,32,WLS_SOA2:8061,0,1,EDNDataSource-rac0,32,1,32.0,1,/JDBC
```
 
If you want to further exclude certain fields from the output, such as ```Process``` and ```Parent```, run the following command:

```
dms-collector --count 10 --delay 30 --url http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Process,Parent
```

If you want to only include rows that match a certain criteria, such as a server name, run the following command:

```
dms-collector --count 10 --delay 30 --url http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Parent,Process --filter "bool(re.match(r\"WLS_SOA[0-9]+\",str(ServerName)))"```
```
The `--filter` parameter accepts any valid python expression with variable names matching table's header names. You can use all header names regardless whether they are inluded or excluded from the output.   

## Timestamp and Timezone

`dms-collector` adds two columns to the CSV output, namely datetime and timezone. This is the current local time when the data is retrieved from DMS and changes with every iteration. You can change the field names for both columns by using `--datetimefield` and `--timezonefield` respectively as well as remove them from the output by using `--exclude` option.    

## Delay Time

You can specify number of seconds `dms-collector` should wait between iterations by using `--delay` parameter. Since reading the data may in some situations take more time to finish, the delay time needs to be adjusted so that `dms-collector` always retrieves the data at the same time so that the overall running time can be determined. The time adjustment is however disabled when time to retrieve the DMS data takes more than 2/3 of the delay time. You can disable the delay time adjustment by using `--nodelayadjust`.

## Login
 
`dms-collector` uses DMS Spy form login by default. If you are collecting data from a DMS Spy of an earlier version such as FMW infrastructure 11g, you need to use `--basicauth` option which uses HTTP basic authentication.
 
## Changes over previous version 1.1

The version 2.0+ introduces the following changes:

*  It is now possible to use `dms-collector` as a Python module which provides [DmsCollector class](https://github.com/tomvit/dms-collector/blob/v2.0/dms_collector/dms.py) that you can integrate into your Python applications. 

* Several command-line arguments were removed such as linux pipelines and emitting the events, DMS reset and time adjustments.  

You can still access the previous version in [1.1 branch](https://github.com/tomvit/dms-collector/tree/v1.1).
 
# License

free and free as a bird
