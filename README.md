# $ dms-collector

DMS is a Weblogic Dynamic Monitoring Service providing a massive amount of sensors about Weblogic and application components performance.
It can be accessed in a number of ways, such as Weblogic Scripting Tool (wlst), Java API or DMS Spy application. DMS Spy is used to access DMS metric tables by using a browser while it also provides endpoints to retrieve metric tables in XML format.

dms-collector is a Python utility that retrieves DMS metrics from Weblogic DMS Spy application. It provides an API to access DMS tables' data and a CLI to query the DMS and display the data in CSV.

## Installation

You can install the dms-collector with pip as follows:

```
pip install dms-collector 
``` 

## Usage

You can use dms-collector CLI to query the DMS Spy running at `https://wls-domain` with username `weblogic` and password `password1` by running the following command: 

```
$ dms-collector --url https://wls-domain --connect weblogic/password1 --table JVM_Memory
datetime,timezone,Host,Parent,ServerName,pendingFinalization_value,verbose_value,Process,JVM,Name
"22-01-12 11:23:30",+0100,"domain-3.oraclevnc.com","/JVM/MxBeans","AdminServer",0,"TRUE","AdminServer:7101","JVM","memory"
"22-01-12 11:23:30",+0100,"fmw-poc-app10.oraclevcn.com","/JVM/MxBeans","soa_server2",0,"TRUE","soa_server2:8102","JVM","memory"
"22-01-12 11:23:30",+0100,"fmw-poc-app10.oraclevcn.com","/JVM/MxBeans","proc15010",0,"FALSE","machine2:15010","JVM","memory"
"22-01-12 11:23:30",+0100,"domain-3.oraclevcn.com","/JVM/MxBeans","proc69725",0,"FALSE","machine1:69725","JVM","memory"
```

## CLI Options

There are many options that you can use to control, for example, a number of calls the CLI will run, a delay between calls, fields to be included or excluded or rows to be filtered out in the result. 

For the full list of options please run `dms-collector --help`. 

### Filtering 

If you want to exclude certain fields from the output, such as `Process` and `Parent`, run the following command:

```
$ dms-collector --url https://wls-domain --connect weblogic/password1 --table JVM_Memory \
  --exclude Process,Parent
```

If you want to only return rows that match a certain criteria, such as a server name, run the following command:

```
$ dms-collector --url https://wls-domain --connect weblogic/password1 --table JVM_Memory \
  --filter "bool(re.match(r\"WLS_SOA[0-9]+\",str(ServerName)))"
```

The `--filter` parameter accepts any valid Python expression with variable names matching table's header names. You can use all header names regardless whether they are included or excluded from the output.   

### Timestamp and Timezone

The dms-collector CLI adds two columns to the CSV output, namely `datetime` and `timezone`. This is the current local time when the data is retrieved from the DMS and changes with every iteration. You can change the field names for both columns by using `--datetimefield` and `--timezonefield` respectively as well as remove them from the output by using `--exclude` option.    

### Delay Time

You can specify a number of seconds the dms-collector CLI should wait between iterations by using `--delay` parameter. Since reading the data may in some situations take more time to finish, the delay time needs to be adjusted so that dms-collector always retrieves the data at the same time and the overall running time can be determined. The time adjustment is however disabled when the time to retrieve the DMS data takes more than 2/3 of the delay time. You can disable the delay time adjustment by using `--nodelayadjust` or change the 2/3 limit by `--nodelayperc`.

### Login
 
dms-collector uses DMS Spy login form by default. If you are collecting data from a DMS Spy of an earlier version such as FMW infrastructure 11g, you need to use `--basicauth` option which uses HTTP basic authentication.
 
## Changes over previous version 1.1

The version 2.0+ introduces the following changes:

*  It is now possible to use `dms-collector` as a Python module which provides [DmsCollector class](https://github.com/tomvit/dms-collector/blob/v2.0/dms_collector/dms.py) that you can integrate into your Python applications. 

* Several command-line arguments were removed such as linux pipelines and emitting the events, DMS reset and time adjustments.  

You can still access the previous version in [1.1 branch](https://github.com/tomvit/dms-collector/tree/v1.1).
 
# License

free and free as a bird
