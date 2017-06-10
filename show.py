import json
import sys
from xdict.jprint import pobj

fd = open('./INFOS/pics.info','r')
pi = fd.read()
pics = json.loads(pi)
fd.close()

picid = sys.argv[2]
pobj(pics[picid])


