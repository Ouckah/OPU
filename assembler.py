opcodes = { 'NOPE': ['000', '000'],  # [NON_IMM, IMM] 
            'GYAT': ['aa0', 'aa0'],
            'YEET': ['600', '600'],
            'RIZZ': ['080', '280'],
            'FTAX': ['180', '380'], 
            'MOVE': ['080', '280'] }
NON_IMM, IMM = 0, 1

FILE_TYPE = '.ouck'

lines, lineinfo, lineadr, labels = [], [], [], {}
LINEINFO_NONE = '000000'

datainfo, dataadr = [], []
DATAINFO_NONE = '00'

REGS = set(['0', '1', '2', '3'])
OZR = "OZR"
RM_FILLER = '111000'

INSTRUCTION_RAM_SIZE = 32 * 8
DATA_RAM_SIZE = 16 * 16

HEADER = 'v3.0 hex words addressed'
TEXT_FILE_NAME = 'text_image'
DATA_FILE_NAME = 'data_image'

# helper functions
def add_padding(input, length):
    if len(input) < length:
        pad_length = length - len(input)
        padded = '0' * pad_length + input
        return padded
    else:
        return input
    
def is_reg(register):

    # special case OZR
    if register.upper() == OZR: return True

    # check length (HAS to be two since only 4 registers)
    if len(register) != 2: return False

    # check if it has X
    if register[0].upper() != "O": return False

    # check if second character is 1-3
    if register[1] not in REGS: return False

    return True

def is_imm(immediate):
    
    # check if imm is a number
    try: immediate = int(immediate)
    except: return False

    # check if imm is <= 8 bits
    bin_imm = bin(immediate)
    if len(str(bin_imm)) - 2 > 8: return False

    return True

def reg_to_bin(register):

    # validate register
    if not is_reg(register):
        return ''
    
    # special case OZR
    if register.upper() == OZR:
        return '11'

    # convert reg to binary
    reg_num = int(register[1])
    bin_reg = bin(reg_num)
    untagged_bin_reg = str(bin_reg)[2:]

    # add padding
    untagged_bin_reg = add_padding(untagged_bin_reg, 2)

    return untagged_bin_reg

def imm_to_bin(immediate):

    # convert str to int
    num = int(immediate)

    # convert int to bin
    bin_num = bin(num)

    # convert bin back to str
    bin_imm = str(bin_num)[2:]

    # add padding (8 bits)
    bin_imm = add_padding(bin_imm, 8)

    return bin_imm

def imm_to_hex(immediate):

    # convert str to int
    num = int(immediate)

    # convert int to hex
    hex_num = hex(num)

    # convert hex back to str
    hex_imm = str(hex_num)[2:]

    # add padding (2 bits)
    hex_imm = add_padding(hex_imm, 2)
    
    return hex_imm

def bin_to_hex(binary):

    # convert bin to int
    num = int(binary, 2)

    # convert bin to hex
    hex_num = hex(num)

    # convert hex to str
    str_num = str(hex_num)[2:]

    # add padding
    str_num = add_padding(str_num, 3)

    return str_num

def create_add_label(address):

    # convert string to hex
    hex_add = hex(address)

    # remove hex tag and convert to string
    label = str(hex_add)[2:]

    # add padding
    label = add_padding(label, 2)

    # add colon
    label += ": "

    return label

import sys

# error handling
# incorrect amount of args
if len(sys.argv) != 2: 
    print('Usage: assembler.py <sourcefile>')
    sys.exit(1)

# validate file type
f_name = sys.argv[1]
if f_name[-5:] != FILE_TYPE:
    print(f'Error: Assembler only takes {FILE_TYPE} files. Invalid file {f_name}')
    sys.exit(1)

# read file
f = open(sys.argv[1], 'r')

while True:
    line = f.readline()
    if not line: break
    lines.append(line.strip())

# break apart lines into instructions
text_found, data_found = False, False
for i in range(len(lines)):

    line = lines[i]

    # skip blank lines
    if not line: continue

    # special case: section headers
    if line == ".text":
        text_found = True
        continue
    if line == ".data":
        data_found = True
        continue


    # in data section
    if data_found and not text_found:

        name, data = '0', '0'

        args = line.split(' ')
        
        # invalid amount of args
        if len(args) != 2:
            print(f'Error: Invalid data given on line {i + 1}. {line}')
            sys.exit(1)
        
        name, data = args
        
        # validate variable name format
        if name[-1] != ':':
            print(f'Error: Invalid data given on line {i + 1}. {line}')
            sys.exit(1)
        name = name.strip()[:-1]

        # validate variable data (must be imm8)
        if not is_imm(data):
            print(f'Error: Invalid data given on line {i + 1}. {line}')
            sys.exit(1)

        # store data info
        datainfo.append(imm_to_hex(data))

        # add label
        labels[name] = data

    
    # in text section
    elif text_found:

        name, Rm, Rn, Rd = '0', '0', '0', '0'

        args = line.split(',')

        # NOP
        if len(args) == 1:

            name = args[0]

            # specific case NOP
            if name == 'NOP':
                Rn, Rm, Rd = OZR, OZR, OZR
            
            # if its not NOP its an invalid instruction
            else:
                print(f'Error: Invalid instruction given on line {i + 1}. {line}')
                sys.exit(1)

        # MOV
        elif len(args) == 2:
            
            instruction_data, Rm = args
            name, Rd = instruction_data.split(' ')

            # clean Rn + Rm regs
            Rn = Rn.strip()
            Rm = Rm.strip()

            # special case: Rm is a label
            if Rm in labels:
                
                # get data associated to variable
                Rm = labels[Rm]

            # check if Rm is a register / imm or a label
            if is_reg(Rm) or is_imm(Rm):
                Rn = OZR

            # error
            else:
                print(f'Error: Invalid instruction given on line {i + 1}. {line}')
                sys.exit(1)
                

        # STR, LDR, ADD, SUB
        elif len(args) == 3:

            instruction_data, Rn, Rm = args
            name, Rd = instruction_data.split(' ')

            # clean Rn + Rm regs
            Rn = Rn.strip()
            Rm = Rm.strip()

            # validation
            if is_reg(Rn) and (is_reg(Rm) or is_imm(Rm)):
                pass

            # special case Rm is a label
            elif Rm in labels:
                Rm = labels[Rm]

            # special [reg, imm / reg] case (STR, LDR)
            elif Rn[0] == "[" and Rm[len(Rm) - 1] == "]":

                # remove []
                Rn = Rn[1:]
                Rm = Rm[:-1]

                # validate registers
                if not is_reg(Rn) or (not is_reg(Rm) and not is_imm(Rm)):
                    print(f'Error: Invalid instruction given on line {i + 1}. {line}')
                    sys.exit(1)
            
            else:
                print(f'Error: Invalid instruction given on line {i + 1}. {line}')
                sys.exit(1)

        else:
            print(f'Error: Invalid instruction given on line {i + 1}. {line}')
            sys.exit(1)

        # clean data
        name, Rm, Rn, Rd = name.strip(), Rm.strip(), Rn.strip(), Rd.strip()

        # check if Rm is immediate or register
        Rm_imm = False
        if is_reg(Rm): 
            Rm = RM_FILLER + reg_to_bin(Rm)
        else:
            Rm = imm_to_bin(Rm)
            Rm_imm = True

        # check other registers and convert to binary
        if not is_reg(Rn) or not is_reg(Rd):
            print(f'Error: Invalid register given on line {i + 1}. {line}')
            sys.exit(1)
        Rn, Rd = reg_to_bin(Rn), reg_to_bin(Rd)

        # convert instruction to hex (for image file)
        opcode_hex = opcodes[name][Rm_imm]
        reg_hex = bin_to_hex(Rm + Rn + Rd)
        instruction_hex = opcode_hex + reg_hex

        # store instruction hex
        lineinfo.append(instruction_hex)

        # store instruction address
        lineadr.append(hex(i))
    
    else:
        print(f'Error: .text not found or instruction outside of .text on line {i + 1}. {line}')
        sys.exit(1)
    
# build source files

# create a new TEXT file
# handle file exists error
f_created = False
f_count = 1
f_name = TEXT_FILE_NAME
while not f_created:
    try: 
        f = open(f_name, 'x')
        f_created = True
    except:
        f_name = TEXT_FILE_NAME + f' ({f_count})'
        f_count += 1

# add header
f.write(HEADER)

# add hex instructions to image file
for i in range(INSTRUCTION_RAM_SIZE):

    # check if address label is needed (every 8 instructions)
    if i % 8 == 0:
        f.write('\n')

        label = create_add_label(i)
        f.write(label)

    # write instruction to image (if it exists)
    if i < len(lineinfo):
        f.write(lineinfo[i] + " ")
    else:
        f.write(LINEINFO_NONE + " ")

# add line (cause ASM needs that idk)
f.write('\n')

# close the file
f.close()


# create a new DATA file
# handle file exists error
f_created = False
f_count = 1
f_name = DATA_FILE_NAME
while not f_created:
    try: 
        f = open(f_name, 'x')
        f_created = True
    except:
        f_name = DATA_FILE_NAME + f' ({f_count})'
        f_count += 1

# add header
f.write(HEADER)

# add hex instructions to image file
for i in range(DATA_RAM_SIZE):

    # check if address label is needed (every 16 values)
    if i % 16 == 0:
        f.write('\n')

        label = create_add_label(i)
        f.write(label)

    # write instruction to image (if it exists)
    if i < len(datainfo):
        f.write(datainfo[i] + " ")
    else:
        f.write(DATAINFO_NONE + " ")

# add line (cause ASM needs that idk)
f.write('\n')

# close the file
f.close()