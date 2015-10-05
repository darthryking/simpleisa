import sys

FROZEN = getattr(sys, 'frozen', False)

class Op:
    """ Namespace for instruction opcodes. """
    
    # Misc
    NOP = 0x00
    END = 0xFF
    
    # Data Manipulation
    MOV = 0xD0
    STR = 0xD1
    LDR = 0xD2
    LDC = 0xD3
    
    # Arithmetic
    INC = 0xA0
    DEC = 0xA1
    NEG = 0xA2
    BCM = 0xA3
    ADD = 0xA4
    SUB = 0xA5
    AND = 0xA6
    OR  = 0xA7
    CMP = 0xA8
    
    # Jumps
    JMP = 0xB0
    JLT = 0xB1
    JGT = 0xB2
    JUL = 0xB3
    JUG = 0xB4
    JEQ = 0xB5
    