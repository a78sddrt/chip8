import time
import random
import pygame
import tkinter as tk
from tkinter import filedialog

SCALE = 15  
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

KEYMAP = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,
    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF
}

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
                
            case 0x2000: #2nnn - CALL addr Call subroutine at nnn
                self.stack[self.SP] = self.PC
                self.SP += 1
                self.PC = self.opcode & 0x0FFF
                
            case 0x3000:
            #3xkk - SE Vx, byte Skip next instruction if Vx = kk
                x = (self.opcode & 0x0F00) >> 8
                kk = self.opcode & 0x00FF
                if self.V[x] == kk:
                    self.PC += 2
            
            case 0x4000:
            #4xkk - SNE Vx, byte Skip next instruction if Vx != kk
                x = (self.opcode & 0x0F00) >> 8
                kk = self.opcode & 0x00FF
                if self.V[x] != kk:
                    self.PC += 2
            
            case 0x5000:
            #5xy0 - SE Vx, Vy, Skip next instruction if Vx = Vy
                x = (self.opcode & 0x0F00) >> 8
                y = (self.opcode & 0x00F0) >> 4
                if self.V[x] == self.V[y]:
                    self.PC += 2
                
            case 0x6000: #6xkk The interpreter puts the value kk into register Vx.
                x = (self.opcode & 0x0F00) >> 8
                kk = self.opcode & 0x00FF
                self.V[x] = kk
            
            case 0x7000: #7xkk - ADD Vx, byte Set Vx = Vx + kk.
                x = (self.opcode & 0x0F00) >> 8
                kk = self.opcode & 0x00FF
                self.V[x] += kk
                self.V[x] = self.V[x] & 0xFF
                
            case 0x8000:
                match self.opcode & 0x000F:
                    case 0x000:
                    #8xy0 - LD Vx, Vy Set Vx = Vy.
                        x = (self.opcode & 0x0F00) >> 8
                        y = (self.opcode & 0x00F0) >> 4
                        self.V[x] = self.V[y]
                    
                    case 0x001:
                    #8xy1 - OR Vx, Vy Set Vx = Vx OR Vy.
                        x = (self.opcode & 0x0F00) >> 8
                        y = (self.opcode & 0x00F0) >> 4
                        self.V[x] = self.V[x] | self.V[y]
                        
                    case 0x002:
                    #8xy2 - AND Vx, Vy Set Vx = Vx AND Vy.
                        x = (self.opcode & 0x0F00) >> 8
                        y = (self.opcode & 0x00F0) >> 4
                        self.V[x] = self.V[x] & self.V[y]
                        
                    case 0x003:
                    #8xy3 - XOR Vx, Vy Set Vx = Vx XOR Vy.
                        x = (self.opcode & 0x0F00) >> 8
                        y = (self.opcode & 0x00F0) >> 4
                        self.V[x] = self.V[x] ^ self.V[y]
                    
                    case 0x004:
                    #8xy4 - ADD Vx, Vy Set Vx = Vx + Vy, set VF = carry.
                        x = (self.opcode & 0x0F00) >> 8
                        y = (self.opcode & 0x00F0) >> 4
                        add_value = self.V[x] + self.V[y]
                        self.V[x] = add_value & 0xFF
                        if add_value > 255:
                            self.V[0xF] = 1
                        else:
                            self.V[0xF] = 0
                        
                    case 0x005:
                    #8xy5 - SUB Vx, Vy Set Vx = Vx - Vy, set VF = NOT borrow.
                        x = (self.opcode & 0x0F00) >> 8
                        y = (self.opcode & 0x00F0) >> 4
                        borrow = 0
                        if self.V[x] >= self.V[y]:
                            borrow = 1
                        else:
                            borrow = 0
                        sub_value = self.V[x] - self.V[y]
                        self.V[x] = sub_value & 0xFF
                        self.V[0xF] = borrow
                    
                    case 0x006:
                    #8xy6 - SHR Vx {, Vy} Set Vx = Vx SHR 1.
                        x = (self.opcode & 0x0F00) >> 8
                        least_significant = self.V[x] & 1
                        self.V[x] = self.V[x] >> 1
                        self.V[0xF] = least_significant
                        
                    case 0x007:
                    #8xy7 - SUBN Vx, Vy Set Vx = Vy - Vx, set VF = NOT borrow.
                        x = (self.opcode & 0x0F00) >> 8
                        y = (self.opcode & 0x00F0) >> 4
                        borrow = 0
                        if self.V[y] >= self.V[x]:
                            borrow = 1
                        else:
                            borrow = 0
                        sub_value = self.V[y] - self.V[x]
                        self.V[x] = sub_value & 0xFF
                        self.V[0xF] = borrow
                    
                    case 0x00E:
                    #8xyE - SHL Vx {, Vy} Set Vx = Vx SHL 1.
                        x = (self.opcode & 0x0F00) >> 8
                        most_significant = (self.V[x] >> 7) & 1
                        self.V[x] = (self.V[x] << 1) & 0xFF
                        if  most_significant == 1:
                            self.V[0xF] = 1
                        else:
                            self.V[0xF] = 0
            
            case 0x9000:
            #9xy0 - SNE Vx, Vy Skip next instruction if Vx != Vy.
                x = (self.opcode & 0x0F00) >> 8
                y = (self.opcode & 0x00F0) >> 4
                if self.V[x] != self.V[y]:
                    self.PC += 2
            
            case 0xA000: #Annn - LD I, addr Set I = nnn
                self.I = self.opcode & 0x0FFF
                
            case 0xB000:
            #Bnnn - JP V0, addr Jump to location nnn + V0.
                nnn = self.opcode & 0x0FFF
                self.PC = self.V[0] + nnn
                self.PC = self.PC & 0xFFFF
            
            case 0xC000:
            #Cxkk - RND Vx, byte Set Vx = random byte AND kk.
                x = (self.opcode & 0x0F00) >> 8
                kk = self.opcode & 0x00FF
                rand_num = random.randint(0, 255)  #generate a random number 0～255
                self.V[x] = rand_num & kk

            
            case 0xD000:  # Dxyn - DRW Vx, Vy, nibble
                self.V[0xF] = 0  # Reset collision flag
                Vx = self.V[(self.opcode & 0x0F00) >> 8]
                Vy = self.V[(self.opcode & 0x00F0) >> 4]
                height = self.opcode & 0x000F

                for row in range(height):
                    sprite_byte = self.memory[self.I + row]
                    y_coord = (Vy + row) % 32  # wrap vertically

                    for col in range(8):
                        x_coord = (Vx + col) % 64  # wrap horizontally
                        pixel_bit = (sprite_byte >> (7 - col)) & 1
                        index = x_coord + (y_coord * 64)

                        if pixel_bit == 1:
                            if self.display[index] == 1:
                                self.V[0xF] = 1
                            self.display[index] ^= 1  # XOR draw

                            
            case 0xE000:
                match self.opcode & 0x000F:
                    case 0x000E:
                    #Ex9E - SKP Vx Skip next instruction if key with the value of Vx is pressed.
                        x = (self.opcode & 0x0F00) >> 8
                        if self.key[self.V[x]] == 1:
                            self.PC += 2
                    case 0x0001:
                    #ExA1 - SKNP Vx Skip next instruction if key with the value of Vx is not pressed.
                        x = (self.opcode & 0x0F00) >> 8
                        if self.key[self.V[x]] == 0:
                            self.PC += 2
            
            case 0xF000:
                match self.opcode & 0x00FF:
                    case 0x0007:
                    #Fx07 - LD Vx, DT Set Vx = delay timer value.
                        x = (self.opcode & 0x0F00) >> 8
                        self.V[x] = self.DT
                        
                    case 0x000A:
                    #Fx0A - LD Vx, K Wait for a key press, store the value of the key in Vx.
                        x = (self.opcode & 0x0F00) >> 8
                        key_pressed = False
                        for i in range(16):
                            if self.key[i]:  # self.key[i] == 1, some keys are pressed
                                self.V[x] = i
                                key_pressed = True
                                break
                        if not key_pressed:
                            #no key is pressed → stop
                            self.PC -= 2
                    
                    case 0x0015:
                    #Fx15 - LD DT, Vx Set delay timer = Vx.
                        x = (self.opcode & 0x0F00) >> 8
                        self.DT = self.V[x]
                    
                    case 0x0018:
                    #Fx18 - LD ST, Vx Set sound timer = Vx.
                        x = (self.opcode & 0x0F00) >> 8
                        self.ST = self.V[x]
                    
                    case 0x001E:
                    #Fx1E - ADD I, Vx Set I = I + Vx.
                        x = (self.opcode & 0x0F00) >> 8
                        self.I += self.V[x]
                        self.I = self.I & 0x0FFF
                    
                    case 0x0029:
                    #Fx29 - LD F, Vx Set I = location of sprite for digit Vx.
                        x = (self.opcode & 0x0F00) >> 8
                        self.I = self.V[x] * 5
                    
                    case 0x0033:
                        # Fx33 - LD B, Vx: Store BCD representation of Vx in memory at I, I+1, I+2
                        x = (self.opcode & 0x0F00) >> 8
                        value = self.V[x]
                        self.memory[self.I]     = value // 100
                        self.memory[self.I + 1] = (value // 10) % 10
                        self.memory[self.I + 2] = value % 10
                        
                    case 0x0055:
                        # Fx55 - Store V0 ~ Vx into memory starting at I
                        x = (self.opcode & 0x0F00) >> 8
                        for i in range(x + 1):
                            self.memory[self.I + i] = self.V[i]
                        self.I += 1

                    case 0x0065:
                        # Fx65 - Load memory[I] ~ memory[I+x] into V0 ~ Vx
                        x = (self.opcode & 0x0F00) >> 8
                        for i in range(x + 1):
                            self.V[i] = self.memory[self.I + i]
            
            
    def load_ROM(self, filename):
        with open(filename, 'rb') as f:
            rom = f.read()
            for i in range(len(rom)):
                self.memory[0x200+i] = rom[i]
    
    #self.display and pygame screen interaction
    def draw_display(self, screen):
        screen.fill((0, 0, 0))
        for y in range(32):
            for x in range(64):
                if self.display[x + y * 64]:
                    pygame.draw.rect(
                        screen,
                        (255, 255, 255),
                        (x * SCALE, y * SCALE, SCALE, SCALE)
                    )
        pygame.display.flip()

    def handle_key_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in KEYMAP:
                self.key[KEYMAP[event.key]] = 1
        elif event.type == pygame.KEYUP:
            if event.key in KEYMAP:
                self.key[KEYMAP[event.key]] = 0

# === Main ===
root = tk.Tk()
root.withdraw()
rom_path = filedialog.askopenfilename(
    title="Choose CHIP-8 ROM file",
    filetypes=[("CHIP-8 ROMs", "*.ch8"), ("All files", "*.*")]
)

if not rom_path:
    print("No ROM file，Program Ends。")
    exit()

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
pygame.display.set_caption("CHIP-8 Emulator")

chip8 = Chip8()
chip8.load_ROM(rom_path)

clock = pygame.time.Clock()

running = True
last_timer_update = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        chip8.handle_key_event(event)

    #execute one opcode
    chip8.cycle()

    # 處理畫面
    chip8.draw_display(screen)

    # 60Hz timer update
    current_time = pygame.time.get_ticks()
    if current_time - last_timer_update >= 1000 // 60:
        last_timer_update = current_time
        if chip8.DT > 0:
            chip8.DT -= 1
        if chip8.ST > 0:
            chip8.ST -= 1
            # for sound
    clock.tick(800)  # 800 opcodes/s

pygame.quit()
                    
            
                
                    
        
        
        
        
        
        
        
        
        
        
