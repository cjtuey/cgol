"""
* Name         : final_project.py
* Author       : Cian Tuey
* Created      : 05/07/2025
* Course       : CIS189
* IDE          : VSCodium
* Description  : A GUI implementation of Conway's Game of Life
*
* Academic Honesty: I attest that this is my original work.
* I have not used unauthorized source code, either modified or
* unmodified.       
"""

import time
import tkinter
from tkinter import messagebox

class InputError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message

class CellData:

    def __init__(self, rows, columns, pattern = [], offsetx = 0, offsety = 0):
        self.active = True
        self.current_cell = 0
        self.rows = rows
        self.columns = columns
        self.pattern = self.init_first(pattern, offsetx, offsety)
        self.init_next()

    def init_first(self, pattern, offsetx, offsety):
        self.cell_states = [[]]
        for i in range(self.rows):
            self.cell_states[0].append([])
            for j in range(self.columns):
                self.cell_states[0][i].append(False)
        for cell in pattern:
            self.cell_states[0][(cell[0] + offsetx) % self.rows][(cell[1] + offsety) % self.columns] = True

    def init_next(self):
        if self.current_cell < len(self.cell_states) - 1:
            return
        self.cell_states.append([])
        for i in range(self.rows):
            self.cell_states[self.current_cell + 1].append([])
            for j in range(self.columns):
                self.cell_states[self.current_cell + 1][i].append(False)

    def next_gen(self):
        if self.current_cell < len(self.cell_states) - 2:
            self.active = True
        if not self.active:
            return False
        for i in range(self.rows):
            for j in range(self.columns):
                live_neighbors = 0
                for row in range(i-1,i+2):
                    row %= self.rows
                    for cell in range(j-1,j+2):
                        cell %= self.columns
                        if row == i and cell == j:
                            pass
                        elif self.cell_states[self.current_cell][row][cell]:
                            live_neighbors += 1
                if row == i and cell == j:
                    pass
                elif self.cell_states[self.current_cell][i][j]:
                    if live_neighbors in range(2, 4):
                        self.cell_states[self.current_cell + 1][i][j] = True
                    else:
                        self.cell_states[self.current_cell + 1][i][j] = False
                else:
                    if live_neighbors == 3:
                        self.cell_states[self.current_cell + 1][i][j] = True
                    else:
                        self.cell_states[self.current_cell + 1][i][j] = False
        if self.cell_states[self.current_cell] == self.cell_states[self.current_cell + 1]:
            self.active = False
            return False
        self.current_cell += 1
        self.init_next()
        return True

def init_grid(rows, columns, pattern = [], offsetx = 0, offsety = 0):
    global cell_data
    global cell_grid
    global m
    global button_array
    global saved_index
    try:
        for coord in pattern:
            if coord[0] >= rows or coord[1] >= columns:
                raise InputError("pattern too large")
        if pattern == []:
            saved_index = -1
        else:
            saved_index = 0
        cell_data = CellData(rows, columns, pattern, offsetx, offsety)
        cell_grid.destroy()
        cell_grid = tkinter.Frame(m)
        cell_grid.grid(row=0)
        button_array = []
        for i in range(NUM_ROWS):
            button_array.append([])
            for j in range(NUM_COLUMNS):
                new_button = tkinter.Button(cell_grid, command=lambda one=i, two=j: cell_click(one, two))
                new_button.grid(row=i, column=j)
                button_array[i].append(new_button)
        update_cells()
    except InputError as e:
        error_handler(e)

def to_pattern(grid):
    pattern = []
    for i in range(NUM_ROWS):
        for j in range(NUM_COLUMNS):
            if grid[i][j]:
                pattern.append((i, j))
    return pattern

def toggle_cell(i, j):
    global cell_data
    if cell_data.cell_states[cell_data.current_cell][i][j]:
        button_array[i][j].config(bg='black', activebackground='black')
    else:
        button_array[i][j].config(bg='white', activebackground='black')

def update_cells():
    for i in range(NUM_ROWS):
        for j in range(NUM_COLUMNS):
            toggle_cell(i, j)

def cell_click(i, j):
    global cell_data
    cell_data.cell_states[cell_data.current_cell][i][j] = not cell_data.cell_states[cell_data.current_cell][i][j]
    cell_data = CellData(NUM_ROWS, NUM_COLUMNS, to_pattern(cell_data.cell_states[cell_data.current_cell]))
    toggle_cell(i, j)

def toggle_play():
    global playing
    global saved_index
    global cell_data
    playing = not playing
    if playing:
        play_pause_button.config(text="⏸")
    else:
        play_pause_button.config(text="▶")
    if saved_index == -1:
        saved_index = cell_data.current_cell
    play_loop()

def play_loop():
    global cell_data
    global playing
    if playing:
        if cell_data.next_gen():
            update_cells()
            m.after(int(speed * 1000), play_loop)
        else:
            toggle_play()

def reset():
    global cell_data
    global saved_index
    cell_data.current_cell = saved_index
    update_cells()

def stepback():
    global cell_data
    if cell_data.current_cell > 0:
        cell_data.current_cell -= 1
        update_cells()

def stepforward():
    global cell_data
    if cell_data.current_cell >= len(cell_data.cell_states) - 2:
        cell_data.next_gen()
    else:
        cell_data.current_cell += 1
    update_cells()

def latest_cell():
    global cell_data
    cell_data.current_cell = len(cell_data.cell_states) - 2
    update_cells()

def resize(x, y):
    global NUM_ROWS
    global NUM_COLUMNS
    global cell_data
    try:
        x = int(x)
        y = int(y)
        if x < 1 or y < 1:
            raise InputError("grid must be at least 1x1")
        elif x > MAX_ROWS or y > MAX_COLUMNS:
            raise InputError(f"grid may not exceed {MAX_ROWS}x{MAX_COLUMNS}")
        new_pattern = to_pattern(cell_data.cell_states[0])
        for coord in new_pattern:
            if coord[0] >= x or coord[1] >= y:
                raise InputError("pattern too large")
        NUM_ROWS = x
        NUM_COLUMNS = y
        init_grid(x, y, new_pattern)
    except ValueError:
        error_handler(InputError(f"both dimensions must be numbers"))
    except InputError as e:
        error_handler(e)

def set_speed(new_speed):
    global speed
    try:
        try:
            new_speed = float(new_speed)
            if new_speed <= 0:
                raise InputError("speed must be a positive number")
            speed = new_speed
        except ValueError as e:
            raise InputError("speed must be a positive number")
    except InputError as e:
        error_handler(e)

def shift(x, y):
    global cell_data
    global button_array
    try:
        x = int(x)
        y = int(y)
        init_grid(NUM_ROWS, NUM_COLUMNS, to_pattern(cell_data.cell_states[0]), x, y)
    except ValueError:
        error_handler(InputError("both dimensions must be numbers"))

def save_pattern(name):
    patterns[name] = to_pattern(cell_data.cell_states[cell_data.current_cell])

def load_pattern(name):
    try:
        init_grid(NUM_ROWS, NUM_COLUMNS, patterns[name])
    except KeyError:
        error_handler(InputError(f"pattern '{name}' not found"))

def error_handler(e):
    messagebox.showerror("Error", f"Input error: {e}")

if __name__ == '__main__':
    NUM_ROWS = 19
    NUM_COLUMNS = 19
    MAX_ROWS = 19
    MAX_COLUMNS = 62
    saved_index = -1
    playing = False

    patterns = {
        "demo1" : [(3, 4), (3, 7), 
                    (4, 4), (4, 5), (4, 6), (4, 7), 
                    (5, 3), (5, 8), 
                    (6, 3), (6, 5), (6, 6), (6, 8), 
                    (7, 3), (7, 8), 
                    (8, 4), (8, 5), (8, 6), (8, 7)],

        "demo2" : [(3, 4), (3, 6), (3, 7), (3, 8), (3, 10), 
                    (4, 5), (4, 7), (4, 9), (4, 12), 
                    (5, 3), (5, 5), (5, 6), (5, 7), (5, 10), (5, 11), 
                    (6, 4), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 12), 
                    (7, 3), (7, 6), (7, 9), (7, 10), (7, 11), (7, 12), 
                    (8, 3), (8, 4), (8, 5), (8, 6), (8, 9), (8, 12), 
                    (9, 3), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (9, 11), 
                    (10, 4), (10, 5), (10, 8), (10, 9), (10, 10), (10, 12), 
                    (11, 3), (11, 6), (11, 8), (11, 10), 
                    (12, 5), (12, 7), (12, 8), (12, 9), (12, 11)]
    }
    speed = 1

    cell_data = CellData(NUM_ROWS, NUM_COLUMNS)
    m = tkinter.Tk(className=" Conway's Game of Life ")
    cell_grid = tkinter.Frame()
    button_array = []
    init_grid(NUM_ROWS, NUM_COLUMNS)
    control_grid = tkinter.Frame()
    control_grid.grid(row=1)
    reset_button = tkinter.Button(control_grid, text="⏮", command=reset)
    reset_button.grid(row=0, column=0)
    stepback_button = tkinter.Button(control_grid, text="⏪", command=stepback)
    stepback_button.grid(row=0, column=1)
    play_pause_button = tkinter.Button(control_grid, text="▶", command=toggle_play)
    play_pause_button.grid(row=0, column=2)
    stepforward_button = tkinter.Button(control_grid, text="⏩", command=stepforward)
    stepforward_button.grid(row=0, column=3)
    latest_button = tkinter.Button(control_grid, text="⏭", command=latest_cell)
    latest_button.grid(row=0, column=4)
    input_grid = tkinter.Frame()
    input_grid.grid(row=2)
    speed_grid = tkinter.Frame(input_grid)
    speed_grid.grid(row=0)
    speed_label1 = tkinter.Label(speed_grid, text="Wait time between generations")
    speed_label1.grid(row=0, column=0)
    speed_input = tkinter.Entry(speed_grid)
    speed_input.insert(0, speed)
    speed_input.grid(row=0, column=1)
    speed_label2 = tkinter.Label(speed_grid, text="second(s)")
    speed_label2.grid(row=0, column=2)
    speed_button = tkinter.Button(input_grid, text="Change speed", command=lambda: set_speed(speed_input.get()))
    speed_button.grid(row=1)
    resize_grid = tkinter.Frame(input_grid)
    resize_grid.grid(row=2)
    row_label = tkinter.Label(resize_grid, text="Number of rows")
    row_label.grid(row=0, column=0)
    row_input = tkinter.Entry(resize_grid)
    row_input.insert(0, NUM_ROWS)
    row_input.grid(row=0, column=1)
    column_label = tkinter.Label(resize_grid, text="Number of columns")
    column_label.grid(row=1, column=0)
    column_input = tkinter.Entry(resize_grid)
    column_input.insert(0, NUM_COLUMNS)
    column_input.grid(row=1, column=1)
    resize_button = tkinter.Button(input_grid, text="Resize", command=lambda: resize(row_input.get(), column_input.get()))
    resize_button.grid(row=3)
    shift_grid = tkinter.Frame(input_grid)
    shift_grid.grid(row=4)
    shiftx_label1 = tkinter.Label(shift_grid, text="Shift pattern vertically by ")
    shiftx_label1.grid(row=0, column=0)
    shiftx_input = tkinter.Entry(shift_grid)
    shiftx_input.insert(0, '0')
    shiftx_input.grid(row=0, column=1)
    shiftx_label2 = tkinter.Label(shift_grid, text=" units (+ is down, - is up)")
    shiftx_label2.grid(row=0, column=2)
    shifty_label1 = tkinter.Label(shift_grid, text="Shift pattern horizontally by ")
    shifty_label1.grid(row=1, column=0)
    shifty_input = tkinter.Entry(shift_grid)
    shifty_input.insert(0, '0')
    shifty_input.grid(row=1, column=1)
    shifty_label2 = tkinter.Label(shift_grid, text=" units (+ is right, - is left)")
    shifty_label2.grid(row=1, column=2)
    shift_button = tkinter.Button(input_grid, text="Shift", command=lambda: shift(shiftx_input.get(), shifty_input.get()))
    shift_button.grid(row=5)
    pattern_grid = tkinter.Frame(input_grid)
    pattern_grid.grid(row=6)
    clear_button = tkinter.Button(pattern_grid, text="Clear pattern", command=lambda: init_grid(NUM_ROWS, NUM_COLUMNS))
    clear_button.grid(row=0, column=0)
    demo1_button = tkinter.Button(pattern_grid, text="Load demo 1", command=lambda: init_grid(NUM_ROWS, NUM_COLUMNS, patterns["demo1"]))
    demo1_button.grid(row=0, column=1)
    demo2_button = tkinter.Button(pattern_grid, text="Load demo 2", command=lambda: init_grid(NUM_ROWS, NUM_COLUMNS, patterns["demo2"]))
    demo2_button.grid(row=0, column=2)
    save_load_grid = tkinter.Frame(input_grid)
    save_load_grid.grid(row=7)
    save_button = tkinter.Button(save_load_grid, text="Save current pattern as...", command=lambda: save_pattern(save_input.get()))
    save_button.grid(row=0, column=0)
    save_input = tkinter.Entry(save_load_grid)
    save_input.grid(row=0, column=1)
    load_button = tkinter.Button(save_load_grid, text="Load pattern...", command=lambda: load_pattern(load_input.get()))
    load_button.grid(row=1, column=0)
    load_input = tkinter.Entry(save_load_grid)
    load_input.grid(row=1, column=1)
    m.mainloop()