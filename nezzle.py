__author__ = "Daewon Lee"
__copyright__ = "Copyright 2021, Daewon Lee"
__credits__ = ["Daewon Lee", ]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Daewon Lee (daewon4you@gmail.com)"
__email__ = "daewon4you@gmail.com"
__status__ = "Production"



import cgitb
cgitb.enable(format='text')

import os
import argparse

from nezzle.app import main

if __name__ == '__main__':

    argparser = argparse.ArgumentParser(description="Nezzle arguments for CUI execution")
    argparser.add_argument('-fc', '--fpath-code',
                           action='store',
                           dest='fpath_code',
                           default=None,
                           help="Designate the absolute file path of a source code file.")
    args = argparser.parse_args()

    main(args)
