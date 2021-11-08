import cgitb
cgitb.enable(format='text')

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
