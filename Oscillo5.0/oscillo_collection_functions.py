"""
@author Manish Roy

This module contains the methods that interface directly with the oscillloscope. 
It also contains many functions that are associated with plotting and saving the oscilloscope data.
Each method is documented in detail, and each line also includes a comment that delineates
its contribution to the overal functionality of the method.
"""

'''
Import the libraries and modules that are needed to run the methods in this module.
'''
#Import unpack from struct. This converts the data from the oscilloscope into usable numbers.
from struct import unpack
#Import the plotting library for plotting data.
import matplotlib.pyplot as plt
#Import numpy. This library contains many methods used in vectorized calculations, and other
# operations involving arrays.
import numpy as np
#Import the visa. This is a library that finds the oscilloscope and allows python to interact with it.
import visa 
#Import the operating system. This allows python to run terminal commands.
import os
#Import datetime. This allows python to create time stamps for naming files. It also allows it to 
# delay and execute its methods according to real-time parameters
import datetime as dt
#Import time. This like datetime, but it is higher level, and easier to use in many situations.
import time as t
#import the threading library. This allows some of the more time-consuming processes to be completed in the background.
import _thread as th

class data_collection(): 

    def __init__(self,rootwindow,strvar):
        '''
        Inherit the GUI window and the message string variable 
        from the Oscillo(TM) main menu module.
        '''
        self.rootwindow = rootwindow
        self.strvar = strvar
        return

    def myprint(self,text):
        '''
        This method is alot like the built-in print() method in python. But instead of 
        "printing" the text to the terminal, it displays it in the GUI message center.
        '''
        #Set the inherited string variable to the new text.
        self.strvar.set(text)
        #update the GUI window so that the text immediately appears.
        self.rootwindow.update()

    def fake_data(self):
        '''
        This method is used mainly during development. But it can also be used to perform 
        operations on data that has already been collected. Normally, when options are
        selected in the GUI, Oscillo(TM) collects a new waveform from the oscilloscope and 
        begins performing the requested task on the new data. However, if a developer wants
        to run a method in Oscillo(TM) but wants that method to be performed without being 
        connected to the oscilloscope, then fake_data() can be put in place of retrieve_waveform()
        in the particular collection method being used. If this is done, then the setup_scope()
        method must be commented out of the respective collection option, and all lines that attempt
        to send settings to the oscilloscope must be commented out as well.
        '''

        #fake data for development. This is just a waveform that I collected on the 
        # 3D-printed Aluminum waveguide on 8/20/2018. The frequency was 5 MHz and the
        # gain was 34 dB. If you want to use a different data set, just replace "test_waveform.csv"
        # with the path of the data that you want to use. The data must be in two collumns with headers
        # for this function to work as is.
        myfile = open("test_waveform.csv",'r')
        #create a list to store the time data
        times = []
        #create a list to store the amplitude data
        amplitudes = []
        print('reading')
        #This loop reads the data line-by-line and stores it in the two lists just created.
        while True:
            
            #read a line from the file
            myline = myfile.readline()
            #split the line into a list based on the comma delimiter 
            mylist = myline.split(',')
            #if the loop gets to the end of the file, and encounters a blank line, the loop will break.
            if myline == "":
                break
            
            #these two lines clip the new line character off the end of the second data point in the list
            amp = mylist[1]
            amp = amp[:len(amp)-1]

            #if the data is not the header (doesn't contain letters), then the data is 
            # converted into a float and appended to the time and amplitude lists.
            if not amp.isalpha():

                times.append(float(mylist[0]))
                amplitudes.append(float(amp))

        #the data file is closed
        myfile.close()
        #the lists are converted into arrays so that they can be used in vectorized calculations.
        time = np.array(times)
        amplitude = np.array(amplitudes)

        #an arbitrary x scale is assigned
        xincr = 1e-9

        #the time and amplitude arrays are returned along with the x-scale factor.
        return time, amplitude, xincr

    def get_time_stamp(self):
        '''
        This method obtains a time stamp that can be used in the naming of files
        '''
        #obtain the time stamp
        mytime = dt.datetime.now().strftime('%d_%m_%Y_%H_%M_%S%f')
        
        #return the time stamp
        return mytime

    def make_directory(self,metal,DL,freq,gain):

        '''
        This method creates a directory to store the data collected from the oscilloscope.
        Data collected with the Oscillo(TM) software package will always be saved to the path
        specified in the dir_name variable below. You can change this default path here if you
        wish. When this method was created, the default path was "C:\\Oscillo\\DataFiles\\"
        '''

        #retrieve time stamp
        mytime = self.get_time_stamp()
        #name the directory based on parameters supplied by the user and the time stamp collected in the 
        # previous line.
        dir_name = "C:\\Oscillo\\DataFiles\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime
        #use the os method to creat the new directory.
        os.makedirs(dir_name)
        
        #return the name of the directory for use by other methods
        return(dir_name)

    def save_me(self,path_name,time,amplitude,metal,DL,freq,gain):
        
        '''
        This method saves the raw or processed waveform data provided in the form of two arrays. The data
        is saved in the directory created by the make_directory method. And a new time stamp is given to 
        the file to distinguish it from other data that were collected using the same parameters.
        '''

        #create an array of arrays
        myarray = np.array([time,amplitude])
        #transpose the arrays so that instead of being row vectors, they are now column vectors
        myarray = np.transpose(myarray)

        #obtain a new time stamp
        mytime = self.get_time_stamp()

        #name the file
        file_name_csv = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime + ".csv"
        #save the file to the path name created in the make_directory method
        np.savetxt(file_name_csv, myarray, delimiter = ',', header = "Time,Amplitude") 

        #The lines below are used to create and save a plot of the data. These have been commented out for now
        # because they were considered to be not very usefull, and they slow down the saving process considerably.
        '''
        file_name_png = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + mytime +  ".png" 
        plt.plot(time,amplitude)
        plt.xlabel('Time (microseconds)')
        plt.ylabel('Amplitude (V)')
        plt.savefig(file_name_png)
        plt.close()
        '''


    def check_data(self,time,amplitude):
        
        '''
        This function is a checkpoint for the data to make sure
        that the arrays are the same size. If they are not the same
        size, then the vectorized calculations involving both of them
        will throw errors.
        '''

        #compare the length of the arrays
        if not len(time) == len(amplitude):
            #if the lengths are not the same, then the time array is truncated by 1. 
            time = time[:len(time)-1]
        
        #return the arrays. 
        return(time, amplitude)



    def setup_scope(self):

        '''
        This method uses the visa library to identify the oscilloscope instrument. It then
        creates an object that serves as a handle for the instrument so that other methods 
        can interact with it. Additionally, this method sends some key settings to the oscilloscope
        to ensure that the proper data set is retrieved.
        '''

        #During development, the oscilloscope was prone to crashing. This try block catches that problem
        # ans alerts the user that the oscilloscope needs to be rebooted.
        try:

            #create a resource manager object. This object contains a list of all the instruments connected to the 
            # computer.
            rm = visa.ResourceManager()

            #create an object that acts as a handel for the oscilloscope. The argument presented her is the name of the
            # oscilloscope that was used during development. If a new oscilloscope is being used, then the name of the new
            # oscilloscope must be discovered by running the following commands in a terminal.
            '''
            >python
            >>>import visa
            >>>rm = visa.ResourceManager()
            >>>rm.list_resources()
            '''
            #the last line displays a list of all the instruments connected to the computer. Select the name that corresponds
            # to the oscilloscope that you are using, and place it here in the argument below.
            scope = rm.open_resource('USB0::0x0699::0x0378::C011202::INSTR')

            #these are settings that the oscilloscope needs in order to collect the spectrum properly
            self.myprint("Sending Parameters...")
            #The data source needs to be Channel 1 if that is the channel being used.
            scope.write('DATA:SOU CH1')
            #I have no idea what this one does.
            scope.write('DATA:WIDTH 1')
            #This tells the oscilloscope how to encode the data. Other encoding formats have proven not to work. 
            scope.write('DATA:ENC RPB')
            #The data collected starts at data point 1
            scope.write('DATA:START 1') 
            #The data collected ends at 1 million data points
            scope.write('DATA:STOP 1000000') 
            #Full resolution needs to be collected. If you replace "FULL" with "REDUCED" then the data collection will be faster
            # but you will lose a considerable ammount of resolution.
            scope.write('DATA:RESOLUTION FULL')
            #This indicates the amount of vertical offeset from the y=0 axis. If this is not set to zero,
            #  then the envelope computation will not work. 
            scope.write("CH1:OFFSET 0.0E+0") 
            

            
        except:
            #notify the user that the instrument was not found
            scope = "instrument error"
        
        #return the object handle.
        return scope

    def scope_reset(self):

        '''
        This method resets the oscilloscope settings. The module that contains the settings is 
        very large, and should only be imported if the oscilloscope needs to be reset. That is
        why this import line appears here instead of at the top of this module. 
        '''
        
        #the object handle for the oscilloscope is retrieved
        scope = self.setup_scope()
        self.myprint("Resetting Oscilloscope...")
        #the module containing the settings is imported
        import oscillo_settings0000 as oss
        #the method in the settings module is executed. 
        oss.oscillo_settings(scope)

        self.myprint("Oscilloscope was returned to its original settings.")

        

    def retrieve_waveform(self, scope):

        '''
        This method retrieves the data from the oscilloscope and converts it into
        numbers that can be used for calculations. It also retrieves ceratin parameters
        from the oscilloscope such as the signal trigger point, the y-offset, the horizontal
        scale factor, the vertical scale factor, etc. 
        '''
        
        #Alert the user if the instrument was not found. 
        if scope == "instrument error":
            self.myprint("The instrument specified was not found.\n\
             Please make sure that the instrument is connected, or\n\
              make sure that the instrument name is correct in the\n\
               source code. (oscillo_collection_options >>> setup_scope()")
            print("The instrument specified was not found. Please make sure that the instrument is connected, or make sure that the instrument name is correct in the source code. (oscillo_collection_options >>> setup_scope()")
            Time, Volts, xzero, xincr = 10, 10, 10, 10
            return Time, Volts, xzero, xincr

        '''
        These lines obtain parameters from the oscilloscope so that they can be used later
        by other methods.
        '''
        #obtain the vertiacl scale factor.
        ymult = float(scope.query('WFMPRE:YMULT?'))
        #I don't know what this one is.
        yzero = float(scope.query('WFMPRE:YZERO?'))
        #obtain the vertical offset
        yoff = float(scope.query('WFMPRE:YOFF?'))
        #obtain the horizontal scale factor
        xincr = float(scope.query('WFMPRE:XINCR?'))
        #obtain the signal trigger point
        xzero = float(scope.query('WFMPRE:XZERO?'))
        
        self.myprint("Collecting Data...")
        print("Collecting Data...")
        
        #I have no idea what this line does, I just know it's necessary. See the programmers manual 
        # if you really want to know.
        scope.write('CURVE?')
        
        #Retrieve the raw data from the oscilloscope
        data = scope.read_raw()

        #These lines remove the header from the data.
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]

        #unpack the data and convert it into a numpy array
        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))

        #Scale the data to physically significant values
        Volts = (ADC_wave - yoff) * ymult  + yzero

        #create a time domain according to the length of the amplitude data retrieved and the x-scale factor
        Time = np.linspace(0, xincr*len(Volts), len(Volts))
        
        #check to make sure that the arrays are the same length
        Time, Volts = self.check_data(Time, Volts)

        #return the arrays and parameters for later use by other methods.
        return Time, Volts, xzero, xincr

    def scope_change_zoom(self, scope, zoom_factor):

        '''
        In the course of development, it was found necessary to change the vertical scale factor between 
        data collections to obtain an acceptable degree of resolution for small features and avoid clipping
        large features. Calling this method is the most robust way to change the scale factor.
        '''
        #tTo measure the distal ends, this value needs to be 5, and to measure the small features, it needs to be .5
        #The gain needs to be 10. Any value larger than this will distort the distal end signals on 3D-printed waveguides.
        
        #Try to change the vertical scale on th oscilloscope
        try:
            scope.write("CH1:SCALE {}".format(zoom_factor)) #this successfully lets me see the smaller features with more information
        
        #Alert the user if the instrument was not found. 
        except:
            self.myprint("The instrument 'scope' could not be found.\n\
             Check your connection or reboot the instrument.")
            print("The instrument 'scope' could not be found. Check your connection or reboot the instrument.")
            exit()



    def plot_waveform(self, time, amplitude):

        '''
        This method is an all-in-one way to plot a waveform. It is mostly used to 
        plot the raw waveforms collected. If you need to plot something that has 
        more than one series, then see the documentation online for matplotlib.pyplot
        '''

        plt.plot(time, amplitude)
        plt.xlabel('Time (microseconds)')
        plt.ylabel('Amplitude (V)')
        plt.show()
        plt.close()


