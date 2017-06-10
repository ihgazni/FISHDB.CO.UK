import json
import sys
from xdict.jprint import pobj

fd = open('./INFOS/pics.info','r')
pi = fd.read()
pics = json.loads(pi)
fd.close()

picid = sys.argv[2]
pobj(pics[picid])

import os
import subprocess
import shlex

def pipe_shell_cmds(shell_CMDs):
    '''
        shell_CMDs = {}
        shell_CMDs[1] = 'netstat -n'
        shell_CMDs[2] = "awk {'print $6'}"
    '''
    len = shell_CMDs.__len__()
    p = {}
    p[1] = subprocess.Popen(shlex.split(shell_CMDs[1]), stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    for i in range(2,len):
        p[i] = subprocess.Popen(shlex.split(shell_CMDs[i]), stdin=p[i-1].stdout, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if(len > 1):
        p[len] = subprocess.Popen(shlex.split(shell_CMDs[len]), stdin=p[len-1].stdout, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    result = p[len].communicate()
    if(len > 1):
        for i in range(2,len+1):
            returncode = p[i].wait()
    else:
        returncode = p[len].wait()
    return(result)

def imageMagick_close():
    shell_CMDs = {}
    shell_CMDs[1] = 'ps -ef'
    shell_CMDs[2] = 'egrep display'
    shell_CMDs[3] = 'egrep -v egrep'
    shell_CMDs[3] = "awk {'print $2'}"
    rslt = pipe_shell_cmds(shell_CMDs)
    rslt = rslt[0].decode('utf-8')
    rslt = rslt.strip('\n')
    rslt = rslt.split('\n')
    for i in range(0,rslt.__len__()):
        os.system('kill ' + rslt[i])

imageMagick_close()

from PIL import Image

def get_exif_data(img):
    '''
        http://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf
    '''
    ret = {}
    exifinfo = img._getexif()
    if(exifinfo != None):
        for tag, value in exifinfo.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
    if(50341 in ret):
        ret['PrintImageMatching'] = ret[50341]
        del ret[50341]
    return(ret)



img=Image.open(pics[picid]['image-dir'])
img.show()
img.close()


