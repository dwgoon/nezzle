import os
import os.path as osp
from setuptools import setup, find_packages

with open('README.md') as fin:
    lines = []
    for line in fin:
        if line.startswith("<"):
            continue 
        
        if "## Examples" in line:
            break
        
        lines.append(line)
        
    long_description = "".join(lines)


with open("nezzle/VERSION", "rt") as fin:
    version = fin.read().strip()

    version = version + "b"
    print("[VERSION]", version)

scripts = []
if os.name == 'nt':
    fpath_script = osp.join('scripts', 'nezzle.bat')
else:
    fpath_script = osp.join('scripts', 'nezzle')

scripts.append(fpath_script)


setup (
    name="nezzle",
    version=version,
    description="Nezzle: a programmable and interactive "
                "network visualization software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwgoon/nezzle",
    author="Daewon Lee",
    author_email="daewon4you@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        "pyqt5>=5",
        "qtpy>=1.5.0",
        "ipython>=7.6.0",
        "qtconsole>=5.2.0",
        "numpy>=1.18",
        "networkx>=2"
    ],
    packages=find_packages(),
    package_data={'': ["VERSION", "*.ui", "*.sif", "*.json"], },
    scripts=scripts,
    entry_points = {
        'gui_scripts': [
            'nezzle = nezzle.app:main'
        ],
    }
)
