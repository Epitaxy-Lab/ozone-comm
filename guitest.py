import tkinter as tk 
import tkinter.font as tkfont 
from constants import *

class Rack_GUI():
    '''
    Class to encompass the GUI components of the Ozone Controller
    '''
    def __init__(self, root):
        '''
        Creates GUI and relevant control scheme for Ozone control

        :param ion_com: serial connection to the ion gauge
        :param leak_com: serial connection to the leak valve
        '''
        self.root = root

        self.init_fonts()
        self.init_buttons()
        self.init_labels()

        self.btn_frame.grid(row=0, column=0, sticky='w')
        self.lbl_frame.grid(row=0, column=1, sticky='e')

    def init_fonts(self):
        '''
        Initializes consistent fonts for GUI usage.
        '''
        self.btn_font = tkfont.Font(family="Helvetica", size=30)
        self.txt_font = tkfont.Font(family="Helvetica", size=24)
        self.inp_font = tkfont.Font(family="Helvetica", size=22)
        self.reading_font = tkfont.Font(family="Helvetica", size=36)
        self.num_font = tkfont.Font(family="Helvetica", size=26)
        self.check_font = tkfont.Font(family="Helvetica", size= 20)

    def init_buttons(self):
        '''
        Initializes ON and OFF button components of the GUI.
        '''
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.config(bg=BG_COLOR)

        self.btn_on = tk.Button(self.btn_frame, text="ON", bg="green", fg="white", height=BTN_H, width=BTN_W, font=self.btn_font) 
        self.btn_off = tk.Button(self.btn_frame, text="OFF", bg="red", fg="white", height=BTN_H, width=BTN_W, font=self.btn_font) 

        self.log = tk.IntVar()
        self.check_log_dat = tk.Checkbutton(self.btn_frame, text="Log Data?", variable=self.log, onvalue=1, offvalue=0, font=self.check_font)

        self.btn_on.pack(side=tk.TOP, padx=(BTN_PAD, BTN_PAD*4), pady=(BTN_VPAD, 0))
        self.check_log_dat.pack(side=tk.TOP, padx=(BTN_PAD, BTN_PAD*4))
        self.btn_off.pack(side=tk.TOP, padx=(BTN_PAD, BTN_PAD*4), pady=BTN_VPAD)

    def init_labels(self):
        '''
        Initializes readable labels and inputs of the GUI.
        '''
        self.lbl_frame = tk.Frame(self.root)
        self.lbl_frame.config(bg=BG_COLOR)

        self.numpad = None

        self.init_reading_labels()
        self.init_input_labels()

    def init_reading_labels(self):
        '''
        Initializes labels related to reading the pressure and valve position
        '''
        self.txt_read_pressure = tk.Label(self.lbl_frame, text="Current Pressure", font = self.txt_font)
        self.lbl_read_pressure = tk.Label(self.lbl_frame, text="300Pa", bg="black", fg="white", font=self.reading_font)
        self.txt_read_valve = tk.Label(self.lbl_frame, text="Current Valve Position", font = self.txt_font)
        self.lbl_read_valve = tk.Label(self.lbl_frame, text="000000", font=self.reading_font)
        self.lbl_exp = tk.Label(self.lbl_frame, text="E -", bg=BG_COLOR, font=tkfont.Font(family="Helvetica", size=18))
        self.txt_read_pressure.pack(side=tk.TOP, pady=top_el_padding)
        self.lbl_read_pressure.pack(side=tk.TOP, ipadx = 10, ipady = 5, pady = bottom_el_padding)

        self.txt_read_valve.pack(side=tk.TOP, pady = top_el_padding)
        self.lbl_read_valve.pack(side = tk.TOP, ipadx=10, ipady = 5, pady = bottom_el_padding)
        self.check_log_dat.pack(side=tk.TOP, pady = bottom_el_padding)

    def init_input_labels(self):
        '''
        Initializes labels and entries related to inputting the temperature
        '''
        self.txt_set_pressure = tk.Label(self.lbl_frame, text="Desired Pressure", font = self.txt_font)
        self.lbl_set_pressure = tk.Entry(self.lbl_frame,  text="Desired Pressure", width=ENTRY_W, font=self.inp_font)
        self.lbl_set_pressure_power = tk.Entry(self.lbl_frame, text="Desired Power", width=ENTRY_W, font=self.inp_font)
        self.lbl_set_pressure.bind("<1>", lambda event: self.create_numpad(self.lbl_set_pressure))
        self.lbl_set_pressure_power.bind("<1>", lambda event: self.create_numpad(self.lbl_set_pressure_power))

        self.txt_set_pressure.pack(side=tk.TOP, pady=top_el_padding)
        self.lbl_set_pressure.pack(side=tk.LEFT, padx=(50, 0), pady = bottom_el_padding, ipady = 10)
        self.lbl_exp.pack(side=tk.LEFT, pady = bottom_el_padding)
        self.lbl_set_pressure_power.pack(side=tk.LEFT, pady = bottom_el_padding, ipady = 10)

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

        for i, b in enumerate(digits):
            cmd = lambda bu=b: self.type_in(entry_widget, bu)
            self.numpad.b = tk.Button(self.numpad, text=str(b), font=self.num_font, width=8, height=2, command = cmd).grid(row = int(i / 3) + 1, column = i % 3)

    def type_in(self, entry_widget, item):
        '''
        Allows numpad to act
        '''
        entry_widget.insert("end", item) if item != "⌫" else entry_widget.delete(0, "end")

root = tk.Tk() 
root.geometry("800x480")
root.config(bg=BG_COLOR)

app = Rack_GUI(root)

root.mainloop()
