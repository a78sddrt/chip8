import time
import random

class Chip8:
    def __init__(self):
    
        #################################
        #            memory(4KB)        #
        #################################
        self.memory = [0]*4096
        
        #################################
        #           registers           #
        #################################
        #16 general registers from V0 to VF, value: 1 byte
        self.V = [0]*16
        
        #Index register(store momery address: 16 bits)
        self.I = 0
        
        #PC register (16 bits)
        self.PC = 0
        
        #delay-time register (8 bits)
        self.DT = 0
         
        #sound-time register (8 bits)
        self.ST = 0
        
        #stack poointer (8 bits)
        self.SP = 0
        
        #################################
        #        stack(16*16 bits)      #
        #################################
        self.stack = [0]*16
        
        
        #################################
        #        keyboard(16 key)       #
        #################################
        self.key = [0]*16
        
        #################################
        #        Display(64*32 pixels)  #
        #################################
        self.display = [0]*(64*32)
        
        #Sprite data(font)
        self.fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        
        #store current instruction
        self.opcode = 0
        
        #Load font into memory
        for i in range(len(self.fontset)):
            self.memory[i] = self.fontset[i]
            
    def cycle(self):
        #Fetch instruction
        self.opcode = (self.memory[self.PC] << 8) | self.memory[self.PC+1]
        
        #PC counter +2
        self.PC+=2
        
        #Decode
        match self.opcode & 0xF000:
            case 0x0000:
                match self.opcode:
                    case 0x00E0:
                    #CLS: Clear the display
                        self.display = [0]*(64*32)
                    
                    
                    case 0x00EE:
                    #RET: Return from a subroutine
                        self.SP -=1
                        self.PC = self.stack[self.SP]
                    
                    case _:
                    #SYS addr: Jump to a machine code routine at nnn
                        pass
            case 0x1000: #JP addr Jump to location nnn.
                self.PC = self.opcode & 0x0FFF
                
            case 0x6000: #6xkk The interpreter puts the value kk into register Vx.
                x = (self.opcode & 0x0F00) >> 8  # 抓 x（高位 nibble）
                kk = self.opcode & 0x00FF        # 抓 nn（低 8 位）
                self.V[x] = kk                   # 設定 Vx = nn
            
            case 0x7000: #7xkk - ADD Vx, byte Set Vx = Vx + kk.
                x = (self.opcode & 0x0F00) >> 8
                kk = self.opcode & 0x00FF
                self.V[x] += kk
            
            case 0xA000: #Annn - LD I, addr Set I = nnn
                self.I = self.opcode & 0x0FFF
            
            case 0xD000:  #Dxyn - DRW Vx, Vy, nibble Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision
                self.V[0xF] = 0
                Vx = self.V[(self.opcode & 0x0F00) >> 8]
                Vy = self.V[(self.opcode & 0x00F0) >> 4]
                n = self.opcode & 0x000F
                for j in range(int(n)):
                    sprite_byte = self.memory[self.I+j]
                    for i in range(8):
                        collision_bit = sprite_byte >> (7 - i) & 1
                        if collision_bit == 1:
                            if self.display[Vx+i+64*(Vy+j)] == 1:
                                V[0xF] = 1
                            self.display[Vx+i+64*(Vy+j)] = collision_bit ^ self.display[Vx+i+64*(Vy+j)]
            
    def load_ROM(self, filename):
        with open(filename, 'rb') as f:
            rom = f.read()
            for i in range(len(rom)):
                self.memory[0x200+i] = rom[i]
                
    def draw_display(self):
        for y in range(32):
            line = ""
            for x in range(64):
                pixel = self.display[x + y * 64]
                line += "██" if pixel else "  "
            print(line)
            
    #def press_keyboard(self):
    #    for key in CHIP8_KEYMAP:
    #        self.key[CHIP8_KEYMAP[key]] = 1 if keyboard.is_pressed(key) else 0
    
        

chip8 = Chip8()
chip8.load_ROM("ibm_logo.ch8")
chip8.PC = 0x200

while True:
    #chip8.press_keyboard()
    chip8.cycle()
    chip8.draw_display()
    time.sleep(1/60)
                    
            
                
                    
        
        
        
        
        
        
        
        
        
        
