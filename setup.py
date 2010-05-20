'''
Created on 16 May 2010

@author: David
'''

from distutils.core import setup
import py2exe, sys, os

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
       if os.path.basename(pathname).lower() in ["sdl_ttf.dll"]:
               return 0
       return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

setup(
    console=["__main__.py"],
    zipfile=None
    )
