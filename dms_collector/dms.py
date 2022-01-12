
import time
import re

import xml.etree.ElementTree as ET

import urllib3
import requests

from dms_collector import __version__

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TBML_VERSIONS = ["11.0"]

# DMS REQESTS URLs
# before changing the urls below check their param bindings as per their usage
DMSREQUEST_HEADER = "%s/dms/Spy?format=xml&table=%s&description=true&value=false"
DMSREQUEST_DATA = "%s/dms/Spy?format=xml&table=%s&value=true&cached=false"
DMSLOGIN_URL = "%s/dms/j_security_check"

# timeout to read data from dms spy
TIMEOUT_CONNECT = 3.05
TIMEOUT_READ = 30


def is_number(s):
    '''
    Checks if the argument is a number.
    '''
    s = str(s)
    p = re.compile(r'^[\+\-]?[0-9]*(\.[0-9]+)?$')
    return s != '' and p.match(s)


def check_positive(value):
    '''
    Checks if the number is a positive integer.
    '''
    ivalue = int(value)
    if ivalue <= 0:
        raise Exception("%s is an invalid positive int value" % value)
    return ivalue


def eval_filter(filter, tags, fields):
    '''
    Evaluates the filter as a Python expression using tags and fields. It adds 
    tags and fields to the scope of the filter evaluation.  
    '''
    try:
        for k, v in tags.items():
            if v is not None:
                exec(k + "=\"" + v + "\"")
        for k, v in fields.items():
            if v is not None:
                exec(k + "=" + str(v))
        return eval(filter)
    except Exception:
        return False


def get_tags_fields(row):
    '''
    Retrieves tags and fields from the row dict. 
    '''
    tags = {k: str(v).replace('\n', ' ')
            for k, v in row.items() if not(is_number(v))}
    fields = {k: float(v) for k, v in row.items() if is_number(v)}
    return tags, fields


def normalize(header, preserve_orig_header):
    '''
    Normalizes the header, i.e. replaces dots with underscores. 
    '''
    if not preserve_orig_header:
        return header.replace(".", "_")
    return header


def int_or_float_or_str(v):
    '''
    Converts the value to int or float. If this is not possible, then it returns 
    the original value. 
    '''
    if isinstance(v, str):
        try:
            return int(v)
        except:
            try:
                return float(v)
            except Exception:
                return v
    else:
        return v


class DmsCollector():
    '''
    The main DMS collector class that allows to retrieve a DMS table from DMS Spy application. 
    '''

    def __init__(self, admin_url, username=None, password=None, basic_auth=False):
        '''
        Create the instance of dms collector with admin server url `admin_url` and authentication details `username` and `password`.
        When you connect to the DMS Spy running on FMW 11g, then you need to set the `basic_auth` to `True`. 
        '''
        self.logged_in = False
        self.session = requests.session()
        self.admin_url = admin_url
        self.username = username
        self.password = password
        self.basic_auth = basic_auth
        self.header_cache = {}

    def login(self):
        '''
        Performs login to the DMS Spy application using the login form.
        '''
        headers = {"User-Agent": "dms-collector/%s" % __version__}
        logindata = {"j_username": self.username,
                     "j_password": self.password, "j_character_encoding": "UTF-8"}
        r = self.session.post(DMSLOGIN_URL % (
            self.admin_url), headers=headers, data=logindata, allow_redirects=True, verify=False)
        r.raise_for_status()
        if len([x.url for x in r.history]) == 1:
            raise Exception("Wrong username or password. Login failed!")
        self.logged_in = True

    def call(self, url):
        '''
        Sends HTTP GET at the specified `url` of the DMS Spy application. When the basic authentication 
        is enabled, the username and password are added on the request. 
        '''
        if not self.logged_in and not self.basic_auth:
            self.login()
        if self.basic_auth and self.username is not None and self.password is not None:
            r = self.session.get(url, auth=(self.username, self.password),
                                 timeout=(TIMEOUT_CONNECT, TIMEOUT_READ), allow_redirects=True)
        else:
            r = self.session.get(url, timeout=(
                TIMEOUT_CONNECT, TIMEOUT_READ), allow_redirects=True)
        r.raise_for_status()
        return r

    def retrieve_data(self, url, check_tbl_version=True):
        '''
        Retrieves and parses DMS table data as XML.
        '''
        r = self.call(url)

        # remove the default namespace if it exsits
        # dmss spy deployed to wls 12c uses default namespaces in TBML whereas previous version not
        xmlstring = r.text
        xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)
        root = ET.fromstring(xmlstring)
        if not(check_tbl_version):
            tbml_version = root.get("version")
            if tbml_version not in TBML_VERSIONS:
                raise Exception("Data retrieved are of not supported tbml version %s. Supported versions are: %s"
                                % (tbml_version, ','.join(TBML_VERSIONS)))
        return root

    def get_header(self, table, check_tbl_version=True):
        '''
        Retrieves a DMS table header. If the table does not exist then it raises an error.
        '''
        if table not in self.header_cache:
            root = self.retrieve_data(DMSREQUEST_HEADER % (
                self.admin_url, table), check_tbl_version=check_tbl_version)
            te = root.find("./table")    
            if te is None or te.get("name") != table:
                raise Exception(f"The table '{table}' does not exist!")
            cdef = root.findall(".//columndef")
            fields = [x.get("name") for x in cdef]
            self.header_cache[table] = fields
        return self.header_cache[table]

    def collect(self, table, check_tbl_version=True, preserve_orig_header=False, include=[], exclude=[], filter=None):
        '''
        Retrieves the DMS table as a list of dict where a dict represents a row with fields and values. 
        The `include` parameter provides a list of fields that should be included in the result, the `exclude` parameter 
        provides a list of fields that should be excluded from the result and `filter` defines a Python expression 
        that is used to filter our the table rows. The expression can contain conditions with table fields.   
        '''
        start_time = time.time()

        header = self.get_header(table, check_tbl_version)
        root = self.retrieve_data(DMSREQUEST_DATA % (
            self.admin_url, table), check_tbl_version=check_tbl_version)

        rows = []
        for rw in root.findall(".//row"):
            row = {}
            for key in header:
                nkey = normalize(
                    key, preserve_orig_header=preserve_orig_header)
                if (nkey not in exclude and len(include) == 0) or nkey in include:
                    cv = rw.find("./column[@name='%s']" % key)
                    if cv is not None and cv.text is not None:
                        if cv.text.strip() != '':
                            row[nkey] = int_or_float_or_str(cv.text.strip())
                        else:
                            row[nkey] = None
                    else:
                        row[nkey] = None

            output_row = True
            if filter is not None and filter.strip() != '':
                tags, fields = get_tags_fields(row)
                output_row = eval_filter(filter, tags, fields)

            if output_row is True:
                rows.append(row)

        return {
            "time": time.time(),
            "table": table,
            "url": DMSREQUEST_HEADER % (self.admin_url, table),
            "include": include,
            "exclude": exclude,
            "filter": filter,
            "query_time": time.time()-start_time,
            "data": rows
        }
