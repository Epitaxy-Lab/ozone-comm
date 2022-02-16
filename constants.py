import tkinter as tk
import tkinter.font as tkfont

## Initialize tkinter root
root = tk.Tk()

## Layout Variables
BTN_W = 10
BTN_H = 3
BTN_PAD = 30
ENTRY_W = 6
LBL_W = 40
LBL_H = 3

## Control Parameters
def_P = .5
def_I = .05
def_D = 0
SAMP_time = 2
RAMP_time = 75
convergence_bound = .05

## Valve Parameters
DEFAULT_VALVE = 46.0
MAX_VALVE_OPEN = 65.0

## Set Paddings
top_el_padding = (10, 4)
bottom_el_padding = (8, 25)