import sys
sys.path.insert(0, r'd:\Trae-项目\门店知识库\lib')
sys.path.insert(0, r'd:\Trae-项目\门店知识库')

import os
os.chdir(r'd:\Trae-项目\门店知识库')

import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
