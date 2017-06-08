import sys
import os
import subprocess
import shlex
import json
import copy
import hashlib
import re

from xdict.jprint import print_j_str

def get_printed_str(obj,with_color=1):
    s = obj.__str__()
    pls = print_j_str(s,with_color=with_color)
    ps = ''
    for n in pls:
        ps = ''.join((ps,pls[n],'\n'))
    return(ps)

def md5(obj):
    obj = obj.__str__().encode()
    m2 = hashlib.md5()   
    m2.update(obj)   
    return(m2.hexdigest().__str__())

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

def file_name_condition_str(condition_str):
    regex_or = re.compile("\|")
    fns = regex_or.sub('_or_',condition_str)
    regex_slash = re.compile("/")
    fns = regex_or.sub('_or_',fns)
    return(fns)

def exact_search(pics,search_dict):
    search_str = get_printed_str(search_dict,with_color=0)
    md5_str = md5(search_str)
    for picid in pics:
        pic = pics[picid]
        matched = 1
        for key in search_dict:
            if(key in pic):
                if(pic[key] == search_dict[key]):
                    matched = 1
                else:
                    matched = 0
            else:
                matched = 0 
                break
        if(matched == 1):
            fns = ''
            for key in search_dict:
                fns = key + '=' + str(search_dict[key])
                fns = file_name_condition_str(fns)
                break
            exact_dir = './SHOWED/' + fns[:20] +  '__' + md5_str[:8] +'/'
            if(os.path.exists(exact_dir)):
                pass
            else:
                os.makedirs(exact_dir)
            fd = open(exact_dir+'search_conditions','w+')
            fd.write(search_str)
            fd.close()
            image_dir = pic['image-dir']
            showed_image_dir = exact_dir + str(pic['picid']) + '.' + pic['image-type']
            cmd = 'cp ' + image_dir + ' ' + showed_image_dir
            pipe_shell_cmds({1:cmd})
        else:
            pass

mode = sys.argv[2]

if(mode == "exact"):
    print('sea\ncom-name\ncontributor\nimage-url\ninfo-dir\nrating\ntown\nsci-name\ndesc\nimage-type\nfamily\nsite\nsub-site\ncountry\nimage-dir\npicid\nreferer-url\nlength\nsci-family\npic-url')
    search_dict = {}
    for i in range(3,sys.argv.__len__(),+2):
        search_dict[sys.argv[i][1:]] = sys.argv[i+1]
    shell_CMDs = {}
    shell_CMDs[1] = 'cat ./INFOS/pics.info'
    rslt = pipe_shell_cmds(shell_CMDs)
    rslt = rslt[0].decode('utf-8')
    pics = json.loads(rslt)
    new_pics = {}
    for key in pics:
        new_pics[int(key)] = pics[key]
    pics = new_pics
    exact_search(pics,search_dict)
else:
    shell_CMDs = {}
    shell_CMDs[1] = 'cat ./INFOS/lines.info'
    condition_str = sys.argv[3]
    shell_CMDs[2] = 'egrep "'+ condition_str +'"'
    print(shell_CMDs)
    rslt = pipe_shell_cmds(shell_CMDs)
    rslt = rslt[0].decode('utf-8')
    rslt = rslt.strip('\n')
    rslt = rslt.split('\n')
    fns = file_name_condition_str(condition_str)
    exact_dir = './SHOWED/' + fns[:10] +  '__' + md5(condition_str)[:8]+'/'
    if(os.path.exists(exact_dir)):
        pass
    else:
        os.makedirs(exact_dir)
    fd = open(exact_dir+'search_conditions','w+')
    fd.write(condition_str)
    fd.close()
    for i in range(0,rslt.__len__()):
        pic = json.loads(rslt[i])
        image_dir = pic['image-dir']
        showed_image_dir = exact_dir + str(pic['picid']) + '.' + pic['image-type']
        cmd = 'cp ' + image_dir + ' ' + showed_image_dir
        pipe_shell_cmds({1:cmd})

