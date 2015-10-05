"""

simplevm.py
By Ryan Lam

A virtual machine for a very simple assembly language that I made up.

Unlike the simulator, this does not simulate the actual hardware or 
microarchitecture involved in running the assembly language.

"""

import sys

from constants import Op


class InvalidFile(Exception):
    pass
    
    
class RegFile(list):
    def __setitem__(self, index, item):
        super(RegFile, self).__setitem__(index, item & 0xFF)
        
        
def error(msg):
    """ Something screwed up. :( """
    sys.stderr.write("ERROR: {}\n".format(msg))
    raw_input("\nPress [ENTER] to continue...")
    return 1
    
    
def load_memory(filePath):
    if filePath.endswith('.hex'):
        with open(filePath, 'r') as f:
            data = f.read()
            
        memory = bytearray(int(c, 16) for c in data.split())
        
        while len(memory) < 256:
            memory.append(0)
            
        if len(memory) != 256:
            raise InvalidFile("Invalid *.hex file!")
            
    elif filePath.endswith('.bin'):
        with open(filePath, 'rb') as f:
            data = f.read()
            
        memory = bytearray(data)
        
        if len(memory) != 256:
            raise InvalidFile("Invalid *.bin file!")
            
    else:
        raise InvalidFile("Must provide a *.hex or *.bin file!")
        
    return memory
    
    
def main(argv):
    try:
        filePath = argv[1]
    except IndexError:
        return error("Must provide a *.hex or *.bin file!")
        
    try:
        memory = load_memory(filePath)
    except InvalidFile as e:
        return error(str(e))
        
    registers = [0] * 8
    pc = 0
    
    class Flags:
        zero = False
        carry = False
        overflow = False
        negative = False
        
        @classmethod
        def update(cls, op, a, result):
            a &= 0xFF
            result &= 0xFF
            
            cls.zero = (result == 0)
            
            aSign = a & 0x80
            rSign = result & 0x80
            
            if aSign != rSign:
                if op in (Op.INC, Op.ADD):
                    cls.carry = (result < a)
                    cls.overflow = (result > a)
                    
                elif op in (Op.DEC, Op.SUB, Op.CMP):
                    cls.carry = (result > a)
                    cls.overflow = (result < a)
                    
            cls.negative = bool(rSign)
            
    def get_regs(regs):
        return ((regs >> 4) & 0xF, regs & 0xF)
        
    while 1:
        op = memory[pc]
        
        print "PC: {}\tInstruction: {}\tRegisters: {}".format(
                pc, hex(op), registers
            )
            
        if op == Op.NOP:
            pc += 1
            
        elif op == Op.END:
            print "Program halted!"
            break
            
        elif op == Op.MOV:
            regA, regB = get_regs(memory[pc + 1])
            registers[regA] = registers[regB]
            pc += 2
            
        elif op == Op.STR:
            reg, _ = get_regs(memory[pc + 1])
            addr = memory[pc + 2]
            
            memory[addr] = registers[reg]
            
            pc += 3
            
        elif op == Op.LDR:
            reg, _ = get_regs(memory[pc + 1])
            addr = memory[pc + 2]
            
            registers[reg] = memory[addr]
            
            pc += 3
            
        elif op == Op.LDC:
            reg, _ = get_regs(memory[pc + 1])
            const = memory[pc + 2]
            
            registers[reg] = const
            
            pc += 3
            
        elif op == Op.INC:
            reg, _ = get_regs(memory[pc + 1])
            
            a = registers[reg]
            result = a + 1
            registers[reg] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.DEC:
            reg, _ = get_regs(memory[pc + 1])
            
            a = registers[reg]
            result = a - 1
            registers[reg] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.NEG:
            reg, _ = get_regs(memory[pc + 1])
            
            a = registers[reg]
            result = -a
            registers[reg] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.BCM:
            reg, _ = get_regs(memory[pc + 1])
            
            a = registers[reg]
            result = ~a
            registers[reg] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.ADD:
            regA, regB = get_regs(memory[pc + 1])
            
            a = registers[regA]
            result = a + registers[regB]
            registers[regA] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.SUB:
            regA, regB = get_regs(memory[pc + 1])
            
            a = registers[regA]
            result = a - registers[regB]
            registers[regA] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.AND:
            regA, regB = get_regs(memory[pc + 1])
            
            a = registers[regA]
            result = a & registers[regB]
            registers[regA] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.OR:
            regA, regB = get_regs(memory[pc + 1])
            
            a = registers[regA]
            result = a | registers[regB]
            registers[regA] = result
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.CMP:
            regA, regB = get_regs(memory[pc + 1])
            
            a = registers[regA]
            result = a - registers[regB]
            
            Flags.update(op, a, result)
            
            pc += 2
            
        elif op == Op.JMP:
            pc = memory[pc + 1]
            
        elif op == Op.JLT:
            if Flags.negative != Flags.overflow:
                pc = memory[pc + 1]
            else:
                pc += 2
                
        elif op == Op.JGT:
            if not Flags.zero and Flags.negative == Flags.overflow:
                pc = memory[pc + 1]
            else:
                pc += 2
                
        elif op == Op.JUL:
            if Flags.carry:
                pc = memory[pc + 1]
            else:
                pc += 2
                
        elif op == Op.JUG:
            if not Flags.carry and not Flags.zero:
                pc = memory[pc + 1]
            else:
                pc += 2
                
        elif op == Op.JEQ:
            if Flags.zero:
                pc = memory[pc + 1]
            else:
                pc += 2
                
        pc %= 256
        
    print "Done!"
    
    while 1:
        addrIn = raw_input("Examine address: ")
        
        if addrIn.lower() == 'done':
            break
            
        addr = int(addrIn, 16)
        
        print "Contents of {}: {}".format(hex(addr), hex(memory[addr]))
        
    return 0
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    