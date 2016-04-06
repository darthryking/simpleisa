import sys

FROZEN = getattr(sys, 'frozen', False)


class Op:
    """ Namespace for instruction opcodes. """
    
    # Misc
    NOP = 0x00
    END = 0xFF
    
    # Data Manipulation
    MOV = 0xD0
    LDC = 0xD1
    LDM = 0xD2
    STM = 0xD3
    
    # Arithmetic
    INC = 0xA0
    DEC = 0xA1
    NEG = 0xA2
    BCM = 0xA3
    USR = 0xA4
    SSR = 0xA5
    USL = 0xA6
    ADD = 0xA7
    SUB = 0xA8
    AND = 0xA9
    OR  = 0xAA
    CMP = 0xAB
    
    # Jumps
    JMP = 0xB0
    JEQ = 0xB1
    JUL = 0xB2
    JUG = 0xB3
    JSL = 0xB4
    JSG = 0xB5
    
    
class Instr:
    """ Namespace for instruction categories. """
    
    ALL = {
        # Misc
        'NOP'   :   Op.NOP,
        'END'   :   Op.END,
        
        # Data Manipulation
        'MOV'   :   Op.MOV,
        'LDC'   :   Op.LDC,
        'LDM'   :   Op.LDM,
        'STM'   :   Op.STM,
        
        # Arithmetic
        'INC'   :   Op.INC,
        'DEC'   :   Op.DEC,
        'NEG'   :   Op.NEG,
        'BCM'   :   Op.BCM,
        'USR'   :   Op.USR,
        'SSR'   :   Op.SSR,
        'USL'   :   Op.USL,
        'ADD'   :   Op.ADD,
        'SUB'   :   Op.SUB,
        'AND'   :   Op.AND,
        'OR'    :   Op.OR,
        'CMP'   :   Op.CMP,
        
        # Jumps
        'JMP'   :   Op.JMP,
        'JEQ'   :   Op.JEQ,
        'JUL'   :   Op.JUL,
        'JUG'   :   Op.JUG,
        'JSL'   :   Op.JSL,
        'JSG'   :   Op.JSG,
        
    }
    
    
    # Instructions of the form: OP r#
    REG = frozenset(
            (
                'INC',
                'DEC',
                'NEG',
                'BCM',
                'USR',
                'SSR',
                'USL',
                Op.INC,
                Op.DEC,
                Op.NEG,
                Op.BCM,
                Op.USR,
                Op.SSR,
                Op.USL,
            )
        )
        
        
    # Instructions of the form: OP rA rB
    REG_REG = frozenset(
            (
                'MOV',
                'ADD',
                'SUB',
                'AND',
                'OR',
                'CMP',
                'LDM',
                'STM',
                Op.MOV,
                Op.ADD,
                Op.SUB,
                Op.AND,
                Op.OR,
                Op.CMP,
                Op.LDM,
                Op.STM,
            )
        )
        
        
    # Instructions of the form: OP r# 0x##
    REG_CONST = frozenset(
            (
                'LDC',
                Op.LDC,
            )
        )
        
        
    # Instructions of the form: OP 0x##
    CONST = frozenset(
            (
                'JMP',
                'JEQ',
                'JUL',
                'JUG',
                'JSL',
                'JSG',
                Op.JMP,
                Op.JEQ,
                Op.JUL,
                Op.JUG,
                Op.JSL,
                Op.JSG,
            )
        )
        
        
class State:
    HALT = 0x0000
    
    FETCH_0 = 0x00F0
    FETCH_1 = 0x00F1
    FETCH_2 = 0x00F2
    
    DECODE = 0x00D0
    
    MOV_0 = (Op.MOV << 8) | 0x00
    MOV_1 = (Op.MOV << 8) | 0x01
    MOV_2 = (Op.MOV << 8) | 0x02
    MOV_3 = (Op.MOV << 8) | 0x03
    
    LDC_0 = (Op.LDC << 8) | 0x00
    LDC_1 = (Op.LDC << 8) | 0x01
    LDC_2 = (Op.LDC << 8) | 0x02
    LDC_3 = (Op.LDC << 8) | 0x03
    LDC_4 = (Op.LDC << 8) | 0x04
    LDC_5 = (Op.LDC << 8) | 0x05
    
    LDM_0 = (Op.LDM << 8) | 0x00
    LDM_1 = (Op.LDM << 8) | 0x01
    LDM_2 = (Op.LDM << 8) | 0x02
    LDM_3 = (Op.LDM << 8) | 0x03
    LDM_4 = (Op.LDM << 8) | 0x04
    LDM_5 = (Op.LDM << 8) | 0x05
    
    STM_0 = (Op.STM << 8) | 0x00
    STM_1 = (Op.STM << 8) | 0x01
    STM_2 = (Op.STM << 8) | 0x02
    STM_3 = (Op.STM << 8) | 0x03
    STM_4 = (Op.STM << 8) | 0x04
    STM_5 = (Op.STM << 8) | 0x05
    
    INC_0 = (Op.INC << 8) | 0x00
    INC_1 = (Op.INC << 8) | 0x01
    INC_2 = (Op.INC << 8) | 0x02
    INC_3 = (Op.INC << 8) | 0x03
    
    DEC_0 = (Op.DEC << 8) | 0x00
    DEC_1 = (Op.DEC << 8) | 0x01
    DEC_2 = (Op.DEC << 8) | 0x02
    DEC_3 = (Op.DEC << 8) | 0x03
    
    NEG_0 = (Op.NEG << 8) | 0x00
    NEG_1 = (Op.NEG << 8) | 0x01
    NEG_2 = (Op.NEG << 8) | 0x02
    NEG_3 = (Op.NEG << 8) | 0x03
    
    BCM_0 = (Op.BCM << 8) | 0x00
    BCM_1 = (Op.BCM << 8) | 0x01
    BCM_2 = (Op.BCM << 8) | 0x02
    BCM_3 = (Op.BCM << 8) | 0x03
    
    USR_0 = (Op.USR << 8) | 0x00
    USR_1 = (Op.USR << 8) | 0x01
    USR_2 = (Op.USR << 8) | 0x02
    USR_3 = (Op.USR << 8) | 0x03
    
    SSR_0 = (Op.SSR << 8) | 0x00
    SSR_1 = (Op.SSR << 8) | 0x01
    SSR_2 = (Op.SSR << 8) | 0x02
    SSR_3 = (Op.SSR << 8) | 0x03
    
    USL_0 = (Op.USL << 8) | 0x00
    USL_1 = (Op.USL << 8) | 0x01
    USL_2 = (Op.USL << 8) | 0x02
    USL_3 = (Op.USL << 8) | 0x03
    
    ADD_0 = (Op.ADD << 8) | 0x00
    ADD_1 = (Op.ADD << 8) | 0x01
    ADD_2 = (Op.ADD << 8) | 0x02
    ADD_3 = (Op.ADD << 8) | 0x03
    
    SUB_0 = (Op.SUB << 8) | 0x00
    SUB_1 = (Op.SUB << 8) | 0x01
    SUB_2 = (Op.SUB << 8) | 0x02
    SUB_3 = (Op.SUB << 8) | 0x03
    
    AND_0 = (Op.AND << 8) | 0x00
    AND_1 = (Op.AND << 8) | 0x01
    AND_2 = (Op.AND << 8) | 0x02
    AND_3 = (Op.AND << 8) | 0x03
    
    OR_0 = (Op.OR << 8) | 0x00
    OR_1 = (Op.OR << 8) | 0x01
    OR_2 = (Op.OR << 8) | 0x02
    OR_3 = (Op.OR << 8) | 0x03
    
    CMP_0 = (Op.CMP << 8) | 0x00
    CMP_1 = (Op.CMP << 8) | 0x01
    CMP_2 = (Op.CMP << 8) | 0x02
    CMP_3 = (Op.CMP << 8) | 0x03
    
    JMP_0 = (Op.JMP << 8) | 0x00
    JMP_1 = (Op.JMP << 8) | 0x01
    JMP_2 = (Op.JMP << 8) | 0x02
    
    JEQ_0 = (Op.JEQ << 8) | 0x00
    JEQ_1 = (Op.JEQ << 8) | 0x01
    JEQ_2 = (Op.JEQ << 8) | 0x02
    
    JUL_0 = (Op.JUL << 8) | 0x00
    JUL_1 = (Op.JUL << 8) | 0x01
    JUL_2 = (Op.JUL << 8) | 0x02
    
    JUG_0 = (Op.JUG << 8) | 0x00
    JUG_1 = (Op.JUG << 8) | 0x01
    JUG_2 = (Op.JUG << 8) | 0x02
    
    JSL_0 = (Op.JSL << 8) | 0x00
    JSL_1 = (Op.JSL << 8) | 0x01
    JSL_2 = (Op.JSL << 8) | 0x02
    
    JSG_0 = (Op.JSG << 8) | 0x00
    JSG_1 = (Op.JSG << 8) | 0x01
    JSG_2 = (Op.JSG << 8) | 0x02
    
    
class Flags:
    ZERO = 0x1 << 3
    CARRY = 0x1 << 2
    OVERFLOW = 0x1 << 1
    NEGATIVE = 0x1
    
    
class ALUOp:
    PASS_A = 0
    PASS_B = 1
    
    NEG_A = 2
    BCM_A = 3
    
    USR_A = 4
    SSR_A = 5
    USL_A = 6
    
    ADD = 7
    SUB = 8
    AND = 9
    OR = 10
    
    NUM_ALU_OPS = 11
    
    
class ALUSelA:
    REG_A = 0
    PC = 1
    MDR = 2
    
    NUM_ALU_A = 3
    
    
class ALUSelB:
    REG_B = 0
    ONE = 1
    
    NUM_ALU_B = 2
    
    