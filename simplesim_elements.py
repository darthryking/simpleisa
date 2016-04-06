"""

simplesim_elements.py
By Ryan Lam

Defines all the hardware elements required to simulate the datapath.

"""

import math
import itertools

from constants import ALUOp


class Wire(object):
    def __init__(self, width, init=None):
        self.init = init
        
        self.width = width
        self.receiverCallbacks = []
        
        self.reset()
        
    def reset(self):
        self.value = self.init
        
    def register_callback(self, callback):
        self.receiverCallbacks.append(callback)
        
    def set_value(self, value):
        if value is not None:
            value %= (2 ** self.width)
            
        if value != self.value:
            self.value = value
            
            for callback in self.receiverCallbacks:
                callback(value)
                
                
class Element(object):
    class State(object):
        pass
        
    _allElements = []
    
    def __new__(cls, *args, **kwargs):
        elem = super(Element, cls).__new__(cls, *args, **kwargs)
        cls._allElements.append(elem)
        return elem
        
    def __init__(self):
        pass
        
    def reset(self):
        self.state = self.State()
        self.next = self.State()
        
    def start_cycle(self):
        pass
        
    def transition(self):
        self.state = self.next
        self.next = self.State()
        
    def post_transition(self):
        pass
        
    @classmethod
    def reset_all(cls):
        for element in cls._allElements:
            element.reset()
            
    @classmethod
    def start_cycle_all(cls):
        for element in cls._allElements:
            element.start_cycle()
            
    @classmethod
    def transition_all(cls):
        for element in cls._allElements:
            element.transition()
            
    @classmethod
    def post_transition_all(cls):
        for element in cls._allElements:
            element.post_transition()
            
    @classmethod
    def simulate_datapath(cls):
        cls.reset_all()
        
        print "\n******* Simulation Started! *******"
        
        for cycle in itertools.count():
            cls.start_cycle_all()
            
            print "\n======= Cycle {} =======".format(cycle)
            
            cls.transition_all()
            cls.post_transition_all()
            
        assert False
        
        
class OrGate(Element):
    def __init__(self, numInputs, width, *args):
        assert numInputs >= 2
        assert len(args) == numInputs + 1
        assert all(e.width == width for e in args)
        
        super(OrGate, self).__init__()
        
        self.width = width
        self.numInputs = numInputs
        
        self.inputs = args[:-1]
        
        for input in self.inputs:
            input.register_callback(self.update)
            
        self.output = args[-1]
        
    def update(self, value):
        output = 0
        for input in self.inputs:
            value = input.value
            
            if value is None:
                output = None
                break
            else:
                output |= input.value
                
        self.output.set_value(output)
        
    def reset(self):
        super(OrGate, self).reset()
        self.output.reset()
        
        
class Mux(Element):
    def __init__(self, numInputs, width, inputSel, *args):
        assert len(args) == numInputs + 1
        assert inputSel.width == bits_required(numInputs)
        assert all(e.width == width for e in args)
        
        super(Mux, self).__init__()
        
        self.width = width
        self.numInputs = numInputs
        
        self.inputs = args[:-1]
        self.inputSel = inputSel
        
        for input in self.inputs:
            input.register_callback(self.update)
            
        inputSel.register_callback(self.update)
        
        self.output = args[-1]
        
    def update(self, value):
        sel = self.inputSel.value
        
        if sel is None:
            self.output.set_value(None)
        else:
            self.output.set_value(self.inputs[sel].value)
            
    def reset(self):
        super(Mux, self).reset()
        self.output.reset()
        
        
class Register(Element):
    def __init__(self, width, inputD, inputEn, outputQ):
        assert inputD.width == width
        assert inputEn.width == 1
        assert outputQ.width == width
        
        super(Register, self).__init__()
        
        self.width = width
        
        self.inputD = inputD
        self.inputEn = inputEn
        
        inputD.register_callback(self.update)
        inputEn.register_callback(self.update)
        
        self.outputQ = outputQ
        
    def start_cycle(self):
        self.update(None)
        self.outputQ.set_value(self.state.value)
        
    def update(self, value):
        inputEn = self.inputEn.value
        
        if inputEn is None:
            self.next.value = None
        elif inputEn:
            self.next.value = self.inputD.value
        else:
            self.next.value = self.state.value
            
    def reset(self):
        super(Register, self).reset()
        
        self.state.value = 0
        self.next.value = 0
        
        self.outputQ.reset()
        
    def transition(self):
        super(Register, self).transition()
        self.next.value = 0
        
        
class RegFile(Element):
    def __init__(self,
            inputSel, inputIn, inputWriteEn,
            outputA, outputB):
            
        assert inputSel.width == 8
        assert inputIn.width == 8
        assert inputWriteEn.width == 1
        assert outputA.width == 8
        assert outputB.width == 8
        
        super(RegFile, self).__init__()
        
        self.inputSel = inputSel
        self.inputIn = inputIn
        self.inputWriteEn = inputWriteEn
        
        inputSel.register_callback(self.update)
        inputIn.register_callback(self.update)
        inputWriteEn.register_callback(self.update)
        
        self.outputA = outputA
        self.outputB = outputB
        
    def update(self, value):
        sel = self.inputSel.value
        
        if sel is None:
            self.outputA.set_value(None)
            self.outputB.set_value(None)
            return
            
        selA = (sel >> 4) & 0xF
        selB = sel & 0xF
        
        if self.inputWriteEn.value is None:
            self.next.regs[selA] = None
        elif self.inputWriteEn.value:
            self.next.regs[selA] = self.inputIn.value
        else:
            self.next.regs[selA] = self.state.regs[selA]
            
        self.outputA.set_value(self.state.regs[selA])
        self.outputB.set_value(self.state.regs[selB])
        
    def reset(self):
        super(RegFile, self).reset()
        
        self.state.regs = [0] * 16
        self.next.regs = [0] * 16
        
        self.outputA.reset()
        self.outputB.reset()
        
    def transition(self):
        super(RegFile, self).transition()
        self.next.regs = self.state.regs[:]
        
        
class ALU(Element):
    def __init__(self, inputA, inputB, inputOp, outputFlags, output):
        assert inputA.width == 8
        assert inputB.width == 8
        assert inputOp.width == bits_required(ALUOp.NUM_ALU_OPS)
        assert outputFlags.width == 4
        assert output.width == 8
        
        super(ALU, self).__init__()
        
        self.inputA = inputA
        self.inputB = inputB
        self.inputOp = inputOp
        
        inputA.register_callback(self.update)
        inputB.register_callback(self.update)
        inputOp.register_callback(self.update)
        
        self.outputFlags = outputFlags
        self.output = output
        
    def update(self, value):
        op = self.inputOp.value
        
        a = self.inputA.value
        b = self.inputB.value
        
        class Flags:
            zero = False
            carry = False
            overflow = False
            negative = False
            
            @classmethod
            def update(cls, op, a, result):
                if a is not None:
                    a &= 0xFF
                    
                if result is not None:
                    result &= 0xFF
                    
                if result is None:
                    cls.zero = None
                else:
                    cls.zero = (result == 0)
                    
                if a is None:
                    aSign = None
                else:
                    aSign = a & 0x80
                    
                if result is None:
                    rSign = None
                else:
                    rSign = result & 0x80
                    
                if op == ALUOp.ADD:
                    if None in (aSign, rSign):
                        cls.carry = None
                        cls.overflow = None
                    elif aSign != rSign:
                        cls.carry = (result < a)
                        cls.overflow = (result > a)
                        
                elif op == ALUOp.SUB:
                    if None in (aSign, rSign):
                        cls.carry = None
                        cls.overflow = None
                    elif aSign != rSign:
                        cls.carry = (result > a)
                        cls.overflow = (result < a)
                        
                if rSign is None:
                    cls.negative = None
                else:
                    cls.negative = bool(rSign)
                    
        if op is None:
            output = None
            
        elif op == ALUOp.PASS_A:
            output = a
            
        elif op == ALUOp.PASS_B:
            output = b
            
        elif op == ALUOp.NEG_A:
            if a is None:
                output = None
            else:
                output = -a
                
        elif op == ALUOp.BCM_A:
            if a is None:
                output = None
            else:
                output = ~a
                
        elif op == ALUOp.USR_A:
            if a is None:
                output = None
            else:
                output = ((a & 0xFF) >> 1) & ~0x80
                
        elif op == ALUOp.SSR_A:
            if a is None:
                output = None
            else:
                output = ((a & 0xFF) >> 1) | (a & 0x80)
                
        elif op == ALUOp.USL_A:
            if a is None:
                output = None
            else:
                output = a << 1
                
        elif op == ALUOp.ADD:
            if None in (a, b):
                output = None
            else:
                output = a + b
                
        elif op == ALUOp.SUB:
            if None in (a, b):
                output = None
            else:
                output = a - b
                
        elif op == ALUOp.AND:
            if None in (a, b):
                output = None
            else:
                output = a & b
                
        elif op == ALUOp.OR:
            if None in (a, b):
                output = None
            else:
                output = a | b
                
        else:
            assert False
            
        Flags.update(op, a, output)
        
        if None in (Flags.zero, Flags.carry, Flags.overflow, Flags.negative):
            flags = None
        else:
            flags = (
                (int(Flags.zero) << 3) | 
                (int(Flags.carry) << 2) |
                (int(Flags.overflow) << 1) |
                int(Flags.negative)
            )
            
        self.outputFlags.set_value(flags)
        self.output.set_value(output)
        
    def reset(self):
        super(ALU, self).reset()
        
        self.outputFlags.reset()
        self.output.reset()
        
        
class Memory(Element):
    def __init__(self, size, inputAddr, inputWriteEn, inputData, outputData):
        assert inputAddr.width == bits_required(size)
        assert inputWriteEn.width == 1
        assert inputData.width == 8
        assert outputData.width == 8
        
        super(Memory, self).__init__()
        
        self.defaultImage = '\x00' * size
        
        self.size = size
        
        self.inputAddr = inputAddr
        self.inputWriteEn = inputWriteEn
        self.inputData = inputData
        
        inputAddr.register_callback(self.update)
        inputWriteEn.register_callback(self.update)
        inputData.register_callback(self.update)
        
        self.outputData = outputData
        
    def load_bytes(self, bytes):
        assert len(bytes) == self.size
        assert isinstance(bytes, str)
        
        self.defaultImage = bytes
        
        self.reset()
        
    def update(self, value):
        writeEn = self.inputWriteEn.value
        addr = self.inputAddr.value
        
        if addr is None:
            if writeEn or writeEn is None:
                self.next.mem = [None] * self.size
            else:
                self.next.mem = self.state.mem[:]
                
            self.outputData.set_value(None)
            
        else:
            if writeEn is None:
                self.next.mem[addr] = None
            elif writeEn:
                self.next.mem[addr] = self.inputData.value
            else:
                self.next.mem[addr] = self.state.mem[addr]
                
            self.outputData.set_value(self.state.mem[addr])
            
    def reset(self):
        super(Memory, self).reset()
        
        self.state.mem = [ord(b) for b in self.defaultImage]
        self.next.mem = self.state.mem[:]
        
        self.outputData.reset()
        
    def transition(self):
        super(Memory, self).transition()
        self.next.mem = self.state.mem[:]
        
        
def bits_required(elems):
    return int(math.ceil(math.log(elems, 2)))
    
    