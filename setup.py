import os
import os.path as osp
from setuptools import setup, find_packages


scripts = []
if os.name == 'nt':
    fpath_script = osp.join('scripts', 'nezzle.bat')
else:
    fpath_script = osp.join('scripts', 'nezzle')

scripts.append(fpath_script)


setup (
    name='nezzle',
    description="Nezzle: a programmable and interactive visualization software",
    url='',
    version='0.0.1',
    author='Daewon Lee',
    author_email='daewon4you@gmail.com',
    license='',
    packages=find_packages(),
    package_data={'': ['*.ui', '*.sif', '*.json'], },
    scripts=scripts,
)
