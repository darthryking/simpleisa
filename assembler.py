"""

assembler.py
By Ryan Lam

An assembler for a very simple assembly language that I made up.

"""

import os
import sys

from constants import FROZEN, Op, Instr

__version__ = '0.0.0'

HEADER = "******* SIMPLE-ISA Assembler *******\n"

if FROZEN:
    HERE = os.path.dirname(sys.executable)
else:
    HERE = os.path.dirname(os.path.abspath(__file__))
    
    
class AssemblerError(Exception):
    """ The assembler can't assemble the given code. """
    pass
    
    
class IllegalToken(AssemblerError):
    """ There's a bad token in the given code. """
    
    def __str__(self):
        return "Illegal token: '{}'".format(self.message)
        
        
def error(msg):
    """ Something screwed up. :( """
    sys.stderr.write("ERROR: {}\n".format(msg))
    raw_input("\nPress [ENTER] to continue...")
    return 1
    
    
def tokenize(data):
    """ Returns an iterator over all the language tokens in the given assembly 
    language data.
    
    """
    
    for line in data.split('\n'):
        for item in line.split(';', 1)[0].strip().split():
            yield item
            
            
def hex_from_int(n):
    """ Gives the 2-digit hexadecimal representation of an integer. """
    return '0x{:0>2}'.format(hex(n)[2:].upper())
    
    
def hex_from_tokens(tokens):
    """ Converts a stream of tokens into a human-readable whitespace-delimited 
    hex string.
    
    """
    
    tokens = iter(tokens)
    
    # Maps label names to addresses
    labelDict = {}
    
    # Maps label names to a list of their occurrences in the result list.
    unknownLabelDict = {}
    
    result = []
    i = 0           # Index of the current memory location.
    
    def get_register_num(register):
        """ Extracts the register number from a register token. """
        return int(register[1:])
        
    def is_register(register):
        """ Determines whether the given token is a register token. """
        
        if not register.startswith('r'):
            return False
            
        try:
            registerNumber = get_register_num(register)
        except ValueError:
            return False
            
        if not (0 <= registerNumber < 16):
            return False
            
        return True
        
    def get_constant(token):
        """ Helper that interprets the given token as a constant number, and 
        adds it to the results list as such.
        
        If the token is a label reference, this helper function either adds a 
        placeholder value to the results list and records its location, or, if 
        the label is known, translates the label into its respective constant 
        value and adds that constant to the results list.
        
        """
        
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
            address = i
            labelDict[label] = address
            
            # Fill in all prior placeholder references to this label, if any.
            if label in unknownLabelDict:
                for index in unknownLabelDict[label]:
                    result[index] = '{}\n'.format(hex_from_int(address))
                    
                del unknownLabelDict[label]
                
        # Instruction
        elif token in Instr.ALL:
            value = Instr.ALL[token]
            result.append(hex_from_int(value))
            i += 1
            
            if token in Instr.REG:
                register = next(tokens)
                
                if not is_register(register):
                    raise IllegalToken(register)
                    
                regNum = get_register_num(register)
                
                result.append('0x{:1x}0\n'.format(regNum))
                i += 1
                
            elif token in Instr.REG_REG:
                register1 = next(tokens)
                register2 = next(tokens)
                
                if not is_register(register1):
                    raise IllegalToken(register1)
                    
                if not is_register(register2):
                    raise IllegalToken(register2)
                    
                upper = get_register_num(register1)
                lower = get_register_num(register2)
                
                result.append('0x{:1x}{:1x}\n'.format(upper, lower))
                i += 1
                
            elif token in Instr.REG_CONST:
                register = next(tokens)
                
                if not is_register(register):
                    raise IllegalToken(register)
                    
                regNum = get_register_num(register)
                
                result.append('0x{:1x}0'.format(regNum))
                i += 1
                
                get_constant(next(tokens))
                i += 1
                
            elif token in Instr.CONST:
                get_constant(next(tokens))
                i += 1
                
            else:
                result[-1] += '\n'
                
        # Assume everything else to be a constant or label reference.
        else:
            get_constant(token)
            i += 1
            
    if unknownLabelDict:
        raise Exception('Missing labels: {}'.format(unknownLabelDict.keys()))
        
    if len(result) > 256:
        raise AssemblerError(
                "Program too large for memory! ({}/256 bytes)"
                    .format(len(result))
            )
            
    return ' '.join(result).replace('\n ', '\n').strip()
    
    
def bytes_from_hex(hexcode):
    """ Given a valid string of whitespace-delimited hexadecimal numbers, 
    returns those hex numbers translated into byte string form.
    
    """
    
    return ''.join(chr(int(code, 16)) for code in hexcode.split())
    
    
def pad_program(bytecode):
    """ Returns bytecode padded with zeros to a length of 256. """
    return bytecode + '\x00' * (256 - len(bytecode))
    
    
def get_filename(filePath):
    """ Given the path to a file, gives the filename without its extension.
    """
    return os.path.basename(filePath).split('.', 1)[0]
    
    
def main(argv):
    print HEADER
    
    try:
        filePath = argv[1]
    except IndexError:
        return error("Must provide a source file!")
        
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
        