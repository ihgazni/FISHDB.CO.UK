import navegador5 as nv 
import navegador5.url_tool as nvurl
import navegador5.head as nvhead
import navegador5.body as nvbody
import navegador5.cookie 
import navegador5.cookie.cookie as nvcookie
import navegador5.cookie.rfc6265 as nvrfc6265
import navegador5.jq as nvjq
import navegador5.js_random as nvjr
import navegador5.file_toolset as nvft
import navegador5.shell_cmd as nvsh
import navegador5.html_tool as nvhtml
import navegador5.solicitud as nvsoli
import navegador5.content_parser 
import navegador5.content_parser.amf0_decode as nvamf0
import navegador5.content_parser.amf3_decode as nvamf3

from lxml import etree
import lxml.html
import collections
import copy
import re
import urllib
import os
import json

from xdict.jprint import  pobj
from xdict.jprint import  print_j_str



#/opt/PY/PY3/DIVE/FISHDB.CO.UK/
#/opt/PY/PY3/DIVE/FISHDB.CO.UK/SOURCE/fishdb.co.uk.py
#/opt/PY/PY3/DIVE/FISHDB.CO.UK/FAMILY/
#/opt/PY/PY3/DIVE/FISHDB.CO.UK/FAMILY/Angelfish/
#/opt/PY/PY3/DIVE/FISHDB.CO.UK/FAMILY/Angelfish/PICS/
#/opt/PY/PY3/DIVE/FISHDB.CO.UK/FAMILY/Angelfish/INFOS/


def new_pic():
    '''
        # Picture ID:
        # Family:
        # Common Name:
        # Scientific Name:
        # Site:
        # Nearest Town:
        # Country:
        # Ocean/Sea:
        # Contributor:
    '''
    pic = {'picid':None,
        'family':None,
        'com-name':None,
        'sci-name':None,
        'site':None,
        'town':None,
        'country':None,
        'sea':None,
        'contributor':None,
        'length':None,
        'rating':None,
        'desc':None,
        'image-url':None,
        'image-type':None,
        'pic-url':None,
        'image-dir':None,
        'info-dir':None,
        'referer-url':None
    }
    return(pic)

def fishdb_co_uk_init():
    info_container = nvsoli.new_info_container()
    base_url = 'http://www.fishdb.co.uk/'
    info_container['base_url'] = base_url
    info_container['url'] = base_url
    info_container['method'] = 'GET'
    req_head_str = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36\r\nAccept-Encoding: gzip,deflate,sdch\r\nAccept-Language: en;q=1.0, zh-CN;q=0.8'''
    info_container['req_head'] = nvhead.build_headers_dict_from_str(req_head_str,'\r\n')
    info_container['req_head']['Connection'] = 'close'
    #### init records_container
    records_container = nvsoli.new_records_container()
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    info_container = nvsoli.auto_redireced(info_container,records_container)
    return((info_container,records_container))



def get_signin_link_href(info_container):
    to_url = info_container['base_url']
    html_text = info_container['resp_body_bytes'].decode('utf-8')
    root = etree.HTML(html_text)
    eles_a = root.xpath('//p/span/a')
    eles_text = root.xpath('//p/span/a/text()')
    regex_login = re.compile('Login',re.I)
    regex_register = re.compile('Register',re.I)
    for seq in range(0,eles_text.__len__()):
        if(regex_login.search(eles_text[seq])):
            href = collections.OrderedDict(eles_a[seq].items())['href']
            href = ''.join((to_url,'/',href))
            return(href)
    href = ''
    href = ''.join((to_url,'/',href))
    return(href)


def gen_login_post_body(eles,username,password,emailme):
    eles_len = eles.__len__()
    query_dict = {}
    for i in range(0,eles_len):
        ele = eles[i]
        name = collections.OrderedDict(ele.items())['name']
        try:
            value = collections.OrderedDict(ele.items())['value']
        except Exception as err:
            if(err.__repr__() == "KeyError('value',)"):
                if(name=='username'):
                    print(value)
                    value = username
                elif(name=='password'):
                    value = password
                else:
                    value = ''
        try:
            type = collections.OrderedDict(ele.items())['type']
        except Exception as err:
            if(err.__repr__() == "KeyError('value',)"):
                type = ''
        query_dict[name] = value
        if(type == 'submit'):
            if(emailme==1):
                query_dict[name] = 'E-mail me'
            else:
                query_dict[name] = 'Submit'
    return(urllib.parse.urlencode(query_dict))


def fishdb_co_uk_login(username,password,info_container,records_container):
    signin_link_href = get_signin_link_href(info_container)
    info_container['req_head']['Referer'] = info_container['base_url']
    info_container['req_head']['Upgrade-Insecure-Requests'] = 1
    info_container['url'] = signin_link_href
    info_container['method'] = 'GET'
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    html_text = info_container['resp_body_bytes'].decode('utf-8')
    root = etree.HTML(html_text)
    eles = root.xpath('//form')
    od = collections.OrderedDict(eles[0].items())
    action = od['action']
    method = od['method']
    eles = root.xpath('//form//input')
    info_container['req_body'] = gen_login_post_body(eles,username,password,0)
    info_container['req_head']['Referer'] = signin_link_href
    info_container['req_head']['Content-Type'] = 'application/x-www-form-urlencoded'
    info_container['req_head']['Upgrade-Insecure-Requests'] = 1
    info_container['method'] = method.upper()
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    return((info_container,records_container))

def get_families_and_oceans(main_page_html_text,base_url):
    html_text = main_page_html_text
    root = etree.HTML(html_text)
    eles = root.xpath('//menu/li/a') 
    families = {}
    oceanes = {}
    for i in range(0,eles.__len__()):
        ele = eles[i]
        href = ele.get('href')
        condf = 'family' in href
        condo = 'ocean' in href
        if(condf):
            family = ele.text
            families[family] = base_url+href
        if(condo):
            ocean = ele.text
            oceanes[ocean] = base_url+href
    return((families,oceanes))



def get_all_pic_urls(info_container,records_container,next=0,limit=4294967296):
    eles_picid = []
    eles_exact_url = []
    eles_referer = []
    is_not_last = True
    to_url = ''
    from_url = info_container['base_url']
    regex_picid = re.compile('[0-9]+')
    cond = next < limit
    while(is_not_last & cond):
        to_url = ''.join((info_container['base_url'],'findpicture.php','?','order=rank','&range=',next.__repr__()))
        info_container['url'] = to_url
        info_container['req_head']['Referer'] = from_url
        info_container = nvsoli.walkon(info_container,records_container=records_container)
        html_text = info_container['resp_body_bytes'].decode('utf-8')
        root = etree.HTML(html_text)
        next_last = root.xpath('//a[@href]/text()')
        eles_img = []
        eles_img = root.xpath('//img[(@alt) and  (@src) and (@title)]')
        if('Next' in next_last):
            next = next + eles_img.__len__()
        else:
            is_not_last = False
        from_url = to_url
        eles_picid_tmp = []
        eles_picid_tmp = root.xpath("//p/b/a[@href]")
        for i in range(0,eles_img.__len__()):
            eles_picid.append(eles_picid_tmp[i*2])
            seq = eles_picid.__len__() - 1
            m = regex_picid.search(eles_picid[seq].items()[0][1])
            eles_exact_url.append(''.join((info_container['base_url'],eles_picid[seq].items()[0][1])))
            eles_referer.append(from_url)
            eles_picid[seq] = m.group(0)
        cond = next < limit
    rslt = {}
    rslt['picids']= eles_picid
    rslt['exact_urls'] = eles_exact_url
    rslt['referers']= eles_referer
    return(rslt)

def creat_toppics_dir(maindir):
    exact_dir = maindir + 'PICS/'
    if(os.path.exists(exact_dir)):
        pass
    else:
        os.makedirs(exact_dir)
    exact_dir = maindir + 'INFOS/'
    if(os.path.exists(exact_dir)):
        pass
    else:
        os.makedirs(exact_dir)
    exact_dir = maindir + 'INFOS/orig.info' 
    if(os.path.exists(exact_dir)):
        pass
    else:
        nvft.write_to_file(fn=exact_dir,content=b'',op='wb+')



def get_exact_single_picinfo(picid,to_url,from_url,info_container,records_container,lowerfamilynames,database_parent_dir,pics):
    info_container['req_head']['Referer'] = from_url
    info_container['method'] = 'GET'
    info_container['url'] = to_url
    info_container = nvsoli.walkon(info_container,records_container=records_container)
    html_text = info_container['resp_body_bytes'].decode('utf-8')
    pic = new_pic()
    pic['picid'] = picid
    pic['pic-url'] = to_url
    pic['referer-url'] = from_url
    root = etree.HTML(html_text)
    ###############################################################
    exact_img = root.xpath('//img[(@alt) and  (@src) and (@title)]')
    pic['image-url'] = ''.join(('http://www.fishdb.co.uk/',exact_img[0].items()[3][1]))
    regex_pic_type = re.compile('\.([^/]+)$')
    m = regex_pic_type.search(pic['image-url'])
    pic['image-type'] = m.group(1)
    pic['com-name'] = root.xpath("//p/b/span[@alt and @title]/text()")[0]
    try:
        pic['sci-name'] = root.xpath("(//p/b/i/span[@class='lname' and @title]/text())|(//p/b/i/a[@href and @title]/text())")[0]
    except:
        print('no sci-name')
    else:
        pass
    #<i><a href='showspeciesdetails.php?speciesid=88' title='Pomacanthus imperator'>Pomacanthus imperator</a></i>
    exact_length_tmp = []
    exact_length_tmp = root.xpath("//p/b/text()")
    regex_length = re.compile('[0-9]+cm')
    exact_length_tmp_2 = []
    for i in range(0,exact_length_tmp.__len__()):
        m = regex_length.search(exact_length_tmp[i])
        if(m):
            exact_length_tmp_2.append(m.group(0))
        else:
            exact_length_tmp_2.append(0)
    pic['desc'] = []
    for i in range(0,exact_length_tmp.__len__()):
        pic['desc'].append(exact_length_tmp[i])
    if(exact_length_tmp_2.__len__()>2):
        pic['length'] = exact_length_tmp_2[2]
    else:
        pic['length'] = None
    exact_apr_tmp = root.xpath('//table/tr/td/center/p/text()')
    apr_len = exact_apr_tmp.__len__()
    regex_photographer = re.compile('Photographer:[ ]+(.*)')
    regex_picrating = re.compile('Picture Rating:[ ]+(.*)')
    exact_location_tmp = exact_apr_tmp[0]
    exact_photographer_tmp = ''
    exact_picrating_tmp = '0'
    previous = 0
    for i in range(1,apr_len):
        temp = exact_apr_tmp[i]
        m_grapher = regex_photographer.search(temp)
        m_picrating = regex_picrating.search(temp)
        if(m_grapher):
            exact_photographer_tmp = m_grapher.group(1)
            previous = 1
        elif(m_picrating):
            exact_picrating_tmp = m_picrating.group(1)
            previous = 2
        else:
            if(previous == 0):
                exact_location_tmp =''.join((exact_location_tmp,"@",temp))
            elif(previous == 1):
                exact_photographer_tmp =''.join((exact_photographer_tmp,"@",temp))
            elif(previous == 2):
                exact_picrating_tmp =''.join((exact_picrating_tmp,"@",temp))
            else:
                pass
    tmp = exact_location_tmp.split('@')
    location = tmp[0]
    locs = location.split('-')
    locs.reverse()
    ld = {'sea':0,'country':1,'town':2,'site':3,0:'sea',1:'country',2:'town',3:'site'}
    for i in range(0,locs.__len__()):
        pic[ld[i]] = locs[i].strip(' ')
    for i in range(1,tmp.__len__()):
        pic['desc'].append(tmp[i])
    pic['contributor'] = exact_photographer_tmp.split('@')[0]
    pic['rating'] = exact_picrating_tmp.split('@')[0]
    regex_family = re.compile('family=(.*)')
    for key in lowerfamilynames:
        if(key in pic['com-name'].lower()):
            pic['family'] = lowerfamilynames[key]
            m = regex_family.search(pic['family'])
            pic['family'] = m.group(1)
            break
    ################################################
    exact_dir = ''.join((database_parent_dir,'PICS/',pic['picid'].__str__(),'.',pic['image-type']))
    if(os.path.exists(exact_dir)):
        pass
    else:
        info_container['req_head']['Referer'] = to_url
        info_container['method'] = 'GET'
        info_container['url'] = pic['image-url']
        info_container = nvsoli.walkon(info_container,records_container=records_container)
        nvft.write_to_file(fn=exact_dir,content=info_container['resp_body_bytes'],op='wb+')
    ##########################################
    exact_dir = ''.join((database_parent_dir,'INFOS/orig.info'))
    nvft.write_to_file(fn=exact_dir,content='\n',op='a+')
    nvft.write_to_file(fn=exact_dir,content=json.dumps(pic),op='a+')
    if(picid in pics):
        pass
    else:
        pics[picid] = pic
    return((info_container,records_container))



##################################################################

##################################################################
username = sys.argv[1]
password = sys.argv[2]
maindir = sys.argv[3]
fromwhich = sys.argv[4]
##################################################################


creat_toppics_dir(maindir)

info_container,records_container = fishdb_co_uk_init()
info_container,records_container = fishdb_co_uk_login(username,password,info_container,records_container)

info_container['method'] = 'GET'
info_container['req_body'] = None
info_container = nvsoli.auto_redireced(info_container,records_container)
main_page_html_text  = info_container['resp_body_bytes'].decode('utf-8')
families,oceanes = get_families_and_oceans(main_page_html_text,info_container['base_url'])
lowerfamilynames = {}
for key in families:
    lowerfamilynames[key.lower()] = families[key]

mypics_url = info_container['base_url'] + "findpicture.php?user=" + username
toppics_url = info_container['base_url'] + "findpicture.php?order=rank"

info_container['url'] = toppics_url

rslt = get_all_pic_urls(info_container,records_container)
picids = rslt['picids']
pic_urls = rslt['exact_urls']
pic_refers = rslt['referers']

#################
pics = {}
for i in range(fromwhich,picids.__len__()):
    print(i)
    picid = picids[i]
    to_url = pic_urls[i]
    from_url = pic_refers[i]
    info_container,records_container = get_exact_single_picinfo(picid,to_url,from_url,info_container,records_container,lowerfamilynames,maindir,pics)


exact_dir = ''.join((maindir,'INFOS/picsdict'))
nvft.write_to_file(fn=exact_dir,content=json.dumps(pics),op='w+')


############################
new_pics = {}
for key in pics :
    new_pics[int(key)] = pics[key]
    new_pics[int(key)]['picid'] = int(key)
    new_pics[int(key)]['rating'] = float(pics[key]['rating'])

no_town = {}
for key in new_pics:
    if(new_pics[key]['town'] == None):
        no_town[key] = new_pics[key]

new_pics = copy.deepcopy(new_pics)
for key in no_town:
    if(no_town[key]['country'] == None):
        pass
    else:
        country = no_town[key]['country']
        locs = country.split('/')
        locs.reverse()
        ld = {'country':0,'town':1,'site':2,'sub-site':3,0:'country',1:'town',2:'site',3:'sub-site'}
        for i in range(0,locs.__len__()):
            new_pics[key][ld[i]] = locs[i].strip(' ')

for key in new_pics:
    if('sub-site' in new_pics[key]):
        pass
    else:
        new_pics[key]['sub-site'] = None

from xdict.jprint import print_j_str

def get_printed_str(obj,with_color=1):
    s = obj.__str__()
    pls = print_j_str(s,with_color=with_color)
    ps = ''
    for n in pls:
        ps = ''.join((ps,pls[n],'\n'))
    return(ps)


for key in new_pics:
    new_pics[key]['sci-family'] = None
    if(new_pics[key]['sci-name'] == None):
        pass
    else:
        new_pics[key]['sci-family'] = new_pics[key]['sci-name'].split(' ')[-1]

pics = new_pics

for key in pics:
    pics[key]['image-dir'] = maindir+'PICS/'+ pics[key]['picid'].__str__() + '.' + pics[key]['image-type']
######################################

exact_dir = ''.join((maindir,'INFOS/pics.info'))
nvft.write_to_file(fn=exact_dir,content=json.dumps(pics),op='w+')

exact_dir = ''.join((maindir,'INFOS/lines.info'))
nvft.write_to_file(fn=exact_dir,content='',op='w+')

for key in pics:
    pic=pics[key]
    nvft.write_to_file(fn=exact_dir,content=json.dumps(pic),op='a+')
    nvft.write_to_file(fn=exact_dir,content='\n',op='a+')

exact_dir = ''.join((maindir,'INFOS/paintedlines.info'))
nvft.write_to_file(fn=exact_dir,content='',op='w+')

for key in pics:
    pic=pics[key]
    nvft.write_to_file(fn=exact_dir,content=get_printed_str(pic,with_color=0),op='a+')
    nvft.write_to_file(fn=exact_dir,content='\n',op='a+')
########################################################################################3
