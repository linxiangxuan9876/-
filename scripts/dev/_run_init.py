import sys
sys.path.insert(0, r'd:\Trae-项目\门店知识库\lib')
sys.path.insert(0, r'd:\Trae-项目\门店知识库')

import os
os.chdir(r'd:\Trae-项目\门店知识库')

exec(open(r'd:\Trae-项目\门店知识库\init_db.py', encoding='utf-8').read())
