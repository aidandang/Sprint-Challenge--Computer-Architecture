"""CPU functionality."""

import sys

# set instruction constants
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

# assign stack pointer to 7
# which is the register which hold value
SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.registers = [0] * 8
        self.registers[7] = 0xF4
        self.pc = 0
        self.ram = [0] * 256
        self.halted = False
        self.flags = {}

    def load(self, filename):
        """Load a program into memory."""
        
        address = 0
        program = []

        try:
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()

                    # Check if the current line is a blank line
                    if num == "":
                        continue

                    value = int(num, 2)

                    program.append(value)

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} Not Found")
            sys.exit(1)

        for instruction in program:
            self.ram_write(instruction, address)
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        # set variables to for flags
        a = self.registers[reg_a]
        b = self.registers[reg_b]

        if op == ADD:
            self.registers[reg_a] += self.registers[reg_b]
            self.pc += 3
        elif op == MUL:
            self.registers[reg_a] *= self.registers[reg_b]
            self.pc += 3
        elif op == CMP:
            if a == b:
                self.flags['E'] = 1
            else:
                self.flags['E'] = 0
            if a < b:
                self.flags['L'] = 1
            else:
                self.flags['L'] = 0
            if a > b:
                self.flags['G'] = 1
            else:
                self.flags['G'] = 0
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def ram_read(self, address):
        return self.ram[address]
    
    def ram_write(self, value, address):
        self.ram[address] = value

    def hlt(self):
        self.halted = True
        self.pc += 1

    def ldi(self, reg_a, opr_b):
        self.registers[reg_a] = opr_b
        self.pc += 3
        
    def prn(self, reg_a):
        print(self.registers[reg_a])
        self.pc += 2
    
    def push(self, reg_a):
        self.registers[SP] -= 1
        self.ram_write(self.registers[reg_a], self.registers[SP])
        self.pc += 2

    def pop(self, reg_a):
        self.registers[reg_a] = self.ram_read(self.registers[SP])
        self.registers[SP] += 1
        self.pc += 2

    def call(self):
        next_instruction_address = self.pc + 2
        self.registers[SP] -= 1
        self.ram_write(next_instruction_address, self.registers[SP])
        register = self.ram_read(self.pc + 1)
        address = self.registers[register]
        self.pc = address

    def ret(self):
        ret_address = self.registers[SP]
        self.pc = self.ram_read(ret_address)
        self.registers[SP] += 1
    
    def jmp(self, reg_a):
        self.pc = self.registers[reg_a]
    
    def jeq(self, reg_a):
        if self.flags['E'] == 1:
            self.pc = self.registers[reg_a]
        else:
            self.pc += 2
    
    def jne(self, reg_a):
        if self.flags['E'] == 0:
            self.pc = self.registers[reg_a]
        else:
            self.pc += 2
    
    def run(self):
        """Run the CPU."""
        while self.halted is False:
            instruction_to_execute = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.execute_instruction(instruction_to_execute, operand_a, operand_b)
    
    def execute_instruction(self, instruction, operand_a, operand_b):
        if instruction == HLT:
            self.hlt()
        elif instruction == LDI:
            self.ldi(operand_a, operand_b)
        elif instruction == PRN:
            self.prn(operand_a)
        elif instruction == ADD:
            self.alu(instruction, operand_a, operand_b)
        elif instruction == MUL:
            self.alu(instruction, operand_a, operand_b)
        elif instruction == PUSH:
            self.push(operand_a)
        elif instruction == POP:
            self.pop(operand_a)
        elif instruction == CALL:
            self.call()
        elif instruction == RET:
            self.ret()
        elif instruction == CMP:
            self.alu(instruction, operand_a, operand_b)
        elif instruction == JMP:
            self.jmp(operand_a)
        elif instruction == JEQ:
            self.jeq(operand_a)
        elif instruction == JNE:
            self.jne(operand_a)
        else:
            print("Don't know what to do.")