'''
@author Manish Roy

This module contains the majority of the functions used in processing the data aquired from
the oscilloscope. Each method is documented in detail and each line is commented to 
delineate its contribution to the overal functionality of the method.
'''

'''
Here, the libraries needed to execute these methods are imported
'''
#Import numpy. This library contains many methods used in vectorized calculations, and other
# operations involving arrays.
import numpy as np
#Import the plotting library. This is a very useful library for developers. (See the matplotlib.pyplot documentation online.)
import matplotlib.pyplot as plt
#This library contains the method used to compute the hilbert transform used in envelope calculations.
import scipy.fftpack as fft
#math is a library that contains many other useful mathematical operations and functions.
import math
#Import the threading module. This allows some of the slower processes to be executed in the background
import _thread as th
#Peak utils is a library that makes it possible to easily find the peaks of a function or discrete data.
import peakutils as pu
#Import time. This is a module that allows python to execute certain commands in real time.
import time as t

class data_process():

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

    def clip_tails(self, time, amplitude, xzero, xincr, xend):
        '''
        Since the "RESOLUTION FULL" setting on the oscilloscope returns a lot of superfluous
        data, this method is necessary to clip most of that uneeded data off. Failing to clip
        off the uneeded data can really bog down some of the processes since the operations will
        be performed on 1 million data points instead of a few hundred thousand.
        '''
        
        #The absolute value of the data trigger point is established
        xzero = abs(xzero)
        #in order to find the location of this trigger point using the numpy.where method,
        # this value has to be buffered.
        zero_buffer = xincr
        zeromin = xzero - zero_buffer
        zeromax = xzero + zero_buffer

        #this method returns the index of the time array where the trigger point was found.
        start_index = np.where(np.logical_and(time <= zeromax, time >= zeromin))

        #extract integer from tuple and array
        while type(start_index) != type(np.int64(4)):

            start_index = start_index[0]

        #the same process is repeated with the ending index, except in this case, the ending index is
        # arbitrary. The developer can select it based on how much of the waveform they want to work with.
        end_buffer = xincr
        endmin = xend - end_buffer
        endmax = xend + end_buffer

        end_index = np.where(np.logical_and(time <= endmax, time >= endmin))
        
        #extract integer from tuple and array
        while type(end_index) != type(np.int64(4)):

            end_index = end_index[0]



        #truncate arrays according to the discovered indecies
        time = time[start_index:end_index]
        amplitude = amplitude[start_index:end_index]

        #return the truncated arrays
        return time, amplitude

    def clip_envelope(self, myarray):
        '''
        Due to a phenomenon that I am not familiar with, the calculation of the envelope always
        results in a sudden spike on the ends of the signal. These spikes can cause artifacts
        in further signal processing, so these spikes are zeroed in this method.
        '''

        #number of indecies that need to be zero
        n = 80
        #create an array of zeros
        zeros = np.zeros(n)
        #replace the front end of the signal with zeros
        myarray[:n] = zeros
        #replace the back end of the signal with zeros
        myarray[len(myarray)-n:] = zeros

        #return the modified array
        return myarray

    def plot_existing_data(self):
        '''
        This is an all-in-one function that can be used to plot data from an existing 
        file. All that you need to do is add the path name of the file you want to plot.
        '''

        #specify the path of the data file
        path = "nothing yet" #come finish this function later
        #extract the data from the file
        mydata = np.genfromtxt(path, delimiter = ',')
        #transpose the data into horizontal arrays
        mydata = np.transpose(mydata)

        #extract the two arrays from the array of arrays
        time = mydata[0]
        amplitude = mydata[1]

        #plot the data in the arrays.
        plt.plot(time,amplitude)
        plt.show()
        plt.close()

    def compute_average(self, times, amplitudes):
        '''
        Due to the noise frequently observed in the data collection, it has proven
        useful to collect various waveforms and then average them point-by-point.
        This method acomplished that.
        '''
        self.myprint("Computing Average...")

        #first an array of zeros is made to hold the sum of the time arrays
        t_sum = np.zeros(len(times[0]))
        #this loop adds all of the time arrays up point-by-point using a vectorized calculation
        for i in range(len(times)):
            t_sum = t_sum + times[i]
        #the sum is then divided by the number of arrays that were summed--producing an average
        time = t_sum/(i+1)

        #the same process is then repeated for the amplitude arrays
        a_sum = np.zeros(len(amplitudes[0]))
        for i in range(len(amplitudes)):
            a_sum = a_sum + amplitudes[i]
        amplitude = a_sum/(i+1)

        #return the averaged arrays
        return time, amplitude

    def compute_envelope(self, amplitude):
        '''
        This method computes the envelope of the waveform. The method used here is described
        in Dr. Skliar's paper entitled "Anisotropic Diffusion Filter for Robust Timing of
        Ultrasound Echoes"
        '''

        #compute the hilbert of amplitude
        h_amp = fft.hilbert(amplitude)

        #compute the envelope "see the method in the paper for more detail."
        A_of_t = (amplitude**2 + h_amp**2)**(1/2)

        #return the envelope
        return A_of_t

    def moving_average(self, amplitude):
        '''
        Although no longer in use, this method is a very standard, well-known, and useful filtering
        technique. I left it here in case anyone finds a use for it in the future. It performs a 
        moving average of the input data. For a deeper understanding of this, look up "moving average"
        online.
        '''

        pamp = np.copy(amplitude)

        window_size = 3 #this should always be a positive odd integer

        window = np.ones(window_size)/window_size
        average = np.convolve(amplitude,window,mode = 'same')

        return average

    def itterative_moving_average(self, amplitude,n):

        for i in range(n):
            amplitude = moving_average(amplitude)
        
        return amplitude

    def mode_of_array(self,myarray):

        bins = {}
        for key in myarray:
            try:
                bins[key] = bins[key] + 1
            except:
                bins[key] = 1

        count = 0
        for key in bins:
            
            if count < bins[key]:
                count = bins[key]
                mode = key
        
        return mode

    def max_of_array(self,myarray):

        maximum = myarray[0]
        for item in myarray:
            if item > maximum:
                maximum = item
            else:
                pass
        
        return maximum

    def min_of_array(self,myarray):

        minimum = myarray[0]
        for item in myarray:
            if item < minimum:
                minimum = item
            else:
                pass
        
        return minimum

    def peaks_fingerprint(self, peaks):

        fingerprint = []
        try:
            for index in range(len(peaks)):
                fingerprint.append(peaks[index+1]-peaks[index])
        except:
            pass
                
        fingerprint = np.array(fingerprint)
        return fingerprint

    def average_TOF(self, peak_indexes,j,n):

        TOF = 0
        i = 1
        while i <= n:
            TOF = TOF + (peak_indexes[j+1] - peak_indexes[j])
            j += 4
            i += 1
        TOF = TOF / n

        return TOF

    def find_peak(self, amplitude):

        peak_indicies = pu.indexes(amplitude, thres = .1, min_dist = 2000)

        return peak_indicies

    def auto_correlate(self, myarray):

        cc = np.correlate(myarray, myarray, mode = "full")
        x_axis = np.arange(0,len(cc))
        
        #find the peaks of the auto-cross-correlation graph
        #for 3D prints, I think I used thres = 0 and min_dist = 3000
        peak_indexes = pu.indexes(cc, thres = .8, min_dist = 3000)

        '''
        #plotting stuff for development
        for index in peak_indexes:
            plt.plot(x_axis[index], cc[index],'r.') 

        plt.plot(x_axis,cc)
        plt.show()

        return(peak_indexes)
        '''

    def gausian_convolution(self, myarray,c,threshold,mindist):


        #create an array of integers that represent the domain of the 
        # gaussian. These will be used as an axis to compute the 
        # y values of the gaussian function
        myx = np.linspace(-100,100,len(myarray))

        '''
        *************useful values for c**************
        For 3D-printed aluminum waveguide, c=1.8
        '''
        
        #compute the y values of the gaussian function.
        gaus = np.exp(-(myx**2) / (2 * c**2))
        
        #plot the gaussian curve with the envelope
        #plt.plot(myx, myarray, 'r', myx, gaus, 'b')
        #plt.show()

        
        #convolve the gaussian function with the envelope
        cc = np.correlate(myarray, gaus, mode = "same")
        x_axis = np.arange(0,len(cc))

        
        #find the peaks of the auto-cross-correlation graph
        #for 3D prints, I think I used thres = 0 and min_dist = 2500
        #for the stair stepping standard, thres = .1 and min_dist = 500
        peak_indexes = pu.indexes(cc, thres = threshold, min_dist = mindist)
        
        
        #plotting stuff for development
        for index in peak_indexes:
            plt.plot(x_axis[index], cc[index],'r.') 

        plt.plot(x_axis,cc)
        plt.show()
        
        #plt.savefig("{}.png".format(c))
        plt.close()
        
        

        return(peak_indexes,cc, x_axis)

    def sinusoidal_convolution(self, myarray,c,threshold,mindist):


        #create an array of integers that represent the domain of the 
        # sinusoidal function. These will be used as an axis to compute the 
        # y values of the function
        myx = np.linspace(-100,100,len(myarray))

        '''
        *************useful values for c**************
        For 3D-printed aluminum waveguide, c=1.8
        '''
        
        #compute the y values of the sinusoidal function.
        
        gaus = 10 * np.exp(-(myx**2) / (2 * c)) * np.sin(myx)
        
        #plot the sinusoidal curve with the envelope
        plt.plot(myx, myarray, 'r', myx, gaus, 'b')
        plt.show()

        
        #convolve the sinusoidal function with the envelope
        cc = np.correlate(myarray, gaus, mode = "same")
        x_axis = np.arange(0,len(cc))

        
        #find the peaks of the graph
        #for 3D prints, I think I used thres = 0 and min_dist = 2500
        #for the stair stepping standard, thres = .1 and min_dist = 500
        peak_indexes = pu.indexes(cc, thres = threshold, min_dist = mindist)

        
        #plotting stuff for development
        for index in peak_indexes:
            plt.plot(x_axis[index], cc[index],'r.') 

        plt.plot(x_axis,cc)
        plt.show()
        
        

        return(peak_indexes)

    def cross_correlate(self, array1, array2):

        cc = np.correlate(array1, array2, mode = "same")
        x_axis = np.arange(0,len(cc))
        
        #find the peaks of the auto-cross-correlation graph
        #for 3D prints, I think I used thres = 0 and min_dist = 3000
        peak_indexes = pu.indexes(cc, thres = 0, min_dist = 3000)
        
        '''
        #plotting stuff for development
        for index in peak_indexes:
            plt.plot(x_axis[index], cc[index],'r.') 

        plt.plot(x_axis,cc)
        plt.show()
        '''
        
        return(peak_indexes)