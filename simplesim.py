"""

simplesim.py
By Ryan Lam

A simulator for a very simple ISA that I made up. Unlike the VM, this actually 
simulates the hardware involved with running the assembly code.

"""

import sys
import pdb

from constants import ALUOp, ALUSelA, ALUSelB

from simplesim_elements import (
    Wire, Element,
    OrGate, Mux,
    Register, RegFile, ALU, Memory,
    bits_required,
)

from simplesim_fsm import Controller


class HaltExecution(Exception):
    def __str__(self):
        return "Program halted!"
        
        
class Debugger(Element):
    def __init__(self,
            regFile,
            inputState, inputHalted,
            inputPC, inputIR, inputMAR, inputMDR,
            inputALUA, inputALUB, inputALUOut, inputALUFlags,
            ):
        super(Debugger, self).__init__()
        
        self.shouldContinue = False
        
        self.regFile = regFile
        self.inputState = inputState
        self.inputHalted = inputHalted
        self.inputPC = inputPC
        self.inputIR = inputIR
        self.inputMAR = inputMAR
        self.inputMDR = inputMDR
        self.inputALUA = inputALUA
        self.inputALUB = inputALUB
        self.inputALUOut = inputALUOut
        self.inputALUFlags = inputALUFlags
        
    def post_transition(self):
        super(Debugger, self).transition()
        
        state = self.inputState.value
        pc = self.inputPC.value
        ir = self.inputIR.value
        mar = self.inputMAR.value
        mdr = self.inputMDR.value
        aluA = self.inputALUA.value
        aluB = self.inputALUB.value
        aluOut = self.inputALUOut.value
        aluFlags = self.inputALUFlags.value
        
        print (
            "State: 0x{:04x} PC: 0x{:02x} IR: 0x{:02x} "
            "MAR: 0x{:02x} MDR: 0x{:02x}"
                .format(
                        state, pc, ir,
                        mar, mdr,
                    )
        )
        
        aluAHex = '0x??' if aluA is None else '0x{:02x}'.format(aluA)
        aluBHex = '0x??' if aluB is None else '0x{:02x}'.format(aluB)
        aluOutHex = '0x??' if aluOut is None else '0x{:02x}'.format(aluOut)
        
        print (
            "ALU A: {} ALU B: {} "
            "ALU Out: {} ALU Flags: {:04b}_b".format(
                    aluAHex, aluBHex,
                    aluOutHex, aluFlags,
                )
        )
        
        for i, value in enumerate(self.regFile.state.regs):
            print "r{}: 0x{:02x}".format(i, value),
            
            if i in (7, 15):
                print ""
                
        if self.inputHalted.value:
            print ""
            raise HaltExecution
            
        if not self.shouldContinue:
            cmd = raw_input()
            
            if cmd == 'b':
                pdb.set_trace()
            elif cmd == 'c':
                self.shouldContinue = True
                
                
def error(msg):
    """ Something screwed up. :( """
    sys.stderr.write("ERROR: {}\n".format(msg))
    raw_input("\nPress [ENTER] to continue...")
    return 1
    
    
def main(argv):
    try:
        filePath = argv[1]
    except IndexError:
        return error("Must provide a *.bin file!")
        
    try:
        with open(filePath, 'rb') as f:
            data = f.read()
    except IOError:
        return error("Coud not open file '{}'!".format(filePath))
        
    controlALUSelA = Wire(bits_required(ALUSelA.NUM_ALU_A))
    controlALUSelB = Wire(bits_required(ALUSelB.NUM_ALU_B))
    controlALUOp = Wire(bits_required(ALUOp.NUM_ALU_OPS))
    aluA = Wire(8)
    aluB = Wire(8)
    aluOp = controlALUOp
    aluFlags = Wire(4)
    aluOut = Wire(8)
    
    controlLdFlags = Wire(1)
    flagsEn = controlLdFlags
    flagsQ = Wire(4)
    
    controlLdPC = Wire(1)
    pcEn = controlLdPC
    pcQ = Wire(8)
    
    controlLdIR = Wire(1)
    irEn = controlLdIR
    irQ = Wire(8)
    
    controlLdReg = Wire(1)
    regWriteEn = controlLdReg
    
    regOutA = Wire(8)
    regOutB = Wire(8)
    
    controlLdMAR = Wire(1)
    marEn = controlLdMAR
    marQ = Wire(8)
    
    controlLdMDR = Wire(1)
    controlMemRead = Wire(1)
    mdrD = Wire(8)
    mdrEn = Wire(1)
    mdrQ = Wire(8)
    
    controlMemWrite = Wire(1)
    memWriteEn = controlMemWrite
    memOut = Wire(8)
    
    signalState = Wire(16)
    signalHalted = Wire(1)
    
    fsm = Controller(
            irQ, flagsQ,
            signalState, signalHalted,
            controlALUSelA, controlALUSelB, controlALUOp, controlLdFlags,
            controlLdPC, controlLdIR, controlLdReg,
            controlLdMAR, controlLdMDR,
            controlMemRead, controlMemWrite,
        )
        
    aluSelA = controlALUSelA
    Mux(3, 8, aluSelA, regOutA, pcQ, mdrQ, aluA)
    
    aluSelB = controlALUSelB
    Mux(2, 8, aluSelB, regOutB, Wire(8, init=1), aluB)
    
    alu = ALU(aluA, aluB, aluOp, aluFlags, aluOut)
    
    flags = Register(4, aluFlags, flagsEn, flagsQ)
    
    pc = Register(8, aluOut, pcEn, pcQ)
    ir = Register(8, aluOut, irEn, irQ)
    
    regFile = RegFile(irQ, aluOut, regWriteEn, regOutA, regOutB)
    
    mar = Register(8, aluOut, marEn, marQ)
    
    Mux(2, 8, controlMemRead, aluOut, memOut, mdrD)
    OrGate(2, 1, controlLdMDR, controlMemRead, mdrEn)
    
    mdr = Register(8, mdrD, mdrEn, mdrQ)
    
    mem = Memory(256, marQ, memWriteEn, mdrQ, memOut)
    mem.load_bytes(data)
    
    debugger = Debugger(
            regFile,
            signalState, signalHalted,
            pcQ, irQ, marQ, mdrQ,
            aluA, aluB, aluOut, flagsQ,
        )
        
    try:
        Element.simulate_datapath()
    except HaltExecution as e:
        print e
        print ""
        
        print "Mem Dump:"
        print ['0x{:02x}'.format(b) for b in mem.state.mem]
        
        return 0
    else:
        assert False
        
        
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    