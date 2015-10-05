"""

simplesim.py
By Ryan Lam

A simulator for a very simple ISA that I made up. Unlike the VM, this actually 
simulates the hardware involved with running the assembly code.

TODO: Implement this.

"""

import sys


def main(argv):
    try:
        filePath = argv[1]
    except IndexError:
        return error("Must provide a hex file!")
        
    return 0
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    