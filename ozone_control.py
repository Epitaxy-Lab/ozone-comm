import tkinter as tk
import tkinter.font as tkfont
import serial.tools.list_ports
import numpy as np
from datetime import datetime
from pid import *
from utilities import *
import serial, os, time


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
convergence_bound = .07

## Valve Parameters
DEFAULT_VALVE = 46.0
MAX_VALVE_OPEN = 55.0

class Valve_Operation():
    '''
    Full GUI and control operations for Ozone flow.
    '''
    def __init__(self, root, ion_com, leak_com):
        '''
        Creates GUI and relevant control scheme for Ozone control

        :param ion_com: serial connection to the ion gauge
        :param leak_com: serial connection to the leak valve
        '''
        self.root = root
        self.ion_conn = serial.Serial(ion_com, baudrate = 19200, timeout = .5)
        self.leak_conn = serial.Serial(leak_com, baudrate = 9600, parity = serial.PARITY_EVEN, bytesize = serial.SEVENBITS, timeout=3)

        self.init_buttons()
        self.init_labels()

        self.btn_frame.grid(row=0, column=0, sticky='w')
        self.lbl_frame.grid(row=0, column=1, sticky='e')

        self.ctrl_loop = None
        self.valve_pos = 0
        self.pressure_val = 1.8e-8

    def init_buttons(self):
        '''
        Initializes ON and OFF button components of the GUI.
        '''
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.config(bg="#4169e1")

        btn_font = tkfont.Font(family="Helvetica", size=36)
        self.btn_on = tk.Button(self.btn_frame, text="ON", bg="green", fg="white", height=BTN_H, width=BTN_W, font=btn_font, command=self.valve_on)
        self.btn_off = tk.Button(self.btn_frame, text="OFF", bg="red", fg="white", height=BTN_H, width=BTN_W, font=btn_font, command=self.valve_close)

        self.btn_on.pack(side=tk.TOP, padx=(BTN_PAD, BTN_PAD*4), pady=19)
        self.btn_off.pack(side=tk.TOP, padx=(BTN_PAD, BTN_PAD*4), pady=19)

    def init_labels(self):
        '''
        Initializes readable labels and inputs of the GUI.
        '''
        self.lbl_frame = tk.Frame(self.root)
        self.lbl_frame.config(bg="#4169e1")
        txt_font = tkfont.Font(family="Helvetica", size=24)
        inp_font = tkfont.Font(family="Helvetica", size=22)
        top_el_padding = (10, 4)
        bottom_el_padding = (8, 25)
        reading_font = tkfont.Font(family="Helvetica", size=36)

        self.numpad = None

        self.txt_read_pressure = tk.Label(self.lbl_frame, text="Current Pressure", font = txt_font)
        self.lbl_read_pressure = tk.Label(self.lbl_frame, text="300Pa", bg="black", fg="white", font=reading_font)
        self.txt_read_valve = tk.Label(self.lbl_frame, text="Current Valve Position", font = txt_font)
        self.lbl_read_valve = tk.Label(self.lbl_frame, text="000000", font=reading_font)
        self.lbl_exp = tk.Label(self.lbl_frame, text="E -", bg="#4169e1", font=tkfont.Font(family="Helvetica", size=18))

        self.txt_set_pressure = tk.Label(self.lbl_frame, text="Desired Pressure", font = txt_font)
        self.lbl_set_pressure = tk.Entry(self.lbl_frame,  text="Desired Pressure", width=ENTRY_W, font=inp_font)
        self.lbl_set_pressure_power = tk.Entry(self.lbl_frame, text="Desired Power", width=ENTRY_W, font=inp_font)
        self.lbl_set_pressure.bind("<1>", lambda event: self.create_numpad(self.lbl_set_pressure))
        self.lbl_set_pressure_power.bind("<1>", lambda event: self.create_numpad(self.lbl_set_pressure_power))

        self.txt_read_pressure.pack(side=tk.TOP, pady=top_el_padding)
        self.lbl_read_pressure.pack(side=tk.TOP, ipadx = 10, ipady = 5, pady = bottom_el_padding)

        self.txt_read_valve.pack(side=tk.TOP, pady = top_el_padding)
        self.lbl_read_valve.pack(side = tk.TOP, ipadx=10, ipady = 5, pady = bottom_el_padding)

        self.txt_set_pressure.pack(side=tk.TOP, pady=top_el_padding)
        self.lbl_set_pressure.pack(side=tk.LEFT, padx=(50, 0), pady = bottom_el_padding, ipady = 10)

        self.lbl_exp.pack(side=tk.LEFT, pady = bottom_el_padding)
        self.lbl_set_pressure_power.pack(side=tk.LEFT, pady = bottom_el_padding, ipady = 10)


    def update_pressure(self):
        '''
        Updates the current pressure reading.
        '''
        command = "#  RDIG\r"
        pressure = send_com(command, self.ion_conn)[3:].strip()
        self.pressure_val = parse_scientific(pressure)
        self.lbl_read_pressure['text'] = pressure
        self.lbl_read_valve['text'] = round(self.valve_pos, 3)
        self.root.after(500, self.update_pressure)

    def valve_on(self):
        '''
        Begins control process by initializing PID.
        '''
        self.data = ""

        whole_pressure = self.lbl_set_pressure.get()
        dec_pressure = self.lbl_set_pressure_power.get()
        set_pressure = parse_scientific(whole_pressure + "E-" + dec_pressure)

        if(self.ctrl_loop is not None):
            self.root.after_cancel(self.ctrl_loop)
            self.ctrl.target = set_pressure
        else:
            self.ctrl = PID_ff(def_P, def_I, def_D, set_pressure, SAMP_time, RAMP_time)
            self.valve_pos = DEFAULT_VALVE
            self.open_valve()

        self.adjust_pressure()

    def open_valve(self):
        '''
        Opens the leak valve to the current set position, which should be calculated by our control scheme.
        '''
        position = self.valve_pos
        places = str(position).split(".")
        to_wrt = "{:03.03f}".format(position).zfill(7).split(".")
        to_wrt = "".join(to_wrt)
        msg = "R:" + to_wrt + "\r\n"
        send_com(msg, self.leak_conn)

        print("Valve Position is now: " + to_wrt)
        ## TODO: ERROR HANDLING


    def adjust_pressure(self):
        '''
        Runs the control loop, calculating the new valve position.
        '''
        curr_pressure = self.pressure_val
        pressure_diff = calc_per_diff(curr_pressure, self.ctrl.target)
        if(abs(pressure_diff) > convergence_bound):
            per_diff = self.ctrl.calc_percent_change(curr_pressure)

            valve_adjustment = 1 + per_diff / 100

            if(self.valve_pos * valve_adjustment < MAX_VALVE_OPEN):
                self.valve_pos = self.valve_pos * valve_adjustment
                self.open_valve()
            else:
                print("VALVE POSITION TOO HIGH")
        else:
            print("CONVERGED!")

        self.log_values(curr_pressure)
        self.ctrl_loop = self.root.after(int(SAMP_time * 1000), self.adjust_pressure)

    def log_values(self, curr_pressure):
        '''
        Logs data during ozone flow.
        '''
        curr_time = datetime.now()
        curr_time = curr_time.strftime("%H:%M:%S")

        self.data += str(curr_time) + "," + str(curr_pressure) + "," + str(self.valve_pos) + "\n"

    def valve_close(self):
        '''
        Closes the valve and ends all control processes.
        '''
        command = "C:\r\n"
        response = send_com(command, self.leak_conn)
        self.valve_pos = 0.0
        ## TODO: Error Handling
        self.lbl_set_pressure['text'] = ""
        if(self.ctrl_loop is not None):
            self.root.after_cancel(self.ctrl_loop)
            self.ctrl_loop = None
            self.ctrl = None
            with open(time.strftime("%Y%m%d_%H%M%S") + "-ozone_monitor.csv", 'w') as to_wr:
                to_wr.write(self.data)

    def create_numpad(self, entry_widget):
        '''
        Creates a GUI numpad allowing the user to type with a touch screen

        :param entry_widget: the widget you would like to write to with this numpad
        '''
        if(self.numpad != None):
            self.numpad.destroy()
        self.numpad = tk.Toplevel(self.root)
        self.numpad.overrideredirect(True)

        title_bar = tk.Frame(self.numpad, bg="black", relief="raised", bd=2)
        close_button = tk.Button(title_bar, width=15, height=2, bg="red", text="X", command=self.numpad.destroy)
        title_bar.grid(row=0, column=2)
        close_button.pack()

        self.numpad.wm_title("Numpad")
        digits = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '.', '⌫']
        num_font = tkfont.Font(family="Helvetica", size=26)

        for i, b in enumerate(digits):
            cmd = lambda bu=b: self.type_in(entry_widget, bu)
            self.numpad.b = tk.Button(self.numpad, text=str(b), font=num_font, width=8, height=2, command = cmd).grid(row = int(i / 3) + 1, column = i % 3)

    def type_in(self, entry_widget, item):
        entry_widget.insert("end", item) if item != "⌫" else entry_widget.delete(0, "end")

class Serial_Selection():
    '''
    Class for selection of serial ports for ozone control.
    '''
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
        op_font = tkfont.Font(family="Helvetica", size=18)
        self.valve_selection = tk.OptionMenu(self.root, self.valve_var, *connections)
        self.valve_selection.config(width=45, height=2, font=opmen_font)
        self.root.nametowidget(self.valve_selection.menuname).config(font=op_font)
        self.lbl_valve.pack(pady=(30,10), padx=(30, 0))
        self.valve_selection.pack(pady=(10,15))

        self.gauge_var = tk.StringVar(self.root)
        self.gauge_var.set(connections[0])
        self.gauge_selection = tk.OptionMenu(self.root, self.gauge_var, *connections)
        self.gauge_selection.config(width=45, height=2, font=opmen_font)
        self.root.nametowidget(self.gauge_selection.menuname).config(font=op_font)
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
