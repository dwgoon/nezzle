# -*- coding: utf-8 -*-

#from __future__ import division, absolute_import, print_function

import os
import os.path as osp
          
from setuptools import setup, find_packages


# deps = ['qtpy',
        # 'ipython',
        # 'qtconsole',
        # 'numpy',
        # 'networkx',
        # 'matplotlib',
        # 'seaborn',]

scrps = []
if os.name == 'nt':
    fpath_script = osp.join('scripts', 'nezzle.bat')
else:
    fpath_script = osp.join('scripts', 'nezzle')

scrps.append(fpath_script)

        
setup (
    name='nezzle',
    description='Network Visualization using both GUI and programming',
    url='',
    version='0.0.1',
    author='Daewon Lee',
    author_email='daewon4you@gmail.com',
    license='',
    packages=find_packages(),
    package_data={'': ['*.ui', '*.sif', '*.json'], },
    #install_requires=deps,
    scripts=scrps,
)
