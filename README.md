# Weblogic DMS Metric Collector

Weblogic DMS metric collector is a python utility that can be used to retrieve DMS metrics from Weblogic DMS Spy application. 
It reads a specified metric table data and converts them to CSV format. 

DMS is Weblogic Dynamic Monitoring Service providing a massive amount of sensors about Weblogic and application components performance.
It can be accessed in a number of ways, such as Weblogic Scripting Tool (wlst), Java API or DMS Spy application. DMS Spy is used to access DMS metric tables by using a browser while it also provides endpoints to retrieve metric tables in XML format. ```dms-collector``` uses 
the endpoints to retrieve the desired information. It was originally developed as a probe for [Universal Metric Collector](https://github.com/rstyczynski/umc) but can be used independently of UMC.

Run ```dms-collector --help``` to get more information on how to use it. 

```
usage: dms-collector --url <url> [--connect <u/p>] --count <num>
                     (--delay <seconds>|-<minutes> | --runonevents <num>)
                     (--table <tablename> | --dmsreset <path> | --recurse <value>)
                     [--nodelayadjust] [--secsinmin <secs>] [--alignminutes]
                     [--emitevents] [--maxtime <secs>] [--contacceptevents]
                     [--filter <python-expression>] [-ex <field1,field2,...>]
                     [-in <field1,field2,...>] [--noheader] [--origheader]
                     [--timeformat <format>] [--datetimefield <name>]
                     [--timezonefield <name>] [--nostrinquotes] [--fieldstags]
                     [--printheader] [-h] [-V] [--verbose] [--noversioncheck]
                     [--namedpipe <path>]

Weblogic DMS Spy table metric collector

optional arguments:
  --delay <seconds>|-<minutes>
                        delay between runs; positive value is seconds,
                        negative value is minutes
  --runonevents <num>   run when <num> events occur
  --table <tablename>   name of a valid DMS table which data to be retrieved
  --dmsreset <path>     reset dms aggregated data for <path>
  --recurse <value>     reset dms operation recurse parameter, default is
                        'all'

required arguments:
  --url <url>           Weblogic admin server url where DMS Spy is running
  --connect <u/p>       username/password to login to DMS Spy
  --count <num>         number of runs the data will be retrieved from DMS

optional arguments when --delay argument is used:
  --nodelayadjust       disables delay time adjustment
  --secsinmin <secs>    a second in a minute to run each iteration when delay
                        value is negative
  --alignminutes        when delay value is negative then align minutes to the
                        first minute of an hour; this argument is only applied
                        when delay minutes is 2 or greater
  --emitevents          emits an event after each run

optional arguments when --runonevents argument is used:
  --maxtime <secs>      maximum time in seconds between the first and the last
                        event before the iteration will be triggered, default
                        is 20; set this to 0 to wait indefinitely.
  --contacceptevents    accept events during the whole running timme; when not
                        set, events will not be accepted during DMS callouts

optional filtering arguments:
  --filter <python-expression>
                        a condition that has to hold true for a row to be
                        included in the output
  -ex <field1,field2,...>, --exclude <field1,field2,...>
                        list of header fiedls to be excluded from the output
  -in <field1,field2,...>, --include <field1,field2,...>
                        list of header fiedls to be included in the output
                        (all fields are included by default)

optional formatting arguments:
  --noheader            suppress header in the output
  --origheader          use original header in the output, no normalization
  --timeformat <format>
                        Python time format for datetime field (default is
                        '%y-%m-%d %H:%M:%S')
  --datetimefield <name>
                        datetime header field name (default is 'datetime')
  --timezonefield <name>
                        time zone header field name (default is 'timezone')
  --nostrinquotes       do not place string values in quotes
  --fieldstags          print only header's fields and tags and exit
  --printheader         print the table header and exit

optional other arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --verbose             output details to stderr
  --noversioncheck      do not check tbml version
  --namedpipe <path>    location of a named pipe used to read and write events
```
## Testing Server

In order to test ```dms-collector``` when you do not have an access to a running Weblogic server, you can use
a simple http server running in nodejs that simulates DMS Spy endpoints for sample metric tables. 
This server is available in ```test/local-server``` directory of this repository. The server requires [nodejs](https://nodejs.org/en/) to be available in your system. 

Run the following command in the ```test/local-server``` directory:

```
node http-server.js 
```

The server uses HTTP basic authentication (the same as DMS Spy app deployed on Weblogic version 10.3.6) with username ```weblogic``` and a password ```password1``` and is listening on ```tcp/7031``` by default. 

## Basic Usage

In order to retrieve all rows from a DMS metric table called ```JDBC_DataSources``` 10 times with a delay od 30 seconds between data retrievals, run the following command:

```
dms-collector --count 10 --delay 30 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource
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
dms-collector --count 10 --delay 30 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Process,Parent
```

If you want to only include rows that match a certain criteria, such as a server name, run the following command:

```
dms-collector --count 10 --delay 30 --adminurl http://localhost:7031 --connect weblogic/password1 --table JDBC_DataSource --exclude Parent,Process --filter "bool(re.match(r\"WLS_SOA[0-9]+\",str(ServerName)))"```
```
The ```--filter``` parameter accepts any valid python expression with variable names matching table's header names. You can use all header names regardless whether they are inluded or excluded from the output.   

## Timestamp and Timezone

```dms-collector``` adds two columns to the CSV output, namely datetime and timezone. This is the current local time when the data is retrieved from DMS and changes with every iteration. You can change the field names for both columns by using ```--datetimefield``` and ```--timezonefield``` respectively as well as remove them from the output by using ```--exclude``` option.    

## Delay Time

You can specify number of seconds ```dms-collector``` should wait between iterations by using ```--delay``` parameter. Since reading the data may in some situations take more time to finish, the delay time needs to be adjusted so that ```dms-collector``` always retrieves the data at the same time so that the overall running time can be determined. The time adjustment is however disabled when time to retrieve the DMS data takes more than 2/3 of the delay time. You can disable the delay time adjustment by using ```--nodelayadjust```.

```dms-collector``` will by default fetch data from DMS at the time you started the command. If you need your data to be retrieved always at the same time in a minute, you can further use a negative value for ```--delay``` parameter which indicates waiting time in minutes and another parameter ```--secsinmin``` which defines a second in a minute when ```dms-collector``` should fetch the data. By default, ```dms-collector``` fetches the data in the first second of a minute. If the delay value in minutes is greated than ```2``` you can further say that you want to fetch the data in "aligned" minutes in the hour. For example, if your delay is ```2``` minutes and you start ```dms-collector``` at ```9:31```, the data will be fetched at ```9:32```, ```9:34```, ```9:36```, etc. and not in ```9:31```, ```9:33```, ```9:35```, etc. With these options you can make sure that the data will always be fetched at the same times.       

## DMS Aggregated Data and DMS Reset

DMS provides a set of metrics for which it automatically calculates aggregated values. For example, DMS table ```oracle_soa_composite:soainfra_binding_rollup```, provides aggregated data for running time averages, error rates, etc. DMS always calculates the values since the last DMS reset. That said, if you need to collect such aggregated values on regular time intervals, you need to reset DMS at the beginning of each interval. This may however become more complicated when you want to collect aggregated data from multiple DMS tables while DMS reset applies to all tables. In such a case, you have to make sure that you first collect all metrics and only after all metrics are retrieved you can reset DMS. Such metrics should be obviously collected in the same time intervals. 

```dms-collector``` provides features which allow you to achieve the above requirement by ensuring that your metrics will always be collected at the same times of a minute and an hour, and a DMS reset will only be fired when all aggregated metrics that you collect will be retrieved. This can be achieved by two or more ```dms-collector``` instances sending and receiving events by using Linux named pipes. The below example illustrates such configuration.

Say, you have two DMS aggregated metrics you need to collect, ```metric1``` and ```metric2```. You need to collect these metrics every ```5``` minutes at the same time and only after both metrics are retrieved you need to reset DMS. 

You first run the two instnaces of ```dms-collector``` as follows.

```
dms-collector --count 10 --delay -5 --secsinmin 5 --alignminutes --adminurl url --connect u/p --table metric1 --emitevents
dms-collector --count 10 --delay -5 --secsinmin 5 --alignminutes --adminurl url --connect u/p --table metric2 --emitevents
```

Collection of data for ```metric1``` and ```metric2``` will happen in the 5th second of every 5th minute while the collection time will be aligned to the 5th minute of the hour. Both commands will further emit an event after DMS data is retrieved and you only need to reset DMS when both tables will be retrieved. You can use the below command to achieve this.

```
dms-collector --count 10 --runonevents 2 --dmsreset --adminurl url --connect u/p 
```

The above command will wait for two events and only after it receives them, it will call DMS reset operation. If for some reason only one event will be received, such as ```metric2``` will take more time to fetch, there is a default timeout of ```20``` seconds that indicates the maximum time to receive the last event since the first event was received. You can change this value by ```--maxtime``` parameter or disable this timeout by setting ```--maxtime``` to ```0```. Also, the above command will not accept any events while it is running DMS reset, which may take several seconds to finish. This may be important to achieve DMS reset is happening at the same time. If you want to change this, you can allow to accept events all the time by setting ```--contacceptevents``` parameter. Further, the named pipe that the ```dms-collector``` instances use to communicate events can be changed by ```--namedpipe``` parameter in case you need to change its location or want to separate sets of above configurations. 
 
## TODO

The current version of ```dms-collector``` will most likely not work on recent versions of Weblogic or SOA 11.1.1.7+. The DMS Spy
of such versions uses HTML form authentication instead of HTTP basic authentication. 

# License

free and free as a bird
