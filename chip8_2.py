import time
import random
import pygame
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

SCALE = 15
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

KEYMAP = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
}

class Chip8:
    def __init__(self):
        self.memory = [0]*4096
        self.V = [0]*16
        self.I = 0
        self.PC = 0x200
        self.DT = 0
        self.ST = 0
        self.SP = 0
        self.stack = [0]*16
        self.key = [0]*16
        self.display = [0]*(64*32)
        self.fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, 0x20, 0x60, 0x20, 0x20, 0x70,
            0xF0, 0x10, 0xF0, 0x80, 0xF0, 0xF0, 0x10, 0xF0, 0x10, 0xF0,
            0x90, 0x90, 0xF0, 0x10, 0x10, 0xF0, 0x80, 0xF0, 0x10, 0xF0,
            0xF0, 0x80, 0xF0, 0x90, 0xF0, 0xF0, 0x10, 0x20, 0x40, 0x40,
            0xF0, 0x90, 0xF0, 0x90, 0xF0, 0xF0, 0x90, 0xF0, 0x10, 0xF0,
            0xF0, 0x90, 0xF0, 0x90, 0x90, 0xE0, 0x90, 0xE0, 0x90, 0xE0,
            0xF0, 0x80, 0x80, 0x80, 0xF0, 0xE0, 0x90, 0x90, 0x90, 0xE0,
            0xF0, 0x80, 0xF0, 0x80, 0xF0, 0xF0, 0x80, 0xF0, 0x80, 0x80
        ]
        for i in range(len(self.fontset)):
            self.memory[i] = self.fontset[i]
        self.opcode = 0

    def cycle(self):
        self.opcode = (self.memory[self.PC] << 8) | self.memory[self.PC + 1]
        self.PC += 2
        # 處理指令（略）

    def load_ROM(self, filename):
        with open(filename, 'rb') as f:
            rom = f.read()
            for i in range(len(rom)):
                self.memory[0x200 + i] = rom[i]

    def draw_display(self, screen):
        screen.fill((0, 0, 0))
        for y in range(32):
            for x in range(64):
                if self.display[x + y * 64]:
                    pygame.draw.rect(
                        screen, (255, 255, 255),
                        (x * SCALE, y * SCALE, SCALE, SCALE))
        pygame.display.flip()

    def handle_key_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in KEYMAP:
            self.key[KEYMAP[event.key]] = 1
        elif event.type == pygame.KEYUP and event.key in KEYMAP:
            self.key[KEYMAP[event.key]] = 0

class Chip8App:
    def __init__(self, root):
        self.root = root
        self.root.title("CHIP-8 模擬器")
        self.fps = 600  # 初始執行頻率
        self.chip8 = Chip8()
        self.running = False
        self.setup_menu()
        self.label = tk.Label(root, text="請從『檔案』選單載入 ROM", font=("Arial", 14))
        self.label.pack(padx=20, pady=40)

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="開啟 ROM", command=self.open_rom)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="檔案", menu=file_menu)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="設定 FPS", command=self.set_fps)
        menu_bar.add_cascade(label="設定", menu=settings_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="操作說明", command=self.show_help)
        help_menu.add_command(label="關於", command=self.show_about)
        menu_bar.add_cascade(label="幫助", menu=help_menu)

        self.root.config(menu=menu_bar)

    def open_rom(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CHIP-8 ROMs", "*.ch8"), ("All files", "*.*")])
        if filepath:
            self.chip8 = Chip8()
            self.chip8.load_ROM(filepath)
            self.label.config(text=f"已載入：{filepath.split('/')[-1]}")
            self.start_emulation()

    def set_fps(self):
        new_fps = simpledialog.askinteger("設定 FPS", "輸入每秒執行多少次指令：", initialvalue=self.fps, minvalue=60, maxvalue=2000)
        if new_fps:
            self.fps = new_fps

    def show_help(self):
        messagebox.showinfo("操作說明", "使用說明：\n- 開啟 ROM\n- 設定 FPS\n- 關閉視窗結束模擬")

    def show_about(self):
        messagebox.showinfo("關於", "CHIP-8 Emulator\n作者：Roland")

    def start_emulation(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
        pygame.display.set_caption("CHIP-8")
        clock = pygame.time.Clock()
        self.running = True
        last_timer_update = pygame.time.get_ticks()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.chip8.handle_key_event(event)

            self.chip8.cycle()
            self.chip8.draw_display(screen)

            current_time = pygame.time.get_ticks()
            if current_time - last_timer_update >= 1000 // 60:
                last_timer_update = current_time
                if self.chip8.DT > 0:
                    self.chip8.DT -= 1
                if self.chip8.ST > 0:
                    self.chip8.ST -= 1

            clock.tick(self.fps)
        pygame.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = Chip8App(root)
    root.mainloop()
