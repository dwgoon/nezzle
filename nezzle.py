# -*- coding: utf-8 -*-

"""
@author: Daewon Lee (dwl@kaist.ac.kr)
"""

__author__ = "Daewon Lee"
__copyright__ = "Copyright 2016, KAIST SBiE Daewon Lee"
__credits__ = ["Daewon Lee",]
__license__ = "MIT" # GPL, LGPL, MIT, Apache 2.0
__version__ = "0.0.1"
__maintainer__ = "Daewon Lee (daewon4you@gmail.com)"
__email__ = "daewon4you@gmail.com"
__status__ = "Production"


import cgitb
cgitb.enable(format='text')

from nezzle.app import main

if __name__ == '__main__':
    main()
