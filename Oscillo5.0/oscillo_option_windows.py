'''
@author Manish Roy

This module contains the dialogue and option boxes for the Oscillo(TM) GUI.
I have to be honest here. A lot of this code is over my head. I'm a physical scientist
and a chemical engineer...not a GUI developer. 
'''

#import tkinter. This is the library that was used to build the GUI
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

'''
I tried to make the architecture of this module as simple as possible. Every dialog
box that appears in the gui is created by the same function. The variety of windows 
produced is a result of the if, elif, else statements seen in the __init__function.
'''
class get_value(tk.Toplevel):
    def __init__(self, parent, prompt,kind):
        tk.Toplevel.__init__(self, parent)

        self.label = tk.Label(self, text=prompt)
        self.label.grid(row=0,column=0)

        

        if kind == "parameters":
            #metal, DL, freq, gain
            self.metal = tk.StringVar()
            self.frequency = tk.StringVar()
            self.gain = tk.StringVar()
            self.DL = tk.StringVar()

            #make the entry fields
            self.metal_entry = tk.Entry(self, textvariable=self.metal)
            self.frequency_entry = tk.Entry(self, textvariable=self.frequency)
            self.gain_entry = tk.Entry(self, textvariable=self.gain)
            self.DL_check = tk.Checkbutton(self,text = "Check here if you are using a delay line.",variable=self.DL)
            self.ok_button = tk.Button(self, text="OK", command=self.on_ok_parameters)

            #make entry labels
            self.metal_label = tk.Label(self,text="Waveguide Material")
            self.frequency_label = tk.Label(self,text="Excitation Frequency (MHz)")
            self.gain_label = tk.Label(self,text="Gain (dB)")


            #pack the entry fields
            self.metal_entry.grid(row=1,column=1)
            self.frequency_entry.grid(row=2,column=1)
            self.gain_entry.grid(row=3,column=1)
            self.DL_check.grid(row=4,column=1)
            self.ok_button.grid(row=5,column=1)

            #pack entry labels
            self.metal_label.grid(row=1,column=0)
            self.frequency_label.grid(row=2,column=0)
            self.gain_label.grid(row=3,column=0)

            #self.entry.bind("<Return>", self.on_ok)
        
        elif kind == 'yn':
            yes = tk.Button(self,text="YES", command=self.yes,width=int(.5*len(prompt)))
            no = tk.Button(self,text="NO",command=self.no,width=int(.5*len(prompt)))
            yes.grid(row=1,column=0,rowspan=1)
            no.grid(row=1,column=1,rowspan=1)
        
        elif kind == 'int':
            self.integer = tk.IntVar()
            self.integer_entry = tk.Entry(self, textvariable=self.integer)
            self.integer_label = tk.Label(self,text="Integer: ")
            self.ok_button = tk.Button(self, text="OK", command=self.on_ok_integer)
            self.integer_entry.grid(row=1,column=1)
            self.integer_label.grid(row=1,column=0)
            self.ok_button.grid(row=5,column=1)

        elif kind == 'message':
            self.ok_button = tk.Button(self, text="OK", command=self.on_ok_message)
            self.ok_button.grid(row=5,column=1)
            


            

    def on_ok_parameters(self, event=None):
        self.vars = []
        #populate the vars array
        self.vars.append(self.metal.get())
        self.vars.append(self.DL.get())
        self.vars.append(self.frequency.get())
        self.vars.append(self.gain.get())

        #change the 0 or 1 in the DL variable to a Dl or no_DL
        if self.vars[1] == '1':
            self.vars[1] = 'DL'
        elif self.vars[1] == '0':
            self.vars[1] = 'no_DL'

        #append units to the frequency and gain
        self.vars[2] = self.vars[2] + "MHz"
        self.vars[3] = self.vars[3] + "dB"
        self.destroy()

    def on_ok_integer(self, event=None):
        self.vars = self.integer.get()
        self.destroy()

    def on_ok_message(self, event=None):
        self.vars = None
        self.destroy()

    def show(self):
        #self.wm_deiconify()
        self.wait_window()
        return self.vars
    
    def yes(self):
        self.destroy()
        self.vars = 'y'
    
    def no(self):
        self.destroy()
        self.vars = 'n'


