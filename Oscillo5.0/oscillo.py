

'''
@author Manish Roy

This module is the main user interface for Oscillo(TM). It was written under the
object oriented programming paradigme. Running this module will open the program 
and produce a window that acts as a hub for all the other modules in the Oscillo(TM)
software package. The function of each method in this module is outlined in commments
below. Additionally, each line is given its own comment to delineate its specific
contribution to the overal function of the method.
'''

'''
These lines import the libraries and modules necessary for this module to run.
'''
print("Loading...")
# import the collection options. See the module 'oscillo_collection_options.py' for more info.
import oscillo_collection_options as oso
#import the collection functions. See the module 'oscillo_collection_functinos.py' for more info.
import oscillo_collection_functions
#import the data processing functions. Seee the module 'oscillo_data_processing_functions.py' for more info
import oscillo_data_processing_functions
#import the threading library. This allows some of the more time-consuming processes to be completed in the background.
import _thread as th
#import the system so that the operating system can be detected.
import sys
#import tkinter. This is the library that was used to build the graphical user interface. 
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk


#The main class. This class is instantiated at the end of this module.
class OscilloMainMenu():

    def __init__(self,rootwindow):
        '''
        This method is run when the class is instantiated (see the end of the module).
        This method is mostly a platform for executing other methods that need to be 
        executed upon instantiating the class. It also acts as a place to assign most
        of the key attributes of the class.
        '''
        #Inherit the window created when this class was instantiated.
        self.rootwindow = rootwindow
        #Define the dimensions of the window (in pixels)
        self.rootwindow.geometry("600x500")
        #Creat the frames used to organize the buttons and labels. (See the create_frames method below).
        self.create_frames()
        #Create the welcome message that will display when the program is opened. (see the create_message method below.)
        self.create_message()
        #Instantiate the classes in each of the other modules in the Oscillo(TM) software package.
        # Each class must inherit the GUI window so that it can interact with it. Each class aslo 
        # inherits the universal string variable that was created in the create_message method. Inheriting
        # this string variabel allows each class to update the message in the message center seen on the GUI.
        self.rwf = oso.Raw_waveforms(self.rootwindow,self.strvar)
        self.pwf = oso.Processed_waveforms(self.rootwindow,self.strvar)
        self.cp = oso.Calibration_processes(self.rootwindow,self.strvar)
        self.ts = oso.Temperautre_sensing(self.rootwindow,self.strvar)
        self.cf = oscillo_collection_functions.data_collection(self.rootwindow,self.strvar)
        #The bottons for each process in the Oscillo(TM) software package are created here. (See the 
        # respective methods below for more detail.)
        self.create_raw_options()
        self.create_proc_options()
        self.create_cal_options()
        self.create_oscilloscope_options()
        self.create_other_options()
        
       
    def create_frames(self):
        """
        Here the frames used to orgainize the bottons and labels are created. There are two frames:
        one on the right of the window, and one on the left. Additionally, subframes are created to 
        further orgainize the buttons. Each time a lable or button is created, it is "packed" (or placed)
        into a frame. The frame that the button or label is packed into is the first argument in the
        method that creates the button or label.  
        """
        #create the right frame
        self.r_frame = tk.LabelFrame(self.rootwindow,text="Options")
        #create the left frame
        self.l_frame = tk.LabelFrame(self.rootwindow,text="Message Center")
        #create the frame for the buttons associated with raw waveform collection
        self.raw_frame = tk.LabelFrame(self.r_frame,text="Collect and Save Raw Waveforms")
        #create the frame for the buttons associated with processed waveform collection
        self.proc_frame = tk.LabelFrame(self.r_frame,text="Collect and Process Waveforms")
        #create the frame for the buttons associated with calibration
        self.cal_frame = tk.LabelFrame(self.r_frame,text="Perform Calibration Processes")
        #create the frame for the buttons associated with oscilloscope settings
        self.oscilloscope_frame = tk.LabelFrame(self.r_frame,text="Osciloscope Settings")
        #create the frame for the buttons associated with other options
        self.other_options_frame = tk.LabelFrame(self.r_frame, text="Other Options")
        #pack (place) frames in the GUI.
        self.r_frame.pack(side='right',expand='yes',fill='both',padx=5,pady=5)
        self.l_frame.pack(side='left',expand='yes',fill='both',padx=5,pady=5)
        self.raw_frame.pack()
        self.proc_frame.pack()
        self.cal_frame.pack()
        self.oscilloscope_frame.pack()
        self.other_options_frame.pack()

        
    def create_raw_options(self):
        '''
        In each of these methods that creates the bottons for the options, you will see essetially the 
        same pattern, so only this first options method is documented in detail. Here the buttons are
        created in a for loop. Each button must be assigned two attributes: a text label, and a function 
        that is called when the button is pressed. These attributes are created and stored in a dictionary
        called button_attributes. The buttons are then created in the for loop and stored in the list called
        buttons. Another loop is then used to pack the buttons into the frame that they were assigned to.
        This tactic of using loops to create the bottons was used so that more buttons could easily be added
        later on. To add another button, all you need to do is add another entry to the dictionary--with the
        text on the button as the dictionary key, and the function to be called as the dictionary value.
        '''
        
        #Create a list for the buttons to be stored in.
        buttons = []
        #Create a dictionary to store the attributes needed to create each button. 
        button_attributes = {"Single Waveform":self.rwf.single_waveform,
                            "Multiple Waveforms":self.rwf.multiple_waveforms,
                            "Continuous Waveform":self.rwf.continuous_waveform}
        #Create each button, assigning it a frame to be backed into, text to appear on it, and a function to call
        # when it is pressed.
        for key in button_attributes:
            button = tk.Button(self.raw_frame,text=key,command=button_attributes[key],width=30)
            buttons.append(button)
        i = 0
        j = 0
        #Pack the buttons into the frame.
        for item in buttons:
            item.grid(row=i,column=0)
            i += 1
    
    def create_proc_options(self):
        """
        The structure of this method is itentical to that of the create_raw_options method. See the 
        documentation on that method to understand how this one works. 
        """
        
        buttons = []
        button_attributes = {"Averaged Waveforms":self.pwf.average_waveform,
                            "Gaussian Timing":self.pwf.gaussian_timing,
                            "Gaussian Timing (variable zoom)":self.pwf.gaussian_timing_zoom,
                            "Cross Correlate Envelopes":self.pwf.cross_correlation_envelopes_zoom,
                            "Cross Correlate Waveforms":self.pwf.cross_correlation_waveforms_average_old_data}
                            
        for key in button_attributes:
            button = tk.Button(self.proc_frame,text=key,command=button_attributes[key],width=30)
            buttons.append(button)
        i = 0
        j = 0
        for item in buttons:
            item.grid(row=i,column=0)
            i += 1

    def create_cal_options(self):
        """
        The structure of this method is itentical to that of the create_raw_options method. See the 
        documentation on that method to understand how this one works. 
        """
        
        buttons = []
        button_attributes = {"Calibrate Temperature Sensing":self.cp.Gaussian_calibration,
                            "Collect New Reference Waveform":self.cp.create_new_reference,
                            "Distinguish Peaks By Selective Heating":self.cp.distinguish_peaks

                            }
        for key in button_attributes:
            button = tk.Button(self.cal_frame,text=key,command=button_attributes[key],width=30)
            buttons.append(button)
        i = 0
        j = 0
        for item in buttons:
            item.grid(row=i,column=0)
            i += 1
    
    def create_oscilloscope_options(self):
        """
        The structure of this method is itentical to that of the create_raw_options method. See the 
        documentation on that method to understand how this one works. 
        """
        
        buttons = []
        button_attributes = {"Restore Oscilloscope Settings":self.cf.scope_reset,

                            }
        for key in button_attributes:
            button = tk.Button(self.oscilloscope_frame,text=key,command=button_attributes[key],width=30)
            buttons.append(button)
        i = 0
        j = 0
        for item in buttons:
            item.grid(row=i,column=0)
            i += 1

    def create_other_options(self):
        """
        The structure of this method is itentical to that of the create_raw_options method. See the 
        documentation on that method to understand how this one works. 
        """
        
        buttons = []
        button_attributes = {"Graph Data From File":self.cf.scope_reset,
                            "Sense Temperature":self.ts.gaussian_sensing
                            }
        for key in button_attributes:
            button = tk.Button(self.other_options_frame,text=key,command=button_attributes[key],width=30)
            buttons.append(button)
        i = 0
        j = 0
        for item in buttons:
            item.grid(row=i,column=0)
            i += 1
    

    def create_message(self):
        '''
        This method plays two important roles. #1, it creates the welcome message that is 
        seen when the program is opened. #2, it creates a string variable that will be
        inherited by all the other modules and classes. (see the instantiation of the other
        classes in the __init__ method.) This string variable can then be updated to inform
        the user about processes that are being performed. 
        '''

        #create the universal, inheritable string variable
        self.strvar = tk.StringVar()
        #give the string variable a default value
        self.strvar.set("Welcome to Oscillo. Please choose from\n\
         the options on the right.")

        #create a message attribute (which is a tkinter label) and assign its text as the string variable
        self.message = tk.Label(self.l_frame,textvariable=self.strvar)
        #pack the message attribute into the GUI
        self.message.pack()
        
        


#create a window from the tkinter library. This is the main window you see in the GUI.
rootwindow = tk.Tk()

#instantiate the OscilloMainMenu class, and pass it the window that was just created
app = OscilloMainMenu(rootwindow)

#the windows in tkinter run on an event loop. This loop is initiated here.
rootwindow.mainloop()


