
import requests 
import time
import sys
import re
import urllib3

import xml.etree.ElementTree as ET

from dms_collector import __version__

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TBML_VERSIONS=["11.0"]

# DMS REQESTS URLs
# before changing the urls below check their param bindings as per their usage
DMSREQUEST_HEADER="%s/dms/Spy?format=xml&table=%s&description=true&value=false"
DMSREQUEST_DATA="%s/dms/Spy?format=xml&table=%s&value=true&cached=false"
DMSLOGIN_URL="%s/dms/j_security_check"

# timeout to read data from dms spy
TIMEOUT_CONNECT=3.05
TIMEOUT_READ=30

# maximum buffer size that will be read from the pipe at once
EVENTS_BUFFERSIZE=1024

def is_number(s):
    s=str(s)
    p = re.compile(r'^[\+\-]?[0-9]*(\.[0-9]+)?$')
    return s != '' and p.match(s)

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise Exception("%s is an invalid positive int value" % value)
    return ivalue

def eval_filter(filter, tags, fields):
    try:
        for k,v in tags.items():
            if v is not None:
                exec(k + "=\"" + v + "\"")
        for k,v in fields.items():
            if v is not None:
                exec(k + "=" + str(v))
        return eval(filter)
    except Exception as e:
        #sys.stderr.write("Error when evaluating the filter '%s': %s!\n" % (filter, e)) 
        return False      

def get_tags_fields(row): 
    tags   = { k:str(v).replace('\n', ' ') for k, v in row.items() if not(is_number(v)) }
    fields = { k:float(v) for k, v in row.items() if is_number(v) }                            
    return tags, fields

def normalize(header,preserve_orig_header):
    if not preserve_orig_header:
        return header.replace(".","_")
    else:
        return header

def int_or_float_or_str(v):
    if isinstance(v,str):
        try:
            return int(v)
        except:
            try:
                return float(v)
            except:
                return v 
    else:
        return v

class DmsCollector():
    
    def __init__(self, admin_url, username=None, password=None, basic_auth=False, read_timeout=TIMEOUT_READ):
        self.logged_in = False
        self.session = requests.session()
        self.admin_url = admin_url
        self.username = username
        self.password = password
        self.read_timeout = read_timeout
        self.basic_auth = basic_auth
        self.header_cache = {}
    
    def login(self):
        headers   = { "User-Agent" : "dms-collector/%s"%__version__ }
        logindata = {"j_username" : self.username, "j_password" : self.password, "j_character_encoding" : "UTF-8" }
        r = self.session.post(DMSLOGIN_URL%(self.admin_url),headers=headers,data=logindata,allow_redirects=True,verify=False)
        r.raise_for_status()
        if len([x.url for x in r.history])==1:
            raise Exception("Wrong username or password. Login failed!")
        self.logged_in = True

    def call(self, url):
        if not self.logged_in and not self.basic_auth:
            self.login()
        if self.basic_auth and self.username is not Node and self.password is not None:
            r = self.session.get(url, auth=(self.username, self.password),\
                timeout=(TIMEOUT_CONNECT, self.readt_imeout),allow_redirects=True)
        else:
            r = self.session.get(url,timeout=(TIMEOUT_CONNECT, self.read_timeout),allow_redirects=True)
        r.raise_for_status()
        return r

    def retrieve_data(self,url, check_tbl_version=True):
        r = self.call(url)

        # remove the default namespace if it exsits
        # dmss spy deployed to wls 12c uses default namespaces in TBML whereas previous version not
        xmlstring=r.text
        xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)
        root = ET.fromstring(xmlstring)   
        if not(check_tbl_version): 
            tbml_version = root.get("version")
            if tbml_version not in TBML_VERSIONS:
                raise Exception("Data retrieved are of not supported tbml version %s. Supported versions are: %s"
                    %(tbml_version,','.join(TBML_VERSIONS)))
        return root

    def get_header(self, table, check_tbl_version=True):
        if table not in self.header_cache: 
            root = self.retrieve_data(DMSREQUEST_HEADER%(self.admin_url,table), check_tbl_version=check_tbl_version)                
            cdef = root.findall(".//columndef")
            fields = [x.get("name") for x in cdef]
            self.header_cache[table] = fields
        return self.header_cache[table]

    def collect(self, table, check_tbl_version=True, preserve_orig_header=False, include=[],exclude=[], filter=None):
        start_time=time.time()
        
        header = self.get_header(table, check_tbl_version)
        root = self.retrieve_data(DMSREQUEST_DATA%(self.admin_url,table), check_tbl_version=check_tbl_version)
       
        rows = []
        for rw in root.findall(".//row"):
            row={}
            for key in header:
                nkey = normalize(key, preserve_orig_header=preserve_orig_header)
                if (nkey not in exclude and len(include) == 0) or nkey in include:
                    cv = rw.find("./column[@name='%s']"%key)
                    if cv is not None and cv.text is not None:
                        if cv.text.strip() != '':
                            row[nkey] = int_or_float_or_str(cv.text.strip())
                        else:
                            row[nkey] = None   
                    else:
                        row[nkey] = None
            
            output_row = True
            if filter is not None and filter.strip()!='':
                tags, fields = get_tags_fields(row)
                output_row = eval_filter(filter,tags,fields)
            
            if output_row is True:
                rows.append(row)
        
        result_dict = {}
        result_dict["time"] = time.time()
        result_dict["table"] = table
        result_dict["url"] = DMSREQUEST_HEADER%(self.admin_url,table)
        if include is not None and len(include)>0:
            result_dict["include"] = include
        if exclude is not None and len(exclude)>0:
            result_dict["exclude"] = exclude
        if filter is not None:
            result_dict["filter"] = filter
        result_dict["query_time"] = time.time()-start_time
        result_dict["data"] = rows
        return result_dict
    