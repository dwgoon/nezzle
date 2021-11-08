from os.path import dirname
from os.path import join as pjoin

__author__ = "Daewon Lee"
__copyright__ = "Copyright 2016-2021, Daewon Lee, All Rights Reserved."
__credits__ = ["Daewon Lee",]
__license__ = "MIT"
__maintainer__ = "Daewon Lee (daewon4you@gmail.com)"
__email__ = "daewon4you@gmail.com"
__status__ = "Prototype"

with open(pjoin(dirname(__file__), "VERSION"), "rt") as fin:
    __version__ = fin.read().strip()


from nezzle.fileio import read_sif
from nezzle.fileio import write_sif

from nezzle.fileio import read_json
from nezzle.fileio import write_json

from nezzle.fileio import read_network
from nezzle.fileio import write_network

from nezzle.convert import to_graphics
from nezzle.convert import to_networkx