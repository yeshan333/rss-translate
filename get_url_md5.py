# -*- coding: utf-8 -*-

import hashlib
import sys

def calculate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()

if __name__ == '__main__':
    url = sys.argv[1]
    print(calculate_md5(url))
