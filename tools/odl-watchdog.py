import subprocess
from threading import Timer

checkInterval = None
waitDuration = 10.0
waitDurationAfterRestart = 300.0
karafBin = '/opt/stack/opendaylight/karaf-0.7.3/bin/karaf'
karafStartBin = '/opt/stack/opendaylight/karaf-0.7.3/bin/start'

def isKarafRunning():
    return subprocess.check_output(['ps', 'aux']).find(karafBin.encode()) != -1

def startKaraf():
    return subprocess.call([karafStartBin])

def check():
    if not isKarafRunning():
        print('ODL is not running, restarting now')
        startKaraf()
        checkInterval = Timer(waitDurationAfterRestart, check)
    else:
        print('ODL is still running')
        checkInterval = Timer(waitDuration, check)
    checkInterval.start()
check()
