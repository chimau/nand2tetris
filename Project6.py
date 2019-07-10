"""Solution to Project 6: Assembler """

import sys
import re

class Assembler(object):
  """Provides the ability to assemble a Hack assmbley code to binary code."""

  def __init__(self):
    """Initializes an Assembler with symbole table."""
    self.symbol_table = self._init_symbol_table()


  def  _init_symbol_table(self):
    """Helps populates symbole table with predefined values."""
    symbol_table = {}
    for registers in range(16):
      symbol_table['R'+ str(registers)] = registers

    symbol_table['SCREEN'] = 16384
    symbol_table['KBD'] = 24576
    symbol_table['SP'] = 0
    symbol_table['LCL'] = 1
    symbol_table['ARG'] = 2
    symbol_table['THIS'] = 3
    symbol_table['THAT'] = 4

    return symbol_table

  
  def parse_file(self, file):
    """Takes a hack assembly files 'file.asm' and parses out the assembly commands.

    Args:
      file: A text file containing hack assemly code

    Returns:
      A list of instructions with list index representing an accending order of execusion
    """
    instructions = []
    with open(file) as f:
      for line in f:
        line=line.strip()
        if line.startswith('//'):
          continue
        if re.match('^[a-zA-Z@(0-9]+', line) :
          line = line.split('//')[0].strip()
          instructions.append(line)

    return instructions
    
  def first_pass(self, instructions):
    """Takes a list of hack instrcutions and populates symbol table
    with declaration symbol as key and line number as value.

    Args:
      instructions: A list of hack instructions i.e (loop), M = 1 + A etc,
      declearation stetements are (loop), (start), 
    """

    line_number = 0

    for instruction in instructions:
      if self._is_symbol_decleration(instruction):
        instruction = instruction.replace('(','').replace(')','')
        self.symbol_table[instruction] = line_number
        continue
      line_number += 1

    

  def second_pass(self, instructions):
    """Takes a list of hack instructions and returns a
    dictionary containing a list  of binary code representing translated instructions
    and a list of translated instructions 

    Args: 
      instructions: A list of hack instructions is (loop)

    Return:
      returns a dictionary containting 
        {'binary': binary_code, 'assembly': assembly_instruction}
    """
    binary = []
    asembly_instruction = []
    line_number = 16
    for instruction in instructions:
      if instruction.startswith('@'):
        instruction = instruction.replace('@','')
        if re.match('^[0-9]+', instruction):
          binary.append(bin(int(instruction))[2:].zfill(16))
          asembly_instruction.append(instruction)
          continue
        if instruction in self.symbol_table.keys():
          binary.append(bin(self.symbol_table[instruction])[2:].zfill(16))
          asembly_instruction.append(instruction)
          continue
        self.symbol_table[instruction] = line_number
        binary.append(bin(self.symbol_table[instruction])[2:].zfill(16))
        asembly_instruction.append(instruction)
        line_number += 1
        continue

      if instruction[0].isalnum():
        binary.append(self.C_translate(instruction))
        asembly_instruction.append(instruction)

    return {'binary' : binary, 'assembly': asembly_instruction}


  def C_translate(self, instruction):
    """Helper function for translating C instruction

    Args:
      instructions: A 'C' Hack instruction. i.e A = 1, AM = 0;jmp

    Return: 
      returns a translated hack instruction  
    """

    c_instruction = '111'
    c_translation_table = self.C_translation_table()
    dest = comp = jump = None
    if '=' in instruction:
      dest, leftover1 = instruction.split('=')
    if ';' in instruction:
      leftover2 ,jump = instruction.split(';')
    if '=' not in instruction and ';' not in instruction:
      comp = instruction
    else:
      pre_comp = instruction.split('=')
      pre_comp_with_jump = pre_comp[-1]
      pre_comp_without_jump = pre_comp_with_jump.split(';')
      comp = pre_comp_without_jump[0]

    comp_bin = c_translation_table['comp'][comp]
    a_value = 1 & (comp in c_translation_table['A'].keys())
    dest_bin = c_translation_table['dest'][dest]
    jump = c_translation_table['jump'][jump] 
    c_instruction = c_instruction + str(a_value) + comp_bin + dest_bin  + jump

    return c_instruction

  def _is_symbol_decleration(self, instruction):
    """helper function to Checks if line in text file denotes a hack symbol declartion"""
    return (instruction[0]=='(') & (instruction[-1] ==')')

  def C_translation_table(self):
    """Hack C code translation table, contains dictionary mapping 
    for C instruction to it binary value representation. """
    c_table = {'comp': 
            {
            '0':'101010',
            '1':'111111',
            '-1':'111010',
            'D':'001100',
            'A':'110000', 'M':'110000',
            '!D':'001101',
            '!A':'110001', '!M':'110001',
            '-D':'001111',
            '-A':'110011', '-M':'110011',
            'D+1':'011111',
            'A+1':'110111', 'M+1':'110111',
            'D-1':'001110',
            'A-1':'110010', 'M-1':'110010',
            'D+A':'000010', 'D+M':'000010',
            'D-A':'010011', 'D-M':'010011',
            'A-D':'000111', 'M-D':'000111',
            'D&A':'000000', 'D&M':'000000',
            'D|A':'010101', 'D|M':'010101'},
            'A':
              {
              'M':'110000',
              '!M':'110001',
              '-M':'110011',
              'M+1':'110111',
              'M-1':'110010',
              'D+M':'000010',
              'D-M':'010011',
              'M-D':'000111',
              'D&M':'000000',
              'D|M':'010101'},
            'dest':
              {
              None:'000',
              'M':'001',
              'D':'010',
              'MD':'011',
              'A':'100',
              'AM':'101',
              'AD':'110',
              'AMD':'111'},
           'jump':
               {
               None:'000',
               'JGT':'001',
               'JEQ':'010',
               'JGE':'011',
               'JLT':'100',
               'JNE':'101',
               'JLE':'110',
               'JMP':'111'} }
    return c_table

  def assemble(self, inputfile, outputfile, Verbose=None):
    """Translates a hack assembly file 'inputfile.asm' to a hack binary file 'outputfile.hack'

    Args:
      inputfile: A text file containing hack assembly code
      outputfile: A text file containig hack binary code representation.
      Verbose: if Vabose is V it will print out command as it translates it
    """
    instructions = self.parse_file(inputfile)

    self.first_pass(instructions)
    second_pass = self.second_pass(instructions)
    instructions_in_binary = second_pass['binary']
    instructions_in_assembly = second_pass['assembly']

    if Verbose in ['V', 'v', '-v', '-V']:
      print('*' * 20 + ' Verbose compiling ' + '*' * 20)
      for i in range(len(instructions_in_binary)): 
        print('[Line number: ' + str(i) + ']: ' +  str(instructions_in_assembly[i]) + ' -> ' + str(instructions_in_binary[i]))
      print('Translation complete')

    with open(outputfile + '.hack', 'w+') as f:
      for bin_code in instructions_in_binary:
        f.write(bin_code+'\n')
    print('Assembler completed')


def main():
  
  inputfile = sys.argv[1]
  outputfile = sys.argv[2]
  assembler = Assembler()
  assembler.assemble(inputfile, outputfile, Verbose=sys.argv[3])

if __name__ == '__main__':
  main()
