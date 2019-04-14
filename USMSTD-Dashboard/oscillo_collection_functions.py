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

    def __init__(self):
        print("Initiated class data_collection")


    def get_time_stamp(self):
        '''
        This method obtains a time stamp that can be used in the naming of files
        '''
        #obtain the time stamp
        mytime = dt.datetime.now().strftime('%d_%m_%Y_%H_%M_%S%f')

        #return the time stamp
        return mytime

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


    def retrieve_waveform(self, scope):

        '''
        This method retrieves the data from the oscilloscope and converts it into
        numbers that can be used for calculations. It also retrieves ceratin parameters
        from the oscilloscope such as the signal trigger point, the y-offset, the horizontal
        scale factor, the vertical scale factor, etc. 
        '''
        
        #Alert the user if the instrument was not found. 
        if scope == "instrument error":
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
            print("The instrument 'scope' could not be found. Check your connection or reboot the instrument.")
            exit()

    def clip_tails(self, time, amplitude, xzero, xincr, xend):
        '''
        Since the "RESOLUTION FULL" setting on the oscilloscope returns a lot of superfluous
        data, this method is necessary to clip most of that uneeded data off. Failing to clip
        off the uneeded data can really bog down some of the processes since the operations will
        be performed on 1 million data points instead of a few hundred thousand.
        '''

        # The absolute value of the data trigger point is established
        xzero = abs(xzero)
        # in order to find the location of this trigger point using the numpy.where method,
        # this value has to be buffered.
        zero_buffer = xincr
        zeromin = xzero - zero_buffer
        zeromax = xzero + zero_buffer

        # this method returns the index of the time array where the trigger point was found.
        start_index = np.where(np.logical_and(time <= zeromax, time >= zeromin))

        # extract integer from tuple and array
        while type(start_index) != type(np.int64(4)):
            start_index = start_index[0]

        # the same process is repeated with the ending index, except in this case, the ending index is
        # arbitrary. The developer can select it based on how much of the waveform they want to work with.
        end_buffer = xincr
        endmin = xend - end_buffer
        endmax = xend + end_buffer

        end_index = np.where(np.logical_and(time <= endmax, time >= endmin))

        # extract integer from tuple and array
        while type(end_index) != type(np.int64(4)):
            end_index = end_index[0]

        # truncate arrays according to the discovered indecies
        time = time[start_index:end_index]
        amplitude = amplitude[start_index:end_index]

        # return the truncated arrays
        return time, amplitude





