# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s 

Authenticated by Sherk
Any question please refer to:
    sherkfung@gmail.com
"""

from sqlalchemy import create_engine
from my2sql import Mysql

# connection to local postgresql
args = {}
args['engine'] = 'p'
args['dbname'] = 'ppa'
args['user'] = 'root'
args['password'] = 'root'
args['host'] = '127.0.0.1'
args['port'] = 5432

db = create_engine(
    'postgresql://%s:%s@%s:%s/%s' % 
        (args['user'], args['password'], args['host'], args['port'], args['dbname']),
    encoding='utf8',
    echo=False,
    pool_recycle=5
)

