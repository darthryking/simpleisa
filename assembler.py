"""

assembler.py
By Ryan Lam

An assembler for a very simple assembly language that I made up.

"""

import os
import sys

__version__ = '0.0.0'

HEADER = "******* SIMPLE-ISA Assembler *******\n"

HERE = os.path.dirname(os.path.abspath(__file__))

INSTRUCTIONS_DICT = {
    # Misc
    'NOP'   :   0x00,
    'END'   :   0xFF,
    
    # Data Manipulation
    'MOV'   :   0xD0,
    'STR'   :   0xD1,
    'LDR'   :   0xD2,
    'LDC'   :   0xD3,
    
    # Arithmetic
    'INC'   :   0xA0,
    'DEC'   :   0xA1,
    'NEG'   :   0xA2,
    'ADD'   :   0xA3,
    'SUB'   :   0xA4,
    'AND'   :   0xA5,
    'OR'    :   0xA6,
    'CMP'   :   0xA7,
    
    # Jumps
    'JMP'   :   0xB0,
    'JLT'   :   0xB1,
    'JGT'   :   0xB2,
    'JUL'   :   0xB3,
    'JUG'   :   0xB4,
    'JEQ'   :   0xB5,
    
}

SINGLE_REG_INSTRUCTIONS = set(
        (
            'INC',
            'DEC',
            'NEG',
        )
    )
    
DOUBLE_REG_INSTRUCTIONS = set(
        (
            'MOV',
            'ADD',
            'SUB',
            'AND',
            'OR',
            'CMP',
        )
    )
    
REG_CONSTANT_INSTRUCTIONS = set(
        (
            'STR',
            'LDR',
            'LDC',
        )
    )
    
CONSTANT_INSTRUCTIONS = set(
        (
            'JMP',
            'JLT',
            'JGT',
            'JUL',
            'JUG',
            'JEQ',
        )
    )
    
    
class AssemblerError(Exception):
    pass
    
    
class IllegalToken(AssemblerError):
    def __str__(self):
        return "Illegal token: '{}'".format(self.message)
        
        
def error(msg):
    sys.stderr.write("ERROR: {}\n".format(msg))
    raw_input("\nPress [ENTER] to continue...")
    return 1
    
    
def tokenize(data):
    for line in data.split('\n'):
        for item in line.split(';', 1)[0].strip().split():
            yield item
            
            
def hex_from_int(n):
    return '0x{:0>2}'.format(hex(n)[2:].upper())
    
    
def hex_from_tokens(tokens):
    """ Converts a stream of tokens into a human-readable hex string. """
    
    tokens = iter(tokens)
    
    # Maps label names to addresses
    labelDict = {}
    
    # Maps label names to a list of their occurrences in the result list.
    unknownLabelDict = {}
    
    result = []
    i = 0
    
    def get_register_num(register):
        return int(register[1:])
        
    def is_register(register):
        if not register.startswith('r'):
            return False
            
        try:
            registerNumber = get_register_num(register)
        except ValueError:
            return False
            
        if not (0 <= registerNumber < 8):
            return False
            
        return True
        
    def get_constant(token):
        if token.startswith('0x'):
            try:
                value = int(token, 16)
            except ValueError:
                raise IllegalToken(token)
                
            hexValue = hex_from_int(value)
            
        else:
            try:
                value = labelDict[token]
                
            except KeyError:
                try:
                    unknownLabelDict[token].append(i)
                except KeyError:
                    unknownLabelDict[token] = [i]
                    
                hexValue = '0x??'
                
            else:
                hexValue = hex_from_int(value)
                
        result.append('{}\n'.format(hexValue))
        
    for token in tokens:
        
        # Label
        if token.endswith(':') and not token.startswith('0x'):
            label = token[:-1]
            address = i % 256
            labelDict[label] = address
            
            if label in unknownLabelDict:
                for index in unknownLabelDict[label]:
                    result[index] = '{}\n'.format(hex_from_int(address))
                    
                del unknownLabelDict[label]
                
        # Constant
        elif token.startswith('0x'):
            get_constant(token)
            i += 1
            
        # Instruction
        elif token in INSTRUCTIONS_DICT:
            value = INSTRUCTIONS_DICT[token]
            result.append(hex_from_int(value))
            i += 1
            
            if token in SINGLE_REG_INSTRUCTIONS:
                register = next(tokens)
                
                if not is_register(register):
                    raise IllegalToken(register)
                    
                regNum = get_register_num(register)
                
                result.append('0x{}0\n'.format(regNum))
                i += 1
                
            elif token in DOUBLE_REG_INSTRUCTIONS:
                register1 = next(tokens)
                register2 = next(tokens)
                
                if not is_register(register1):
                    raise IllegalToken(register1)
                    
                if not is_register(register2):
                    raise IllegalToken(register2)
                    
                upper = get_register_num(register1)
                lower = get_register_num(register2)
                
                result.append('0x{}{}\n'.format(upper, lower))
                i += 1
                
            elif token in REG_CONSTANT_INSTRUCTIONS:
                register = next(tokens)
                
                if not is_register(register):
                    raise IllegalToken(register)
                    
                regNum = get_register_num(register)
                
                result.append('0x{}0'.format(regNum))
                get_constant(next(tokens))
                
                i += 2
                
            elif token in CONSTANT_INSTRUCTIONS:
                get_constant(next(tokens))
                i += 1
                
            else:
                result[-1] += '\n'
                
        # Illegal token
        else:
            raise IllegalToken(token)
            
    if unknownLabelDict:
        raise Execption('Missing labels: {}'.format(unknownLabelDict.keys()))
        
    if len(result) > 256:
        raise AssemblerError(
                "Program too large for memory! ({}/256 bytes)"
                    .format(len(result))
            )
            
    return ' '.join(result).replace('\n ', '\n').strip()
    
    
def bytes_from_hex(hexcode):
    return ''.join(chr(int(code, 16)) for code in hexcode.split())
    
    
def pad_program(bytecode):
    return bytecode + '\x00' * (256 - len(bytecode))
    
    
def get_filename(filePath):
    return os.path.basename(filePath).split('.', 1)[0]
    
    
def main(argv):
    if len(argv) != 2:
        return error("Must provide at least one file!")
        
    filePath = argv[1]
    
    print HEADER
    
    print "Reading {}...".format(os.path.basename(filePath))
    
    with open(filePath, 'r') as f:
        data = f.read()
        
    tokens = tokenize(data)
    
    print ""
    print "Translating to hex..."
    
    try:
        hexcode = hex_from_tokens(tokens)
    except StopIteration:
        return error("Unexpected end of file!")
        
    print "Translating to binary..."
    bytecode = bytes_from_hex(hexcode)
    
    print "\t* Final program size: {}/256 bytes".format(len(bytecode))
    print ""
    
    # Pad the bytecode with zeros to the maximum memory size.
    print "Padding memory..."
    bytecode = pad_program(bytecode)
    
    print ""
    
    hexfileName = '{}.hex'.format(get_filename(filePath))
    hexfilePath = os.path.join(HERE, hexfileName)
    
    binfilePath = os.path.join(HERE, 'memory.bin')
    
    print "Writing {}...".format(hexfileName)
    with open(hexfilePath, 'w') as f:
        f.write(hexcode)
        
    print "Writing {}...".format('memory.bin')
    with open(binfilePath, 'wb') as f:
        f.write(bytecode)
        
    print ""
    print "Done!"
    raw_input("\nPress [ENTER] to continue...")
    
    return 0
    
    
if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except AssemblerError as e:
        sys.exit(error(str(e)))
        