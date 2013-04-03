from distutils.core import setup
from py2exe.build_exe import py2exe

setup(
    windows=[{
       'script': 'main.pyw',
       'dest_base': 'screengif'
    }]
)
