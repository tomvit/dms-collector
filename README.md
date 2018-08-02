# Weblogic DMS Metric Collector

Weblogic DMS metric collectior is a python utility that can be used to retrieve DMS metrics from Weblogic DMS Spy application. 
It reads a specificed metric table and converts its data to CSV format according to a number of options. 

DMS is Weblogic Dynamic Monitoring Service providing a massive amount of sensors about Weblogic and application components performance.
It can be accessed in a number of ways, one being by using Weblogic Scripting Tool (wlst). On top of DMS, Weblogic also provides DMS Spy application 
that can be used to access DMS metric tables by using a browser, as well as DMS Spy endpoints provide metric tables in XML format. DMS collector uses 
these endpoints to retrieve the desired information. 

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

In order to test ```dms-collector``` and in cases when you do not have a running Weblogic server, you can use
a simple http server running in nodejs that simulates DMS Spy endpoints for sample metric tables. 
This server is available in the test directory of this repository. 

# License

free and free as a bird