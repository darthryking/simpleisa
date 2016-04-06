"""

simplesim_fsm.py
By Ryan Lam

Defines the Finite State Machine (Flying Spaghetti Monster) controller element 
for the datapath.

"""

from simplesim_elements import Element, bits_required
from constants import State, Flags, ALUSelA, ALUSelB, ALUOp, Op


class Controller(Element):
    def __init__(self,
            inputInstruction, inputFlags,
            outputState, outputHalted,
            outputALUSelA, outputALUSelB, outputALUOp, outputLdFlags,
            outputLdPC, outputLdIR, outputLdReg,
            outputLdMAR, outputLdMDR,
            outputMemRead, outputMemWrite,
            ):
            
        assert inputInstruction.width == 8
        assert outputALUSelA.width == bits_required(ALUSelA.NUM_ALU_A)
        assert outputALUSelB.width == bits_required(ALUSelB.NUM_ALU_B)
        assert outputALUOp.width == bits_required(ALUOp.NUM_ALU_OPS)
        assert all(
                elem.width == 1
                for elem in (
                    outputLdFlags, outputLdPC, outputLdIR, outputLdReg,
                    outputLdMAR, outputLdMDR, outputMemRead, outputMemWrite,
                )
            )
            
        super(Controller, self).__init__()
        
        self.inputInstruction = inputInstruction
        self.inputFlags = inputFlags
        
        inputInstruction.register_callback(self.update)
        inputFlags.register_callback(self.update)
        
        self.outputState = outputState
        self.outputHalted = outputHalted
        self.outputALUSelA = outputALUSelA
        self.outputALUSelB = outputALUSelB
        self.outputALUOp = outputALUOp
        self.outputLdFlags = outputLdFlags
        self.outputLdPC = outputLdPC
        self.outputLdIR = outputLdIR
        self.outputLdReg = outputLdReg
        self.outputLdMAR = outputLdMAR
        self.outputLdMDR = outputLdMDR
        self.outputMemRead = outputMemRead
        self.outputMemWrite = outputMemWrite
        
    def update(self, value):
        state = self.state.state
        
        outputHalted = 0
        outputALUSelA = None
        outputALUSelB = None
        outputALUOp = None
        outputLdFlags = 0
        outputLdPC = 0
        outputLdIR = 0
        outputLdReg = 0
        outputLdMAR = 0
        outputLdMDR = 0
        outputMemRead = 0
        outputMemWrite = 0
        
        if state == State.FETCH_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.FETCH_1
            
        elif state == State.FETCH_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.FETCH_2
            
        elif state == State.FETCH_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.DECODE
            
        elif state == State.DECODE:
            try:
                nextState = {
                    Op.NOP  :   State.FETCH_0,
                    Op.END  :   State.HALT,
                    Op.MOV  :   State.MOV_0,
                    Op.LDC  :   State.LDC_0,
                    Op.LDM  :   State.LDM_0,
                    Op.STM  :   State.STM_0,
                    Op.INC  :   State.INC_0,
                    Op.DEC  :   State.DEC_0,
                    Op.NEG  :   State.NEG_0,
                    Op.BCM  :   State.BCM_0,
                    Op.USR  :   State.USR_0,
                    Op.SSR  :   State.SSR_0,
                    Op.USL  :   State.USL_0,
                    Op.ADD  :   State.ADD_0,
                    Op.SUB  :   State.SUB_0,
                    Op.AND  :   State.AND_0,
                    Op.OR   :   State.OR_0,
                    Op.CMP  :   State.CMP_0,
                    Op.JMP  :   State.JMP_0,
                    Op.JEQ  :   State.JEQ_0,
                    Op.JUL  :   State.JUL_0,
                    Op.JUG  :   State.JUG_0,
                    Op.JSL  :   State.JSL_0,
                    Op.JSG  :   State.JSG_0,
                }[self.inputInstruction.value]
                
            except KeyError:
                nextState = None
                
        elif state == State.HALT:
            outputHalted = 1
            nextState = State.HALT
            
        elif state == State.MOV_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.MOV_1
            
        elif state == State.MOV_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.MOV_2
            
        elif state == State.MOV_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.MOV_3
            
        elif state == State.MOV_3:
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.PASS_B
            outputLdReg = 1
            
            nextState = State.FETCH_0
            
        elif state == State.LDC_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.LDC_1
            
        elif state == State.LDC_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.LDC_2
            
        elif state == State.LDC_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.LDC_3
            
        elif state == State.LDC_3:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.LDC_4
            
        elif state == State.LDC_4:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.LDC_5
            
        elif state == State.LDC_5:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdReg = 1
            
            nextState = State.FETCH_0
            
        elif state == State.LDM_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.LDM_1
            
        elif state == State.LDM_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.LDM_2
            
        elif state == State.LDM_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.LDM_3
            
        elif state == State.LDM_3:
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.PASS_B
            outputLdMAR = 1
            
            nextState = State.LDM_4
            
        elif state == State.LDM_4:
            outputMemRead = 1
            nextState = State.LDM_5
            
        elif state == State.LDM_5:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdReg = 1
            
            nextState = State.FETCH_0
            
        elif state == State.STM_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.STM_1
            
        elif state == State.STM_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.STM_2
            
        elif state == State.STM_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.STM_3
            
        elif state == State.STM_3:
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.PASS_B
            outputLdMAR = 1
            
            nextState = State.STM_4
            
        elif state == State.STM_4:
            outputALUSelA = ALUSelA.REG_A
            outputALUOp = ALUOp.PASS_A
            outputLdMDR = 1
            
            nextState = State.STM_5
            
        elif state == State.STM_5:
            outputMemWrite = 1
            nextState = State.FETCH_0
            
        elif state == State.INC_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.INC_1
            
        elif state == State.INC_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.INC_2
            
        elif state == State.INC_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.INC_3
            
        elif state == State.INC_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.DEC_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.DEC_1
            
        elif state == State.DEC_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.DEC_2
            
        elif state == State.DEC_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.DEC_3
            
        elif state == State.DEC_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.SUB
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.NEG_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.NEG_1
            
        elif state == State.NEG_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.NEG_2
            
        elif state == State.NEG_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.NEG_3
            
        elif state == State.NEG_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUOp = ALUOp.NEG_A
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.BCM_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.BCM_1
            
        elif state == State.BCM_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.BCM_2
            
        elif state == State.BCM_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.BCM_3
            
        elif state == State.BCM_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUOp = ALUOp.BCM_A
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.USR_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.USR_1
            
        elif state == State.USR_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.USR_2
            
        elif state == State.USR_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.USR_3
            
        elif state == State.USR_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUOp = ALUOp.USR_A
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.SSR_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.SSR_1
            
        elif state == State.SSR_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.SSR_2
            
        elif state == State.SSR_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.SSR_3
            
        elif state == State.SSR_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUOp = ALUOp.SSR_A
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.USL_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.USL_1
            
        elif state == State.USL_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.USL_2
            
        elif state == State.USL_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.USL_3
            
        elif state == State.USL_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUOp = ALUOp.USL_A
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.ADD_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.ADD_1
            
        elif state == State.ADD_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.ADD_2
            
        elif state == State.ADD_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.ADD_3
            
        elif state == State.ADD_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.ADD
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.SUB_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.SUB_1
            
        elif state == State.SUB_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.SUB_2
            
        elif state == State.SUB_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.SUB_3
            
        elif state == State.SUB_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.SUB
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.AND_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.AND_1
            
        elif state == State.AND_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.AND_2
            
        elif state == State.AND_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.AND_3
            
        elif state == State.AND_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.AND
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.OR_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.OR_1
            
        elif state == State.OR_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.OR_2
            
        elif state == State.OR_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.OR_3
            
        elif state == State.OR_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.OR
            outputLdReg = 1
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.CMP_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.CMP_1
            
        elif state == State.CMP_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.CMP_2
            
        elif state == State.CMP_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdIR = 1
            
            nextState = State.CMP_3
            
        elif state == State.CMP_3:
            outputALUSelA = ALUSelA.REG_A
            outputALUSelB = ALUSelB.REG_B
            outputALUOp = ALUOp.SUB
            outputLdFlags = 1
            
            nextState = State.FETCH_0
            
        elif state == State.JMP_0:
            outputALUSelA = ALUSelA.PC
            outputALUOp = ALUOp.PASS_A
            outputLdMAR = 1
            
            nextState = State.JMP_1
            
        elif state == State.JMP_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.JMP_2
            
        elif state == State.JMP_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdPC = 1
            
            nextState = State.FETCH_0
            
        elif state == State.JEQ_0:
            if self.inputFlags.value & Flags.ZERO:
                outputALUSelA = ALUSelA.PC
                outputALUOp = ALUOp.PASS_A
                outputLdMAR = 1
                
                nextState = State.JEQ_1
                
            else:
                outputALUSelA = ALUSelA.PC
                outputALUSelB = ALUSelB.ONE
                outputALUOp = ALUOp.ADD
                outputLdPC = 1
                
                nextState = State.FETCH_0
                
        elif state == State.JEQ_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.JEQ_2
            
        elif state == State.JEQ_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdPC = 1
            
            nextState = State.FETCH_0
            
        elif state == State.JUL_0:
            if self.inputFlags.value & Flags.CARRY:
                outputALUSelA = ALUSelA.PC
                outputALUOp = ALUOp.PASS_A
                outputLdMAR = 1
                
                nextState = State.JUL_1
                
            else:
                outputALUSelA = ALUSelA.PC
                outputALUSelB = ALUSelB.ONE
                outputALUOp = ALUOp.ADD
                outputLdPC = 1
                
                nextState = State.FETCH_0
                
        elif state == State.JUL_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.JUL_2
            
        elif state == State.JUL_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdPC = 1
            
            nextState = State.FETCH_0
            
        elif state == State.JUG_0:
            flags = self.inputFlags.value
            
            carry = bool(flags & Flags.CARRY)
            zero = bool(flags & Flags.ZERO)
            
            if not carry and not zero:
                outputALUSelA = ALUSelA.PC
                outputALUOp = ALUOp.PASS_A
                outputLdMAR = 1
                
                nextState = State.JUG_1
                
            else:
                outputALUSelA = ALUSelA.PC
                outputALUSelB = ALUSelB.ONE
                outputALUOp = ALUOp.ADD
                outputLdPC = 1
                
                nextState = State.FETCH_0
                
        elif state == State.JUG_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.JUG_2
            
        elif state == State.JUG_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdPC = 1
            
            nextState = State.FETCH_0
            
        elif state == State.JSL_0:
            flags = self.inputFlags.value
            
            negative = bool(flags & Flags.NEGATIVE)
            overflow = bool(flags & Flags.OVERFLOW)
            
            if negative != overflow:
                outputALUSelA = ALUSelA.PC
                outputALUOp = ALUOp.PASS_A
                outputLdMAR = 1
                
                nextState = State.JSL_1
                
            else:
                outputALUSelA = ALUSelA.PC
                outputALUSelB = ALUSelB.ONE
                outputALUOp = ALUOp.ADD
                outputLdPC = 1
                
                nextState = State.FETCH_0
                
        elif state == State.JSL_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.JSL_2
            
        elif state == State.JSL_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdPC = 1
            
            nextState = State.FETCH_0
            
        elif state == State.JSG_0:
            flags = self.inputFlags.value
            
            zero = bool(flags & Flags.ZERO)
            negative = bool(flags & Flags.NEGATIVE)
            overflow = bool(flags & Flags.OVERFLOW)
            
            if not zero and negative == overflow:
                outputALUSelA = ALUSelA.PC
                outputALUOp = ALUOp.PASS_A
                outputLdMAR = 1
                
                nextState = State.JSG_1
                
            else:
                outputALUSelA = ALUSelA.PC
                outputALUSelB = ALUSelB.ONE
                outputALUOp = ALUOp.ADD
                outputLdPC = 1
                
                nextState = State.FETCH_0
                
        elif state == State.JSG_1:
            outputMemRead = 1
            
            outputALUSelA = ALUSelA.PC
            outputALUSelB = ALUSelB.ONE
            outputALUOp = ALUOp.ADD
            outputLdPC = 1
            
            nextState = State.JSG_2
            
        elif state == State.JSG_2:
            outputALUSelA = ALUSelA.MDR
            outputALUOp = ALUOp.PASS_A
            outputLdPC = 1
            
            nextState = State.FETCH_0
            
        else:
            assert False
            
        assert (
            outputALUOp not in (
                ALUOp.PASS_A,
                ALUOp.NEG_A, ALUOp.BCM_A,
                ALUOp.USR_A, ALUOp.SSR_A, ALUOp.USL_A,
                ALUOp.ADD, ALUOp.SUB, ALUOp.AND, ALUOp.OR,
            ) or
            outputALUSelA is not None
        )
        
        assert (
            outputALUOp not in (
                ALUOp.PASS_B,
                ALUOp.ADD, ALUOp.SUB, ALUOp.AND, ALUOp.OR,
            ) or
            outputALUSelB is not None
        )
        
        assert (
            (outputLdMDR == 0 and outputMemRead == 0) or
            outputLdMDR != outputMemRead
        )
        
        self.outputState.set_value(state)
        self.outputHalted.set_value(outputHalted)
        self.outputALUSelA.set_value(outputALUSelA)
        self.outputALUSelB.set_value(outputALUSelB)
        self.outputALUOp.set_value(outputALUOp)
        self.outputLdFlags.set_value(outputLdFlags)
        self.outputLdPC.set_value(outputLdPC)
        self.outputLdIR.set_value(outputLdIR)
        self.outputLdReg.set_value(outputLdReg)
        self.outputLdMAR.set_value(outputLdMAR)
        self.outputLdMDR.set_value(outputLdMDR)
        self.outputMemRead.set_value(outputMemRead)
        self.outputMemWrite.set_value(outputMemWrite)
        
        self.next.state = nextState
        
    def reset(self):
        super(Controller, self).reset()
        
        self.state.state = State.FETCH_0
        self.next.state = None
        
    def start_cycle(self):
        self.update(None)
        
    def transition(self):
        assert self.next.state is not None
        super(Controller, self).transition()
        self.next.state = None
        
        