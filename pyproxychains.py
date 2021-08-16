#!/usr/bin/python
import argparse
import subprocess
from subprocess import Popen
import requests


def getpubproxies():
    r = requests.get('http://pubproxy.com/api/proxy?limit=3&format=txt&type=https')
    if r.status_code == 200:
        print('successfully retrieved proxy data')
        return r.content.split('\n')
    else:
        print('[!] unable to retrieve data from pubproxy')
        quit() # change later to try other sources
        return False


def locateconf():
    subprocess.call('updatedb', shell=True)
    paths = subprocess.check_output('locate proxychains4_test.conf', shell=True)
    
    if paths:
        for f in paths.split('\n'):
            if 'etc' in f:
                print('found config file at %s' % f)
                return f
    else:
        print('[X] unable to locate proxychains config file!')
        quit()
    return False


def updateconf(conf_file, IPlist, protocol):
    with open(conf_file, 'r+') as f:
        flines = f.readlines()

    with open(conf_file, 'a') as f:
        for line in flines:
            f.write(line)
            if '[ProxyList]' in line:
                break

    with open(conf_file, 'a') as f:
        for IP in IPlist:
            f.write(protocol + ' ' + IP.split(':')[0] + ' ' + IP.split(':')[1] + '\n')

    print('updated conf file with retrieved IP addresses')
    return True


def startchain(app, async):
    if async:
        subprocess.Popen('proxychains ' + app + ' &', shell=True)
    else:
        subprocess.Popen('proxychains' + app, shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='grab up to date free proxy IP addresses (up to 3) and automatically add to proxychains config before starting a given application')
    parser.add_argument('-a', metavar='application', help='the name of the application we want to start, ex: ''firefox''')
    parser.add_argument('-x', action='store_true', help='set this flag if you wish the application to be launched asynchronously from the terminal')

    args = parser.parse_args()
    app = args.a

    IPlist = getpubproxies()
    conf_file = locateconf()
    if updateconf(conf_file, IPlist, 'https'):
        startchain(app, args.x)



