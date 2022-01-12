
import argparse
import re
import time
import sys

from dms_collector import DmsCollector, TBML_VERSIONS

from dms_collector import __version__

from .dms import is_number


def checkPattern(str, pattern, errormsg):
    p = re.compile(pattern)
    if not p.match(str):
        raise Exception(errormsg)


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            "%s is an invalid positive int value" % value)
    return ivalue


def check_perc(value):
    ivalue = float(value)
    if ivalue > 1 or ivalue < 0:
        raise argparse.ArgumentTypeError("%s must be between 0 and 1" % value)
    return ivalue


# arguments
parser = argparse.ArgumentParser(
    description='Weblogic DMS Spy table metric collector', add_help=False, prog='dms-collector')

required = parser.add_argument_group('required arguments')
required.add_argument('--url', required=True,
                      help='Weblogic admin server url where DMS Spy is running', metavar='<url>')
required.add_argument('--connect', required=True,
                      help='username/password to login to DMS Spy', metavar='<u/p>')
required.add_argument('-t','--table', help='name of a valid DMS table which data to be retrieved', required=True,
                      default=None, metavar='<tablename>')

group1 = parser.add_argument_group('optional count and delay arguments')
group1.add_argument('-c','--count', required=False, default=1,
                      help='number of runs the data will be retrieved from DMS', metavar='<num>', type=check_positive)
group1.add_argument('-d','--delay', help='delay between runs',
                      default=60, type=int, metavar='<seconds>')
group1.add_argument('--nodelayadjust', required=False,
                    help='disables delay time adjustment', default=False, action='store_true')
group1.add_argument('--nodelayperc', metavar='<perc>', default=0.7, type=check_perc, required=False,
                    help='when response time is more than this percantage of elapsed time then the delay will be disabled')

fiopts = parser.add_argument_group('optional filtering arguments')
fiopts.add_argument('--filter', required=False, help='a condition that has to hold true for a row to be included in the output',
                    default='', metavar='<python-expression>')
fiopts.add_argument("-ex", '--exclude', required=False,
                    help='list of header fiedls to be excluded from the output', default='', metavar='<field1,field2,...>')
fiopts.add_argument("-in", '--include', required=False,
                    help='list of header fiedls to be included in the output (all fields are included by default)', default='', metavar='<field1,field2,...>')

foopts = parser.add_argument_group('optional formatting arguments')
foopts.add_argument('--csvdelimiter', required=False,
                    default=",", metavar='<char>', help='CSV delimiter')
foopts.add_argument('--noheader', required=False,
                    help='suppress header in the output', default=False, action='store_true')
foopts.add_argument('--origheader', required=False,
                    help='use original header in the output, no normalization', default=False, action='store_true')
foopts.add_argument('--timeformat', required=False, help='Python time format for datetime field (default is \'%%y-%%m-%%d %%H:%%M:%%S\')',
                    default="%y-%m-%d %H:%M:%S", metavar='<format>')
foopts.add_argument('--datetimefield', required=False,
                    help='datetime header field name (default is \'datetime\')', default="datetime", metavar='<name>')
foopts.add_argument('--timezonefield', required=False,
                    help='time zone header field name (default is \'timezone\')', default="timezone", metavar='<name>')
foopts.add_argument('--nostrinquotes', required=False,
                    help='do not place string values in quotes', default=False, action='store_true')

otopts = parser.add_argument_group('optional other arguments')
otopts.add_argument("-h", "--help", action="help",
                    help="show this help message and exit")
otopts.add_argument("-V", '--version', action='version', version='%(prog)s ' +
                    __version__ + ', supports DMS tbml versions: ' + ','.join(TBML_VERSIONS))
otopts.add_argument('--noversioncheck', required=False,
                    help='do not check tbml version', default=False, action='store_true')
otopts.add_argument('--basicauth', required=False, default=False, action='store_true',
                    help='use basic authentication instead of form login. This is required for earlier versions of DMS SPy.')

try:
    args = parser.parse_args()

    def strinquotes(val):
        if args.nostrinquotes or is_number(val):
            return val
        else:
            return "\"%s\"" % val

    checkPattern(args.url, r"^(https?:)//([A-Za-z0-9\-\.\_]+)(:[0-9]+)?/?$",
                 "The admin url address '%s' is invalid! It should be in a form http(s)://hostname[:port]" % args.url)
    checkPattern(args.connect, r"^[a-zA-Z0-9]+/.+$",
                 "The connect argument is invalid. It should be in a form username/password")

    username, password = args.connect.split("/")
    dms = DmsCollector(args.url, username=username, password=password,
                       basic_auth=args.basicauth)

    args.datetimefield = args.datetimefield.strip()
    args.timezonefield = args.timezonefield.strip()

    header_printed = False
    count = 0
    while (count < args.count):
        count = count + 1
        stime = time.strftime(args.timeformat, time.localtime())
        tzone = time.strftime('%z')

        # current time in seconds for adustement of delay time
        time_s = time.time()

        table = dms.collect(
            args.table,
            filter=args.filter,
            include=[x.strip()
                     for x in args.include.split(',') if x.strip() != ''],
            exclude=[x.strip()
                     for x in args.exclude.split(',') if x.strip() != ''],
            check_tbl_version=not args.noversioncheck,
            preserve_orig_header=args.origheader
        )

        if not args.noheader and not header_printed:
            header_printed = True
            fields = [x for x in table["data"][0].keys()]
            fields.insert(0, args.datetimefield)
            fields.insert(1, args.timezonefield)
            sys.stdout.write(','.join(x for x in fields) + "\n")
            sys.stdout.flush()

        for row in table["data"]:
            r = args.csvdelimiter.join([str(strinquotes(x))
                                        for x in [stime, tzone] + [x for x in row.values()]])

            if len(r) > 0:
                sys.stdout.write(r + "\n")
                sys.stdout.flush()

        if count < args.count:
            elapsed_s = time.time() - time_s
            if args.nodelayadjust or elapsed_s > args.delay*args.nodelayperc:
                elapsed_s = 0
            time.sleep(args.delay - elapsed_s)

except (KeyboardInterrupt, SystemExit):
    pass
except Exception as e:
    sys.stderr.write("ERROR: %s\n" % str(e))
