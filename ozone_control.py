import tkinter as tk
import tkinter.font as tkfont
import serial.tools.list_ports
from simple_pid import PID
from utilities import *
import serial
import os


## Layout Variables
BTN_W = 10
BTN_H = 3
BTN_PAD = 30
ENTRY_W = 6
LBL_W = 40
LBL_H = 3

## Control Parameters
def_P = .1
def_I = .1
def_D = 0
convergence_bound = .03

## Valve Parameters
DEFAULT_VALVE = 46.0
MAX_VALVE_OPEN = 55.0

class Valve_Operation():
    def __init__(self, root, ion_com, leak_com):

        self.root = root
        self.ion_conn = serial.Serial() #serial.Serial(ion_com, baudrate=4800, timeout=.5)
        #self.leak_conn = serial.Serial(leak_com, baudrate=9600, parity=serial.PARITY_EVEN, bytesize=serial.SEVENBITS, timeout=3)

        self.init_buttons()
        self.init_labels()

        self.btn_frame.grid(row=0, column=0, sticky='w')
        self.lbl_frame.grid(row=0, column=1, sticky='e')

        self.ctrl_loop = None
        self.valve_pos = 0
        self.pressure_val = 1.8e-8

    def init_buttons(self):
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.config(bg="#4169e1")

        btn_font = tkfont.Font(family="Helvetica", size=36)
        self.btn_on = tk.Button(self.btn_frame, text="ON", bg="green", fg="white", height=BTN_H, width=BTN_W, font=btn_font, command=self.valve_on)
        self.btn_off = tk.Button(self.btn_frame, text="OFF", bg="red", fg="white", height=BTN_H, width=BTN_W, font=btn_font, command=self.valve_close)

        self.btn_on.pack(side=tk.TOP, padx=(BTN_PAD, BTN_PAD*4), pady=19)
        self.btn_off.pack(side=tk.TOP, padx=(BTN_PAD, BTN_PAD*4), pady=19)

    def init_labels(self):
        self.lbl_frame = tk.Frame(self.root)
        self.lbl_frame.config(bg="#4169e1")
        txt_font = tkfont.Font(family="Helvetica", size=24)
        self.txt_set_pressure = tk.Label(self.lbl_frame, text="Desired Pressure", font = txt_font)
        inp_font = tkfont.Font(family="Helvetica", size=22)
        self.lbl_set_pressure = tk.Entry(self.lbl_frame, text="Desired Pressure", width=ENTRY_W, font=inp_font)
        self.lbl_set_pressure_power = tk.Entry(self.lbl_frame, text="Desired Power", width=ENTRY_W, font=inp_font)
        self.lbl_set_pressure.bind("<1>", run_pi_keyboard)
        self.txt_read_pressure = tk.Label(self.lbl_frame, text="Current Pressure", font = txt_font)
        reading_font = tkfont.Font(family="Helvetica", size=36)
        self.lbl_read_pressure = tk.Label(self.lbl_frame, text="300Pa", bg="black", fg="white", font=reading_font)
        self.txt_read_valve = tk.Label(self.lbl_frame, text="Current Valve Position", font = txt_font)
        self.lbl_read_valve = tk.Label(self.lbl_frame, text="000000", font=reading_font)
        self.lbl_exp = tk.Label(self.lbl_frame, text="E", bg="#4169e1", font=tkfont.Font(family="Helvetica", size=18))

        top_el_padding = (20, 8)
        bottom_el_padding = (10, 15)

        self.txt_read_pressure.pack(side=tk.TOP, pady=top_el_padding)
        self.lbl_read_pressure.pack(side=tk.TOP, ipadx = 10, ipady = 5, pady = bottom_el_padding)

        self.txt_read_valve.pack(side=tk.TOP, pady = top_el_padding)
        self.lbl_read_valve.pack(side = tk.TOP, ipadx=10, ipady = 5, pady = bottom_el_padding)

        self.txt_set_pressure.pack(side=tk.TOP, pady=top_el_padding)
        self.lbl_set_pressure.pack(side=tk.LEFT, padx=(50, 0), pady = bottom_el_padding)

        self.lbl_exp.pack(side=tk.LEFT, pady = bottom_el_padding)
        self.lbl_set_pressure_power.pack(side=tk.LEFT, pady = bottom_el_padding)


    def update_pressure(self):
        command = "#  RDIG\r"
        pressure = send_com(command, self.ion_conn)[3:].strip()
        self.pressure_val = parse_scientific(pressure)
        self.lbl_read_pressure['text'] = pressure
        self.lbl_read_valve['text'] = self.valve_pos
        self.root.after(500, self.update_pressure)

    def valve_on(self):
        whole_pressure = self.lbl_set_pressure.get()
        dec_pressure = self.lbl_set_pressure_power.get()
        set_pressure = parse_scientific(whole_pressure + "E" + dec_pressure)

        self.ctrl = PID(def_P, def_I, def_D)
        self.ctrl.setpoint = set_pressure

        if(self.ctrl_loop is not None):
            self.root.after_cancel(self.ctrl_loop)
        if(self.valve_pos == 0.0):
            self.valve_pos = DEFAULT_VALVE
        self.open_valve(self.valve_pos)
        self.adjust_pressure()

    def open_valve(self, position):
        places = str(position).split(".")
        to_wrt = "{:03.03f}".format(position).zfill(7).split(".")
        to_wrt = "".join(to_wrt)
        msg = "R:" + to_wrt + "\r\n"

        print(send_com(msg, self.leak_conn))
        print("Valve Position is now: " + to_wrt)
        ## TODO: ERROR HANDLING



    def adjust_pressure(self):
        curr_pressure = self.pressure_val
        if(abs(calc_per_diff(curr_pressure, self.ctrl.setpoint)) > convergence_bound):
            adjustment = self.ctrl(curr_pressure)
            ## Calculate percent difference, and scale valve accordingly
            per_diff = (adjustment - curr_pressure) / curr_pressure
            dir = 1 if per_diff > 0 else -1
            valve_adjustment = 1 + dir * abs(per_diff / 100)

            self.valve_pos = self.valve_pos * valve_adjustment
            if(self.valve_pos < MAX_VALVE_OPEN):
                print("valve is: " + str(self.valve_pos))
                self.open_valve(round(self.valve_pos,6))
            else:
                print("VALVE POSITION TOO HIGH")

        self.ctrl_loop = self.root.after(1500, self.adjust_pressure)

    def valve_close(self):
        command = "C:\r\n"
        response = send_com(command, self.leak_conn)
        self.val_pos = 0.0
        ## TODO: Error Handling
        self.lbl_set_pressure['text'] = ""
        if(self.ctrl_loop is not None):
            self.root.after_cancel(self.ctrl_loop)
            self.ctrl_loop = None
            self.ctrl = None

class Serial_Selection():
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root)

        header_font = tkfont.Font(family="Helvetica", size=32, weight='bold')
        self.lbl_header = tk.Label(self.root, text="Please select your serial connections.", bg="orange")
        self.lbl_header['font'] = header_font
        self.lbl_header.pack(side=tk.TOP, pady=5)

        label_font = tkfont.Font(family="Helvetica", size=24)
        self.lbl_valve = tk.Label(self.root, text="Leak Valve Connection:", font=label_font, bg="#4169e1", fg="white", anchor="w", width="45")
        self.lbl_gauge = tk.Label(self.root, text="Ion Gauge Connection:", font=label_font, bg="#4169e1", fg="white", anchor="w", width="45")
        connections = list(serial.tools.list_ports.comports())
        self.valve_var = tk.StringVar(self.root)
        self.valve_var.set(connections[0])

        opmen_font = tkfont.Font(family="Helvetica", size=14)
        self.valve_selection = tk.OptionMenu(self.root, self.valve_var, *connections)
        self.valve_selection.config(width=45, height=2, font=opmen_font)
        self.lbl_valve.pack(pady=(30,10), padx=(30, 0))
        self.valve_selection.pack(pady=(10,15))

        self.gauge_var = tk.StringVar(self.root)
        self.gauge_var.set(connections[0])
        self.gauge_selection = tk.OptionMenu(self.root, self.gauge_var, *connections)
        self.gauge_selection.config(width=45, height=2, font=opmen_font)
        self.lbl_gauge.pack(pady=(30, 10), padx=(30, 0))
        self.gauge_selection.pack(pady=(10, 5))

        self.btn_ok = tk.Button(self.root, text="OK", command=self.move_on)
        self.btn_ok.pack(side=tk.BOTTOM, ipady=20, ipadx=40, pady=10)

    def move_on(self):
        igauge = self.gauge_var.get().split("-")[0].strip()
        lvalve = self.valve_var.get().split("-")[0].strip()
        self.root.destroy()
        root = tk.Tk()
        root.geometry("800x480")
        root.config(bg="#4169e1")

        app = Valve_Operation(root, igauge, lvalve)
        app.update_pressure()

        root.mainloop()

def main():
    root = tk.Tk()
    root.geometry("800x480")
    root.config(bg="#4169e1")

    app = Serial_Selection(root)

    root.mainloop()

if __name__ == "__main__":
    main()
