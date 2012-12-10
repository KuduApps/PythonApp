from django.http import HttpResponse
from cStringIO import StringIO
import os
import sys
import azure

KNOWN_FAILURES = [
    # socket access forbidden
    'test_asynchat', 
    'test_logging', 
    'test_asyncore',
    'test_docxmlrpc', 
    'test_multiprocessing', 
    'test_httplib', 
    'test_socket',
    'test_urllib2_localnet', 
    'test_poplib', 
    'test_httpservers', 
    'test_xmlrpc', 
    'test_ftplib', 
    'test_smtplib', 
    'test_telnetlib', 

    # subprocess std handles
    'test_threading', 
    'test_unicodedata',
    'test_winsound', 
    'test_warnings', 
    'test_sys',   # also fails due to stdout being redirected
    'test_quopri', 
    'test_file2k',
    'test_subprocess', 

    # email.charset is mutated in Django
    'test_email', 
    'test_email_renamed', 

    # builtins module is a little different due to Django
    'test_rlcompleter',

    #  requires visual studio
    'test_distutils',

    # stdout redirected, no exception when expected when calling into print
    'test_descr', 

    # times out ctrl-break to console
    'test_os',

    # cannot access:
    #  OpenKey(HKEY_CURRENT_USER, test_key_name, 0, KEY_ALL_ACCESS) as key:
    #  EnumValue(HKEY_PERFORMANCE_DATA, 0)
    #  with OpenKey(HKEY_CURRENT_USER, test_key_name, 0, KEY_ALL_ACCESS) as key:
    #  SetValue(root_key, test_key_name, REG_SZ, "Default value") (HKEY_CURRENT_USER)
    #  SetValue(root_key, test_key_name, REG_SZ, "Default value") (HKEY_CURRENT_USER)
    'test_winreg',

    # cannot write to systemprofile romaing dir
    'test_site', 

    # cannot access \\%COMPUTERNAME%\c$\python27\python.exe
    'test_tcl', 

    # crashes writing 10 bytes to a memory mapped file
    'test_mmap',

    # hangs calling uuid.getnode()
    'test_uuid', 
]

def stdlib(request):
    """handles requests to /stdlib/ which can either run tests one by one, or can
       specify the test name to be run"""

    test_path = sys.prefix + r'\Lib\test'
    if test_path not in sys.path:
        sys.path.append(test_path)

    url = request.path[8:]
    if url.endswith('/'):
        url = url[:-1]
    
    sys.stdout = sys.stderr = StringIO()
    if not url:
        # no test specified, run tests one-by-one using regrtest
        import regrtest
        cur_argv = list(sys.argv)
        sys.argv.extend(KNOWN_FAILURES)
        result = ''
        try:
            try:
                res = regrtest.main(single=True, exclude=True, verbose = True)
            finally:
                sys.argv[:] = cur_argv
        except SystemExit, se:     
            if se.code != 0:
                result = '<font color=red>Test failed</font>'
            else:
                result = '<font color=green>Test passed</font>'

        html = "<html><body>" + result + "<br>" + sys.stdout.getvalue().replace('\n', '<br>') + "</body></html>"
    else:
        # run the individual test using regrtest
        def runner():
            from test import regrtest
            env = dict(os.environ)
            try:
                regrtest.runtest(url, 1, False)
            except Exception, e:
                print e
                import traceback
                traceback.print_exc()
            finally:
                os.environ.update(env)
            
            
        import threading
        th = threading.Thread(target=runner)
        th.start()
        th.join(30)
        if th.isAlive():
             print 'thread has not exited!'

        html = "<html><body>" + sys.stdout.getvalue().replace('\n', '<br>') + "</body></html>"

    return HttpResponse(html)

def ping_mysql(request):
    import MySQLdb
    db = MySQLdb.connect(
                    os.environ["MySqlServer"], 
                    os.environ["MySqlUsername"],
                    os.environ["MySqlPassword"])
    db.select_db('python_test_db')
    cur = db.cursor()
    cur.execute("insert into foo (id, data) values (1, 'bar');")
    cur.execute("select * from foo")
    res = cur.fetchmany()
    if (1L, 'bar') in res:
        cur.execute("delete from foo where id=1")
        cur.execute("select * from foo")
        if not cur.fetchmany():
            return HttpResponse("Succeeded!")
    return HttpResponse("Failed! " + repr(res))
 

def test_mysql_dmo(request):
    try:
        import MySQLdb
        db = MySQLdb.connect(
                        os.environ["MySqlServer"], 
                        os.environ["MySqlUsername"],
                        os.environ["MySqlPassword"])
        db.query("create database test_dmo_database;")
        db.query("drop database test_dmo_database")
        return HttpResponse("Succeeded!")
    except:
        import traceback
        return HttpResponse("Failed! " + traceback.format_exc())
    
def test_azure_call(request):
    import os
    try:
        from azure.storage import BlobService
        bs = BlobService(os.environ["AZURE_STORAGE_ACCOUNT"], os.environ["AZURE_STORAGE_ACCESS_KEY"])
        import random
        container_name = hex(int(random.random() * 1000000000))

        bs.create_container(container_name)
        bs.put_blob(container_name, 'testblob', 'hello world\n', 'BlockBlob')
        blob = bs.get_blob(container_name, 'testblob')
        if blob != 'hello world\n':
            return HttpResponse("Failed!", status = '404')
        
        bs.delete_blob(container_name, 'testblob')
        bs.delete_container(container_name)

        return HttpResponse("Succeeded!")
    except:
        try:
            import traceback
        
            return HttpResponse(traceback.format_exc() + str(os.environ.keys()))
        except:
            import traceback
            return HttpResponse(traceback.format_exc())


def test_http_request(request):
    if 'url' not in request.REQUEST:
        url = 'www.python.org'
    else:
        url = request.REQUEST['url']

    import httplib
    conn = httplib.HTTPConnection(url)
    conn.request('GET', '/')
    resp = conn.getresponse()
    if resp.status == 200:
        return HttpResponse("Succeeded!")
    return HttpResponse("Failed!")
    

def test_local_file(request):
    if 'file' not in request.REQUEST:
        import tempfile
        filename = tempfile.mktemp()
    else:
        filename = request.REQUEST['file']
    
    f = file(filename, 'w')
    f.write('hello world\n' * 100)
    f.close()
    f = file(filename, 'r')
    if f.read() == 'hello world\n' * 100:
        f.close()
        import os
        os.unlink(filename)
        return HttpResponse("Succeeded!") 
    return HttpResponse("Failed!")
    
def test_write_illegal_path(request):
    try:
         f = file('C:\\foo.txt')
         return HttpResponse("Failed!")
    except:
        pass
    return HttpResponse("Succeeded!") 

def run_one_test(test_name):
        sys.stdout = sys.stderr = StringIO()
        from unittest import TestProgram
        try:
            TestProgram(test_name, verbosity=2)
        except SystemExit, e:
             if e.code != 0:
                 print 'Failed!'
             else:
                 print 'Succeeded!'
   
        except:
            import traceback
            traceback.print_exc()

        html = "<html><body>" + sys.stdout.getvalue().replace('\n', '<br>') + "</body></html>"
        return HttpResponse(html)

def run_azure_test(request):
    test_name = 'DjangoApplication.azuretest.' + request.path[7:]    
    
    return run_one_test(test_name)
