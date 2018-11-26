'''
@author Manish Roy

This module is the crux of using Oscillo(TM) as a developer. It contains all of the major
collection and processing methods for the software package. It is the second highest in the
calling heirarchy (second only to the GUI). From this module, you can manipulate and use all the
other modules to achieve customized and automated collection and processing of data. This module
contains proceedures that I used most commonly while developing Oscillo(TM). Although this module
contains many ready-to-use proceedures, it is completely open module, meaning that new proceedures
can and should be added to it as future developers and researchers see fit.

This module is organized into classes to group methods according to their function. 

Each method and class is documented in detail, and each line includes a comment that delineates its contribution
to the overal functionality of the method.
'''

'''
Import the libraries needed to execute the methods in this module.
'''

#Import the collection functions. (See the oscillo_collection_functions.py module.)
import oscillo_collection_functions
#Import the data processing funtions (See the oscillo_data_processing_functinos.py module.)
import oscillo_data_processing_functions
#Import time. This is a module that allows python to execute certain commands in real time.
import time as t
#Import the threading module. This allows some of the slower processes to be executed in the background
import _thread as th
#Import the plotting library. This is a very useful library for developers. (See the matplotlib.pyplot documentation online.)
import matplotlib.pyplot as plt
#Import numpy. This library contains many methods used in vectorized calculations, and other
# operations involving arrays.
import numpy as np
#Import the module that contains the dialog box functions. Any dialog box seen in Oscillo(TM) is created in this module.
# (see the oscillo_option_windows.py module.)
import oscillo_option_windows as oow
import os



class Raw_waveforms():
    '''
    This class contains the method that collects and saves raw, unprocessed waveforms.
    '''

    def __init__(self,rootwindow,strvar):
        '''
        This method is executed when the class is instantiated. It serves as a platform for 
        inheriting the GUI window and the string varible from the message center. It is also a
        place where various other classes from other modules can be instantiated.
        '''

        #inherit the window from the GUI
        self.rootwindow = rootwindow
        #inherit the string variable fromt the message center
        self.strvar = strvar
        #instantiate the class in the collection functions module
        self.osf = oscillo_collection_functions.data_collection(self.rootwindow,self.strvar)
        #instantiate teh class in the data processing functions module
        self.odf = oscillo_data_processing_functions.data_process(self.rootwindow,self.strvar)
        
    def myprint(self,text):
        '''
        This method is alot like the built-in print() method in python. But instead of 
        "printing" the text to the terminal, it displays it in the GUI message center.
        '''
        #Set the inherited string variable to the new text.
        self.strvar.set(text)
        #update the GUI window so that the text immediately appears.
        self.rootwindow.update()

    def single_waveform(self):

        '''
        This method collects a single waveform from the oscilloscope, plots it for the
        user to see, and then prompts the user if they want to save it. 
        '''

        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()

        #set the vertical scale to the desired value
        self.osf.scope_change_zoom(scope,5)

        #retrieve the waveform, time axis, trigger point, and horizontal scale
        time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
        print(xzero)
        #clip off the superfluous data.
        time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 7e-4)

        #plot the data for the user to see
        self.osf.plot_waveform(time,amplitude)
        
        #ask the user if they want to save the collected waveform
        saveme = oow.get_value(self.rootwindow, "Would you like to save this waveform?",'yn').show()

        #if the user wants to save the waveform...
        if saveme == 'y':
            #ask the user for the parameters of the collection
            metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters","parameters").show()
            #create a directory for the new data file
            path_name = self.osf.make_directory(metal, DL, freq, gain)
            #save the new data to file
            self.osf.save_me(path_name, time, amplitude, metal, DL, freq, gain)
        
        self.myprint("Waveform(s) collected successfully")
 
    def multiple_waveforms(self):

        '''
        This method can collect multiple waveforms without intermediate instructions. It is useful in the case
        where the user needs to collect a large sample of waveforms because the user only needs to initiate the method
        and then check back on it later when the collection is complete.
        '''

        #ask the user how many waveforms they want to collect. (This must be an integer number.)
        n = oow.get_value(self.rootwindow, "How many waveforms would you like to colleect?",'int').show()
        #ask the user for the parameters of the collection
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters","parameters").show()
        #create a directory for the new data file
        path_name = self.osf.make_directory(metal, DL, freq, gain)
        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()
        #set the vertical scale to the desired value
        self.osf.scope_change_zoom(scope,5)

        '''
        This loop collects and saves the waveforms one-at-a-time until it has collected the desired number of waveforms. 
        It then breaks, and the program returns to the main menu.
        '''
        #create a counting variable
        i = 1
        #set the looping condition.
        while i <= n:
            #retrieve the waveform, time axis, trigger point, and horizontal scale
            time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            #clip off the superfluous data.
            time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 5.22e-4)
            #save the data in the background so that the loop can continue collecting data.
            th.start_new_thread(self.osf.save_me,(path_name, time, amplitude, metal, DL, freq, gain))
            
            self.myprint('Waveform #{} collected and saving'.format(i))
            
            #increment the counting variable
            i += 1

        self.myprint("Waveform(s) collected successfully. Data will\n\
        continue to save for several minutes.")

    def continuous_waveform(self):

        '''
        This method collects and saves raw waveforms for a specified ammount of time and at a specified
        rate of collection. This method can be useful if the user wants to collect waveforms over the course
        of a few hours, but doesn't want to spend all of that time in the lab clicking a collect button.
        Once this method is initiated, it will collect at the specified rate until the collection time is 
        expired, and then it will return to the main menu. 
        '''

        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()    

        #ask the user to specify the duration of the collection
        duration = oow.get_value(self.rootwindow, "For how many minutes would you like to collect?",'int').show()
        #ask the user to specify the rate of data collection
        rate = oow.get_value(self.rootwindow, "How many waveforms per minute would you like to collect?",'int').show()
        #ask the user for the parameters of the collection
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters.",'parameters').show()
        #create a directory for the new data file
        path_name = self.osf.make_directory(metal, DL, freq, gain)

        #create time references
        then = t.time()
        now = t.time()

        #scale the duration to seconds
        duration = duration * 60

        #scale the interval between measurements. 60s is one minute.
        interval = 60 / rate

        #create a counting variable
        i = 1
        '''
        This loop will run until the current run time exceeds the collection duration
        specified by the user. 
        '''
        while (now - then) < duration:
            
            #retrieve the current time
            now = t.time()

            #computre the current run time, and see if it is time to collect a waveform. 
            if (now - then) % interval < 0.9:
                
                #retrieve the waveform, time axis, trigger point, and horizontal scale
                time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
                #clip off the superfluous data.
                time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 5.22e-4)
                #save the data in the background so that the loop can continue collecting data.
                th.start_new_thread(self.osf.save_me,(path_name, time, amplitude, metal, DL, freq, gain))
                
                self.myprint('Waveform #{} collected and saving'.format(i))
                
                #increment the counting variable
                i += 1
                #This loop runs way too fast for the if statement above to be effective by itself.
                # So I slowed it down here by having the program sleep (wait) for 1 second before it
                # continues through the loop.
                t.sleep(1)
        
        self.myprint("Waveform(s) collected successfully. Data will\n\
        continue to save for several minutes.")

class Processed_waveforms():
    '''
    This class contains several methods that collect and process waveforms. In most 
    cases, these methods don't wave the processed data, but rather they save the output
    of any calculations made using the collected data. 
    '''

    def __init__(self,rootwindow,strvar):
        '''
        This method is executed when the class is instantiated. It serves as a platform for 
        inheriting the GUI window and the string varible from the message center. It is also a
        place where various other classes from other modules can be instantiated.
        '''

        #inherit the window from the GUI
        self.rootwindow = rootwindow
        #inherit the string variable fromt the message center
        self.strvar = strvar
        #instantiate the class in the collection functions module
        self.osf = oscillo_collection_functions.data_collection(self.rootwindow,self.strvar)
        #instantiate teh class in the data processing functions module
        self.odf = oscillo_data_processing_functions.data_process(self.rootwindow,self.strvar)

    def myprint(self,text):
        '''
        This method is alot like the built-in print() method in python. But instead of 
        "printing" the text to the terminal, it displays it in the GUI message center.
        '''
        #Set the inherited string variable to the new text.
        self.strvar.set(text)
        #update the GUI window so that the text immediately appears.
        self.rootwindow.update()

    def average_waveform(self):

        '''
        This method collects several waveforms and then averages them.
        This procedure is often useful for atenuating noise in data. The method
        askes the user how many waveforms should be involved in each average, and
        then it collects that many waveforms on a loop before averaging them. 
        '''

        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()

        #Ask user how many waveforms should be averaged
        n = oow.get_value(self.rootwindow, "How many waveforms would you like to collect and average?",'int').show()
        #ask the user for the parameters of the collection
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters.",'parameters').show()
        #create a directory for the new data file
        path_name = self.osf.make_directory(metal, DL, freq, gain)


        #create lists to store the data to be averaged
        times = []
        amplitudes = []

        #collect waveforms in loop.
        for i in range(n):

            #retrieve the waveform, time axis, trigger point, and horizontal scale
            time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            #clip off the superfluous data.
            time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 5.22e-4)

            #Append the time array to the list of time arrays
            times.append(time)
            #Append the amplitude array to the list of amplitude arrays
            amplitudes.append(amplitude)

            self.myprint("Collected waveform #{}".format(i+1))

        #compute average in data processing module
        time, amplitude = self.odf.compute_average(times,amplitudes)

        #plot averaged data
        self.osf.plot_waveform(time, amplitude)
        
        #save the data in a new thread
        th.start_new_thread(self.osf.save_me,(path_name, time, amplitude, metal, DL, freq, gain))

        self.myprint("Waveforms collected successfully")

    def gaussian_timing(self):

        '''
        This method involves a timing technique that was developed during the development of Oscillo(TM). It 
        performs a descrete convolution between the amplitude data and a gaussian curve. The product of the 
        convolution is then used to find the time location of the various features in the signal. Once these
        time locations are discovered, subtraction is used to determine the time of flight between 
        echogenic features.

        The architecture of this method is similar to that of the multiple_waveforms() method in the
        Raw_waveforms() class in that it performs its operations on a specified number of waveforms. This 
        itterative techinique is useful because the user can initiate the method, tell it to collect 30 waveforms,
        and go do something else while the collection and processing occurs. The calculated times of flight from these
        30 waveforms can then be used to calculate a mean and run significance tests. 
        '''

        #Ask user how many waveforms to collect and process
        n = oow.get_value(self.rootwindow, "How many waveforms would you like to colleect?",'int').show()
        #ask the user for the parameters of the collection
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters","parameters").show()
        #create a directory for the new data file
        path_name = self.osf.make_directory(metal, DL, freq, gain)
        #create a new time stamp
        mytime = self.osf.get_time_stamp()
        #name the new data file
        file_name_csv = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime + ".csv"
        #open the new data file for writing
        myfile = open(file_name_csv,'w')

        #create a dictionary to contain the peaks obtained from the convolution
        peaks = {}
        #write column headers to the file
        myfile.write("fwg, s1, s2, s3, s4\n")

        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()

        #create a counting variable
        i = 1
        #this loop will run until the specified number of waveforms have been collected and processed.
        while i <= n:
            
            #set the vertical zoom factor to the desired value
            self.osf.scope_change_zoom(scope,0.5)
            #retrieve the waveform, time axis, trigger point, and horizontal scale
            time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            #clip off the superfluous data.
            time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 5.22e-4)
                      
            
            #compute the envelope of the amplitude data
            A_of_t = self.odf.compute_envelope(amplitude)

            #zero the ends of the envelope to avoid error
            A_of_t = self.odf.clip_envelope(A_of_t)

            #Plot the amplitude and envelope. This shoud be commented out 
            '''
            plt.plot(time, amplitude, 'b', time, A_of_t,"r")
            plt.show()
            '''

            #Convolve the envelope with a gaussian function of the same size produces
            # a graph whose peaks are very easy to find. Each index in 'peaks' is
            # the index corresponding to the instance of a feature in the waveguide.
            sigma = 1.9 #this is the standard deviation of the gaussian function used in the convolution
            peaks, cc, x_axis = self.odf.gausian_convolution(A_of_t,sigma,.01, 2500)

            #correct for the error in the initial bang
            tof = peaks[8] - peaks[4]
            tofsudo = peaks[4] - peaks[0]
            dt = tof - tofsudo
            peaks[0] = peaks[0] - dt


            #Now that we have a very consistant number of peaks, we can use them to
            # find the time of flight between the features. Each peak represents an 
            # echo off of an echogenic feature. The first peak is the initial bang,
            # and the peaks that follow conform to the order that the echogenic features
            # appear on the waveguide. Remember that the peaks are numbered from zero, as
            # is the convention in python.
            #The next few lines take the data from the peaks list and creates a list of the 
            # times of flight between echogenic features.
            times_of_flight = ['','','','','']
            times_of_flight[0] = (peaks[4] - peaks[0]) * xincr #TOF for full wave guide in seconds
            j = 0
            while j <= 3:
                times_of_flight[j+1] = (peaks[j+1] - peaks[j]) * xincr #TOF for a segment of the waveguide in seconds
                j += 1


            
            #Write these times of flight to a file.
            for item in times_of_flight:
                myfile.write('{},'.format(item))
            myfile.write("\n")

            print("Collected and wrote data set {}.".format(i))
            i += 1


        #close the data file
        myfile.close()
        print()
        print("Waveform(s) collected successfully.")
        self.myprint("Waveform(s) collected successfully")

    def gaussian_timing_zoom(self):

        '''
        This method employs the same paradigm as the method called gaussian_timing, but it adds the feature of using
        different vertical axis scales for different features in the signal. This serves to augment the resolution
        in the smaller features and at the same time prevent the larger features from being clipped.
        '''

        #Ask user how many waveforms to collect and process
        n = oow.get_value(self.rootwindow, "How many waveforms would you like to colleect?",'int').show()
        #ask the user for the parameters of the collection
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters","parameters").show()
        #create a directory for the new data file
        path_name = self.osf.make_directory(metal, DL, freq, gain)
        #create a new time stamp
        mytime = self.osf.get_time_stamp()
        #name the new data file
        file_name_csv = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime + ".csv"
        #open the new data file for writing
        myfile = open(file_name_csv,'w')

        
        #create a dictionary to contain the peaks obtained from the convolution
        peaks = {}
        #write column headers to the file
        myfile.write("fwg, s1, s2, s3, s4\n")

        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()

        #create a counting variable
        i = 1
        #this loop will run until the specified number of waveforms have been collected and processed.
        while i <= n:
            
            #retrieve waveform zoomed out
            self.osf.scope_change_zoom(scope,10) #change this back to 5 for the waveguide
            time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 5.22e-4)
            
            #retrieve waveform zoomed in
            self.osf.scope_change_zoom(scope,0.5)
            ztime, zamplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            ztime, zamplitude = self.odf.clip_tails(ztime, zamplitude, xzero, xincr, 5.22e-4)           
            
            #compute the envelopes
            A_of_t = self.odf.compute_envelope(amplitude)
            zA_of_t = self.odf.compute_envelope(zamplitude)

            #zero the ends of the envelope to avoid error
            A_of_t = self.odf.clip_envelope(A_of_t)
            zA_of_t = self.odf.clip_envelope(zA_of_t)

            '''
            #These plotting tools can be useful during development
            plt.plot(time, amplitude, 'b', time, A_of_t,"r")
            plt.show()
            plt.plot(ztime,zamplitude,'b',ztime, zA_of_t, 'r')
            plt.show()
            '''

            #Correlating the envelope with a gaussian function of the same size produces
            # a graph whose peaks are very easy to find. Each index in 'peak_indexes' is
            # the index corresponding to the instance of a feature in the waveguide.
            sigma = 1.8
            peak_indexes, cc, x_axis = self.odf.gausian_convolution(A_of_t,sigma,.1, 2500)
            zpeak_indexes, zcc, zx_axis = self.odf.gausian_convolution(zA_of_t,sigma, .05, 2500)

            #I now have 2 sets of peaks, from the zoomed-out set, I need to extract the
            # peaks of the distal-end echos. From the zoomed-in set, I need to extract
            # the peaks of the smaller echogenic features.
            j = 0
            while j <= 8:
                
                if j == 0 or j == 4 or j == 8:
                    k = int(j/4)
                    peaks[j] = peak_indexes[k]
                
                else:
                    peaks[j] = zpeak_indexes[j]
                
                j += 1

            #correct for the error in the initial bang
            tof = peaks[8] - peaks[4]
            tofsudo = peaks[4] - peaks[0]
            dt = tof - tofsudo
            peaks[0] = peaks[0] - dt


            #Now that we have a very consistant number of peaks, we can use them to
            # find the time of flight between the features. Each peak represents an 
            # echo off of an echogenic feature. The first peak is the initial bang,
            # and the peaks that follow conform to the order that the echogenic features
            # appear on the waveguide. Remember that the peaks are numbered from zero, as
            # is the convention in python.
            times_of_flight = ['','','','','']
            times_of_flight[0] = (peaks[4] - peaks[0]) * xincr #TOF for full wave guide in seconds
            j = 0
            while j <= 3:
                times_of_flight[j+1] = (peaks[j+1] - peaks[j]) * xincr #TOF for a segment of the waveguide in seconds
                j += 1


            
            #Write these times of flight to a file.
            for item in times_of_flight:
                myfile.write('{},'.format(item))
            myfile.write("\n")

            print("Collected and wrote data set {}.".format(i))
            i += 1

        #close the data file.
        myfile.close()
        print()
        print("Waveform(s) collected successfully.")
        self.myprint("Waveform(s) collected successfully")

    def cross_correlation_envelopes_zoom(self):

        '''
        This method aims to acheive the same goal as other timing methods. It discovers the time locations
        of the features of interest in the signal. Then a copy of the envelope is made for each feature. These
        copies are used to isolate the feature (zeroing out the rest of the signal) so that two features can
        be cross-correlated with each other. The cross correlation produces a graph with a single peak. The
        position of that peak is indicative of the time shift required to obtain the highest degree of correlation
        between the features. This time shift is sinonymous with the time of flight.

        Again, this method performs the given operation on a specified number of waveforms.
        '''

        #Ask user how many waveforms to collect and process
        n = oow.get_value(self.rootwindow, "How many waveforms would you like to colleect?",'int').show()
        #ask the user for the parameters of the collection
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters","parameters").show()
        #create a directory for the new data file
        path_name = self.osf.make_directory(metal, DL, freq, gain)
        #create a new time stamp
        mytime = self.osf.get_time_stamp()
        #name the new data file
        file_name_csv = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime + ".csv"
        #open the new data file for writing
        myfile = open(file_name_csv,'w')

        
        #create a dictionary to contain the peaks obtained from the convolution
        peaks = {}
        #write column headers to the file
        myfile.write("fwg, s1, s2, s3, s4\n")

        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()

        #create a counting variable
        i = 1
        #this loop will run until the specified number of waveforms have been collected and processed.
        while i <= n:
            
            #retrieve waveform zoomed out
            self.osf.scope_change_zoom(scope,10) #change this back to 5 for the waveguide
            time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 5.22e-4)
            
            #retrieve waveform zoomed in
            self.osf.scope_change_zoom(scope,0.5)
            ztime, zamplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            ztime, zamplitude = self.odf.clip_tails(ztime, zamplitude, xzero, xincr, 5.22e-4)           
            
            #compute the envelopes
            self.myprint("Processing Data. This could take up\n\
                         to a 60 seconds")
            A_of_t = self.odf.compute_envelope(amplitude)
            zA_of_t = self.odf.compute_envelope(zamplitude)

            #zero the ends of the envelope to avoid error
            A_of_t = self.odf.clip_envelope(A_of_t)
            zA_of_t = self.odf.clip_envelope(zA_of_t)
            
            '''
            #these plotting tools are useful during development
            plt.plot(time, amplitude, 'b', time, A_of_t,"r")
            plt.show()
            plt.plot(ztime,zamplitude,'b',ztime, zA_of_t, 'r')
            plt.show()
            '''

            #Correlating the envelope with a gaussian function of the same size produces
            # a graph whose peaks are very easy to find. Each index in 'peak_indexes' is
            # the index corresponding to the instance of a feature in the waveguide.
            sigma = 1.8
            peak_indexes, cc, x_axis = self.odf.gausian_convolution(A_of_t,sigma,.1, 2500)
            zpeak_indexes, zcc, zx_axis = self.odf.gausian_convolution(zA_of_t,sigma, .05, 2500)

            #I now have 2 sets of peaks, from the zoomed-out set, I need to extract the
            # peaks of the distal-end echos. From the zoomed-in set, I need to extract
            # the peaks of the smaller echogenic features.
            j = 0
            while j <= 8:
                
                if j == 0 or j == 4 or j == 8:
                    k = int(j/4)
                    peaks[j] = peak_indexes[k]
                
                else:
                    peaks[j] = zpeak_indexes[j]
                
                j += 1

            times_of_flight = ['','','','','']


            #these are the time locations of the distal end features
            DE1 = peaks[4] * xincr - xzero
            DE2 = peaks[8] * xincr - xzero

            #now I need to find these time locations on the original spectrum.
            # I do this by buffering the time location of the feature of 
            # interest and then using the numpy.where method.
            buffer = xincr
            DE1min = DE1 - buffer
            DE1max = DE1 + buffer
            DE2min = DE2 - buffer
            DE2max = DE2 + buffer

            DE1 = np.where(np.logical_and(time <= DE1max, time >= DE1min))
            DE2 = np.where(np.logical_and(time <= DE2max, time >= DE2min))

            #extract integer from tuple and array
            while type(DE1) != type(np.int64(4)):
                DE1 = DE1[0]
            while type(DE2) != type(np.int64(4)):
                DE2 = DE2[0]

            #now I have the indecies if the two distal features along the
            # temporal axis. With these, I am going to zero everything
            # except a few microseconds in each direction along the temporal
            # axis.
            DE1_env = np.copy(A_of_t)
            DE2_env = np.copy(A_of_t)  

            half_width =  500#in indecies

            DE1_env[DE1+half_width:] = 0
            DE1_env[:DE1-half_width] = 0
            
            DE2_env[:DE2-half_width] = 0
            DE2_env[DE2+half_width:] = 0

            '''
            #plotting tools that are useful during developement
            plt.plot(time,amplitude,'k')
            plt.plot(time,A_of_t,'b')
            plt.plot(time,DE1_env,'g')
            plt.plot(time,DE2_env,'r')
            plt.show()
            '''

            #With these zero-padded, isolated segments of the envelope, I can perform
            # a cross correlation, find the peaks of this cross correlation, and from
            # that, determine the TOF for a complete round trip.
            peak_indexes = self.odf.cross_correlate(DE1_env, DE2_env)
            index_shift = (int(len(time)/2) - peak_indexes[0])
            times_of_flight[0] = index_shift * xincr
            
            #correct for the error in the initial bang
            peaks[0] = peaks[4] - index_shift
            


            
            #this just graphs the shifted waveform features
            DE2_env = DE2_env[index_shift:]
            zero_pad = np.zeros(index_shift)
            DE2_env = np.concatenate((DE2_env,zero_pad))
            '''
            plt.plot(time,DE2_env,'b',time,DE1_env,'r.')
            plt.show()
            '''
            

            j = 1 #if you start this at zero, it will cause problems. Start it at 1
            while j <= 4:

                '''
                The architecture of this loop is almost identical to that of the code
                preceeding it. The only difference is that now the operation is being
                performed on the smaller features.
                '''

                #these are the time locations of the features of interest
                f1 = peaks[j] * xincr - xzero
                f2 = peaks[j+1] * xincr - xzero

                #now I need to find these time locations on the original spectrum
                buffer = xincr
                f1min = f1 - buffer
                f1max = f1 + buffer
                f2min = f2 - buffer
                f2max = f2 + buffer

                f1 = np.where(np.logical_and(time <= f1max, time >= f1min))
                f2 = np.where(np.logical_and(time <= f2max, time >= f2min))

                #extract integer from tuple and array
                while type(f1) != type(np.int64(4)):
                    f1 = f1[0]
                while type(f2) != type(np.int64(4)):
                    f2 = f2[0]

                #now I have the indecies if the two along the
                # temporal axis. With these, I am going to zero everything
                # except a few microseconds in each direction along the temporal
                # axis.
                half_width =  500 #in indecies
                if j == 4:
                    f1_env = np.copy(A_of_t)
                    f2_env = np.copy(zA_of_t)
                    half_width = 1500 #this case needs a larger window

                elif j == 3:
                    f1_env = np.copy(zA_of_t)
                    f2_env = np.copy(A_of_t)

                else:
                    f1_env = np.copy(zA_of_t)
                    f2_env = np.copy(zA_of_t)  

                f1_env[f1+half_width:] = 0
                f1_env[:f1-half_width] = 0

                f2_env[:f2-half_width] = 0
                f2_env[f2+half_width:] = 0

                '''
                plt.plot(time,zamplitude,'k')
                plt.plot(time,zA_of_t,'b')
                plt.plot(time,f1_env,'g')
                plt.plot(time,f2_env,'r')
                plt.show()
                '''
                

                #With these zero-padded, isolated segments of the envelope, I can perform
                # a cross correlation, find the peaks of this cross correlation, and from
                # that, determine the TOF for a complete round trip.
                peak_indexes = self.odf.cross_correlate(f1_env, f2_env)
                index_shift = (int(len(time)/2) - peak_indexes[0])
                times_of_flight[j] = index_shift * xincr
                


                
                #this just graphs the shifted waveform features
                f2_env = f2_env[index_shift:]
                zero_pad = np.zeros(index_shift)
                f2_env = np.concatenate((f2_env,zero_pad))
                '''
                plt.plot(time,f2_env,'b',time,f1_env,'r.')
                plt.show()
                '''

                j += 1
                




            
            #Write these times of flight to a file.
            for item in times_of_flight:
                myfile.write('{},'.format(item))
            myfile.write("\n")

            print("Collected and wrote data set {}.".format(i))
            
            i += 1

        #close the data file
        myfile.close()
        print()
        print("Waveform(s) collected successfully.")
        self.myprint("Waveform(s) collected successfully")

    def cross_correlation_waveforms_average_old_data(self):

        '''
        This method aims to acheive the same goal as other timing methods, but using a proceedure that we believe to
        be much more precise and acurate. It discovers the time locations
        of the features of interest in the signal. Then a copy of the waveform is made for each feature. These
        copies are used to isolate the feature (zeroing out the rest of the signal) so that two features can
        be cross-correlated with each other. The cross correlation produces a graph whose highest peak is 
        indicative of the time shift required to obtain the highest degree of correlation
        between the features. This time shift is sinonymous with the time of flight.

        Again, this method performs the given operation on a specified number of waveforms.
        '''

        #Ask user how many waveforms to collect and process
        n = oow.get_value(self.rootwindow, "How many waveforms would you like to colleect?",'int').show()
        #ask the user for the parameters of the collection
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters","parameters").show()
        #create a directory for the new data file
        path_name = self.osf.make_directory(metal, DL, freq, gain)
        #create a new time stamp
        mytime = self.osf.get_time_stamp()
        #name the new data file
        file_name_csv = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime + ".csv"
        #open the new data file for writing
        myfile = open(file_name_csv,'w')

        
        #create a dictionary to contain the peaks obtained from the convolution
        peaks = {}
        #write column headers to the file
        myfile.write("s1, s2, s3, s4, fwg\n")

        #retrieve the oscilloscope object handle
        scope = self.osf.setup_scope()
        #set the zoom of the oscilloscope
        self.osf.scope_change_zoom(scope,10)

        #create a counting variable
        i = 1
        #this loop will run until the specified number of waveforms have been collected and processed.
        
        while i <= n:

            #collect 10 waveforms and average them
            times = []
            amplitudes = []
            j = 1
            k = 10
            while j <= k:
                #retrieve waveform from oscilloscope
                time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
                
                #append to the lists of lists
                times.append(time)
                amplitudes.append(amplitude)
                j += 1
                self.myprint("Collected subset {} of {}".format(j,k))
            
            time, amplitude = self.odf.compute_average(times, amplitudes)
            time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 5.22e-4)
            
            plt.plot(time,amplitude)
            plt.show()

            
            self.myprint("Processing Data. This could take up\n\
                         to a 60 seconds")
            
            #compute the envelopes
            A_of_t = self.odf.compute_envelope(amplitude)

            #zero the ends of the envelope to avoid error
            A_of_t = self.odf.clip_envelope(A_of_t)
            
            #plt.plot(time, amplitude, 'b', time, A_of_t,"r")
            #plt.show()
            #plt.plot(ztime,zamplitude,'b',ztime, zA_of_t, 'r')
            #plt.show()

            #Correlating the envelope with a gaussian function of the same size produces
            # a graph whose peaks are very easy to find. Each index in 'peak_indexes' is
            # the index corresponding to the instance of a feature in the waveguide.
            sigma = 1.4
            peaks, cc, x_axis = self.odf.gausian_convolution(A_of_t,sigma,0, 3000)
            
            times_of_flight = ['','','','','']

            
            #these are the time locations of the distal end features
            DE1 = peaks[4] * xincr - xzero #4 for no DL, 3 for DL
            DE2 = peaks[8] * xincr - xzero #8 for no DL, 7 for DL

            #now I need to find these time locations on the original spectrum
            buffer = xincr
            DE1min = DE1 - buffer
            DE1max = DE1 + buffer
            DE2min = DE2 - buffer
            DE2max = DE2 + buffer

            DE1 = np.where(np.logical_and(time <= DE1max, time >= DE1min))
            DE2 = np.where(np.logical_and(time <= DE2max, time >= DE2min))

            #extract integer from tuple and array
            while type(DE1) != type(np.int64(4)):
                DE1 = DE1[0]
            while type(DE2) != type(np.int64(4)):
                DE2 = DE2[0]

            #now I have the indecies if the two distal features along the
            # temporal axis. With these, I am going to zero everything
            # except a few microseconds in each direction along the temporal
            # axis.
            DE1_env = np.copy(amplitude)
            DE2_env = np.copy(amplitude)  

            half_width =  500#in indecies

            DE1_env[DE1+half_width:] = 0
            DE1_env[:DE1-half_width] = 0
            
            DE2_env[:DE2-half_width] = 0
            DE2_env[DE2+half_width:] = 0
            
            
            plt.plot(time,amplitude,'k')
            #plt.plot(time,A_of_t,'b')
            plt.plot(time,DE1_env,'g')
            plt.plot(time,DE2_env,'r')
            plt.show()
            
            
            
            #With these zero-padded, isolated segments of the envelope, I can perform
            # a cross correlation, find the peaks of this cross correlation, and from
            # that, determine the TOF for a complete round trip.
            peak_indexes = self.odf.cross_correlate(DE1_env, DE2_env)
            index_shift = (int(len(time)/2) - peak_indexes[0])
            times_of_flight[4] = index_shift * xincr

            
            #this just graphs the shifted waveform features
            DE2_env = DE2_env[index_shift:]
            zero_pad = np.zeros(index_shift)
            DE2_env = np.concatenate((DE2_env,zero_pad))
            
            
            plt.plot(time,DE2_env,'b',time,DE1_env,'r.')
            plt.show()
            
            

            j = 0 #start at 0 for no DL and 3 for DL
            while j <= 3: #3 for no DL and 6 for DL
                
                #these are the time locations of the features of interest
                f1 = peaks[j] * xincr - xzero
                f2 = peaks[j+1] * xincr - xzero


                #now I need to find these time locations on the original spectrum
                buffer = xincr
                f1min = f1 - buffer
                f1max = f1 + buffer
                f2min = f2 - buffer
                f2max = f2 + buffer

                f1 = np.where(np.logical_and(time <= f1max, time >= f1min))
                f2 = np.where(np.logical_and(time <= f2max, time >= f2min))

                #extract integer from tuple and array
                while type(f1) != type(np.int64(4)):
                    f1 = f1[0]
                while type(f2) != type(np.int64(4)):
                    f2 = f2[0]

                #now I have the indecies if the two along the
                # temporal axis. With these, I am going to zero everything
                # except a few microseconds in each direction along the temporal
                # axis.
                half_width =  500 #in indecies
                if j == 0: #The first segment gets its own special treatment
                    f1 = peaks[j+1] * xincr - xzero
                    f2 = peaks[j+4] * xincr - xzero

                    #now I need to find these time locations on the original spectrum
                    buffer = xincr
                    f1min = f1 - buffer
                    f1max = f1 + buffer
                    f2min = f2 - buffer
                    f2max = f2 + buffer

                    f1 = np.where(np.logical_and(time <= f1max, time >= f1min))
                    f2 = np.where(np.logical_and(time <= f2max, time >= f2min))

                    #extract integer from tuple and array
                    while type(f1) != type(np.int64(4)):
                        f1 = f1[0]
                    while type(f2) != type(np.int64(4)):
                        f2 = f2[0]

                    f1_env = np.copy(amplitude)
                    f2_env = np.copy(amplitude)

                else:
                    f1_env = np.copy(amplitude)
                    f2_env = np.copy(amplitude)  
                
                f1_env[f1+half_width:] = 0 
                f1_env[:f1-half_width] = 0

                f2_env[:f2-half_width] = 0
                f2_env[f2+half_width:] = 0 

                
                plt.plot(time,amplitude,'k')
                plt.plot(time,f1_env,'g')
                plt.plot(time,f2_env,'r')
                plt.show()
                
                

                #With these zero-padded, isolated segments of the envelope, I can perform
                # a cross correlation, find the peaks of this cross correlation, and from
                # that, determine the TOF for a complete round trip.
                peak_indexes = self.odf.cross_correlate(f1_env, f2_env)
                index_shift = (int(len(time)/2) - peak_indexes[0])

                
                
                if j == 0: #again, the first segment gets special treatment
                    times_of_flight[j] = times_of_flight[4] - index_shift * xincr
                
                else:
                    
                    times_of_flight[j] = index_shift * xincr

                
                #this just graphs the shifted waveform features
                f2_env = f2_env[index_shift:]
                zero_pad = np.zeros(index_shift)
                f2_env = np.concatenate((f2_env,zero_pad))
                
                plt.plot(time,f2_env,'b',time,f1_env,'r.')
                plt.show()
                

                j += 1
            
            #Write these times of flight to a file.
            for item in times_of_flight:
                myfile.write('{},'.format(item))
            myfile.write("\n")

            print("Collected and wrote data set {}.".format(i))
            
            i += 1

        myfile.close()
        print()
        print("Waveform(s) collected successfully.")
        self.myprint("Waveform(s) collected successfully")
    

class Calibration_processes():

    def __init__(self,rootwindow,strvar):
        self.rootwindow = rootwindow
        self.strvar = strvar
        self.use_previouse_reference()
        self.osf = oscillo_collection_functions.data_collection(self.rootwindow,self.strvar)
        self.odf = oscillo_data_processing_functions.data_process(self.rootwindow,self.strvar)
        return

    def myprint(self,text):
        self.strvar.set(text)
        self.rootwindow.update()

    def use_previouse_reference(self):

        ref_file = open("reference.txt","r")
        ref_line = ref_file.readline()
        self.ref_values = ref_line.split(',')

        for index in range(len(self.ref_values)):
            self.ref_values[index] = int(self.ref_values[index])
            
        self.ref_values = np.array(self.ref_values)

    def create_new_reference(self):

        answer = oow.get_value(self.rootwindow, "Are you sure you want to create a new reference?",'yn').show()

        if answer == 'y':

            #ref_temp = oow.get_value(self.rootwindow, "What is the temperature of the new reference?",'int').show()

            ref_file = open("ref4.csv","w") #change back to reference.txt after development

            #The waveform from the waveguide in the furnace is collected here.
            scope = self.osf.setup_scope()
            scope.write("DATA:RESOLUTION REDUCED") #this is to see if I can make the processing on the long wave guides any faster.
            self.osf.scope_change_zoom(scope,5) #this should be .5 for the 3d prints
            time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)
            '''
            plt.plot(time, amplitude)
            plt.show()
            '''
            #clip off the undeeded portions of the waveform
            #time, amplitude = self.odf.clip_tails(time, amplitude, xzero, xincr, 9e-4)
            #if you collect a reduced waveform, the this method is not necessary. The oscilloscope clips the tails off for you.
            '''
            plt.plot(time, amplitude)
            plt.show()
            '''
            #Compute the envelope of the waveform
            A_of_t = self.odf.compute_envelope(amplitude)

            #zero the ends of the envelope to prevent convolution artifacts
            A_of_t = self.odf.clip_envelope(A_of_t)
            '''
            plt.plot(time, amplitude)
            plt.plot(time,A_of_t)
            plt.show()
            '''
            #convolve the envelope with a gaussian of the same size and retrieve the 
            # index location of the peaks
            #peaks = self.odf.gausian_convolution(A_of_t, 1.8, 0, 2500) #these are parameters for the 3dprints
            peaks = self.odf.gausian_convolution(A_of_t, .5, 0, 10) #these are parameters for the longer waveguides

            #write the list of peaks to the reference file for future use
            mystring = ''
            for peak in peaks:
                string_peak = str(peak)
                mystring = mystring + string_peak + ","
            mystring = mystring[:len(mystring)-1]
            ref_file.write("{}".format(mystring))

            self.myprint("The new reference has been collected and created.\n\
                        You may need to restart the program before the new\n\
                        reference can be used.")

    def distinguish_peaks(self):


        #ref_temp = oow.get_value(self.rootwindow, "What is the temperature of the new reference?",'int').show()

        ref_file = open("heated_peaks.csv","a+") #change back to reference.txt after development
        
        #The waveform from the waveguide in the furnace is collected here.
        scope = self.osf.setup_scope()
        scope.write("DATA:RESOLUTION REDUCED") #this is to see if I can make the processing on the long wave guides any faster.
        scope.write("ZOOM:ZOOM1:HORIZONTAL:POSITION 61")
        scope.write("ZOOM:MODE 1")
        scope.write("ZOOM:ZOOM1:STATE 1")
        scope.write("ZOOM:ZOOM1:SCALE 2E-5")
        self.osf.scope_change_zoom(scope,2) #this should be .5 for the 3d prints
        
        #answer = oow.get_value(self.rootwindow, "Are you ready to collect the first waveform?",'yn').show()
        #create time references
        then = t.time()
        now = t.time()

        #scale the duration to seconds
        duration = 10 #minutes
        duration = duration * 60

        #create a counting variable
        j = 0
        '''
        This loop will run until the current run time exceeds the collection duration
        specified by the user. 
        '''
        while (now - then) < duration:
            
            #retrieve the current time
            now = t.time()

            #create data lists
            times = []
            amplitudes = []

            n = 5
            for i in range(n):

                time, amplitude, xzero, xincr = self.osf.retrieve_waveform(scope)

                times.append(time)
                amplitudes.append(amplitude)

                self.myprint("Collected waveform #{}".format(i+1))

            #compute average in data processing module
            time, amplitude = self.odf.compute_average(times,amplitudes)

            #split the spectrum into two parts for separate analysis
            #first make copies of the time and amplitude arrays
            time1 = np.copy(time)
            amplitude1 = np.copy(amplitude)
            time2 = np.copy(time)
            amplitude2 = np.copy(amplitude)
            time3 = np.copy(time)
            amplitude3 = np.copy(amplitude)

            #cut the arrays
            cutpoint1 = int(3*(len(time)/4))
            cutpoint2 = int(7*(len(time)/8))
            time1 = time1[:cutpoint1]
            amplitude1 = amplitude1[:cutpoint1]
            time2 = time2[cutpoint1:cutpoint2]
            amplitude2 = amplitude2[cutpoint1:cutpoint2]
            time3 = time3[cutpoint2:]
            amplitude3 = amplitude3[cutpoint2:]
            
            #clip off the undeeded portions of the waveform
            time1, amplitude1 = self.odf.clip_tails(time1, amplitude1, 1.4e-5, xincr, len(time1)*xincr)          

            #Compute the envelope of the waveform
            A_of_t1 = self.odf.compute_envelope(amplitude1)
            A_of_t2 = self.odf.compute_envelope(amplitude2)
            A_of_t3 = self.odf.compute_envelope(amplitude3)

            #there is an ideal ammount of filtering that produces a consistent number of peaks. This ideal ammount of 
            # filtering is different every time you turn on the instrument and replace the transducer. These loops run 
            # on the start up of this method and they find the optimal value for sigma.

            if j == 0:
                self.myprint("Adjusting Filtering Settings.\n\
                            This could take a few seconds.")
                sigma1 = .01
                sigma2 = .01
                sigma3 = .5
                threshold1 = 0
                threshold2 = 0 #.54
                threshold3 = 0
                len1 = []
                len2 = []
                len3 = []
                count1 = 18
                count2 = 5
                count3 = 4
                
                m = 0
                while True:
                    
                    peaks1, cc1, x_axis1 = self.odf.gausian_convolution(A_of_t1, sigma1, threshold1, 0)
                    len1.append(len(peaks1))
                    if len1[m] == count1 and len1[m-1000] == count1:
                        break
                    elif len(peaks1) < count1:
                        print("overshot")
                        sigma1 -= .01
                    else:
                        sigma1 += .001
                    m += 1
                
                m = 0
                while True:
                    
                    peaks2, cc2, x_axis2 = self.odf.gausian_convolution(A_of_t2, sigma2, threshold2, 0)
                    len2.append(len(peaks2))
                    if len2[m] == count2 and len2[m-1400] == count2:
                        break
                    elif len(peaks2) < count2:
                        sigma2 -= .01
                    else:
                        sigma2 += .001
                    m += 1

                m = 0
                while True:
                    
                    peaks3, cc3, x_axis3 = self.odf.gausian_convolution(A_of_t3, sigma3, threshold3, 0)
                    len3.append(len(peaks3))
                    if len3[m] == count3 and len3[m-3000]:
                        break
                    elif len(peaks3) < count3:
                        sigma3 -= .01
                    else:
                        sigma3 += .001
                    m += 1
                
                self.myprint("Adjustments finished.")
                
            
            else:
                peaks1, cc1, x_axis1 = self.odf.gausian_convolution(A_of_t1, sigma1, threshold1, 0)
                peaks2, cc2, x_axis2 = self.odf.gausian_convolution(A_of_t2, sigma2, threshold2, 0)
                peaks3, cc3, x_axis3 = self.odf.gausian_convolution(A_of_t3, sigma3, threshold3, 0)
            
            if j == 0:
                #plotting stuff for development
                #find the threshold point
                mymax = self.odf.max_of_array(cc1)
                mymin = self.odf.min_of_array(cc1)
                myrange = mymax - mymin
                mythres = myrange * threshold1

                for index in peaks1:
                    plt.plot(x_axis1[index], cc1[index],'r.') 

                plt.plot(x_axis1,cc1)
                plt.show()
                plt.close()

                #plotting stuff for development
                #find the threshold point
                mymax = self.odf.max_of_array(cc2)
                mymin = self.odf.min_of_array(cc2)
                myrange = mymax - mymin
                mythres = myrange * threshold2
                
                for index in peaks2:
                    plt.plot(x_axis2[index], cc2[index],'r.') 

                plt.plot(x_axis2,cc2)
                plt.show()
                plt.close()

                #plotting stuff for development
                #find the threshold point
                mymax = self.odf.max_of_array(cc3)
                mymin = self.odf.min_of_array(cc3)
                myrange = mymax - mymin

                for index in peaks3:
                    plt.plot(x_axis3[index], cc3[index],'r.') 

                plt.plot(x_axis3,cc3)
                plt.show()
                plt.close()
                adjust = oow.get_value(self.rootwindow, "Do you need to adjust the transducer?",'yn').show()
                if adjust == 'y':
                    return
                

            ref_file = open("heated_peaks.csv","a+") #change back to reference.txt after development
            
            #join the three arrays of peaks
            for index in range(len(peaks2)):
                peaks2[index] = peaks2[index] + peaks1[len(peaks1)-1]
            for index in range(len(peaks3)):
                peaks3[index] = peaks3[index] + peaks2[len(peaks2)-1]
            
            print(len(peaks1))
            print(len(peaks2))
            print(len(peaks3))
            peaks = np.concatenate((peaks1,peaks2,peaks3))

            '''
            #check to make sure there are the correct number of peaks
            print(len(peaks))
            if len(peaks) != 33:
                self.myprint("Wrong number of peak. Trying again...")
                continue
            '''

            #write the list of peaks to the reference file for future use
            mystring = ''
            for peak in peaks:
                string_peak = str(peak)
                mystring = mystring + string_peak + ","
            mystring = mystring[:len(mystring)-1]
            ref_file.write("{}\n".format(mystring))
            ref_file.close()
            
            '''
            #write the convolution to the reference file
            mystring = ''
            for value in cc:
                string_value = str(value)
                mystring = mystring + string_value + ","
            mystring = mystring[:len(mystring)-1]
            ref_file.write("{}\n".format(mystring))
            '''
            
            self.myprint("Finished collection {}".format(j))
            j += 1
            
            
            
            
            


        self.myprint("Heating test concluded.")
        ref_file.close()
        

    def Gaussian_calibration(self):

        '''
        This function is intended for the process of calibrating the
        temperature sensing technology. It waits for a signal from the 
        furnace saying that the desired temperature has been reached,
        It then calculates the dt shift of each waveform peak relative
        to the time position of each waveform peak on the reference 
        waveform.
        '''

        #create the file and path to save the data that is going to be collected
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters","parameters").show()
        path_name = self.osf.make_directory(metal, DL, freq, gain)
        mytime = self.osf.get_time_stamp()
        file_name_csv = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime + ".csv"
        myfile = open(file_name_csv,'w')


        #Write the column headers to the file.
        myfile.write('temp,dt1,dt2,dt3,dt4,dt5')
        
        answer = oow.get_value(self.rootwindow, "Are you ready to collect the first waveform?",'yn').show()
        
        while answer == 'y':

            '''
            Things to automate:
                -Temperautre input
                -Collection trigger
                -termination of sequence recognition 
            '''
            #from the user, obtain the temperatures of each of the segments
            '''I need to automate this eventually'''
            temp = oow.get_value(self.rootwindow, "Enter the temperatures of the collection.",'int').show()
            #temps = temps.split(',')

            #The waveform from the waveguide in the furnace is collected here.
            scope = self.osf.setup_scope()
            time, volts, xzero, xincr = self.osf.retrieve_waveform(scope)

            #clip off the undeeded portions of the waveform
            time, amplitude = self.odf.clip_tails(time, volts, xzero, xincr, 5.22e-4)

            #Compute the envelope of the waveform
            A_of_t = self.odf.compute_envelope(amplitude)

            #zero the ends of the envelope to prevent convolution artifacts
            A_of_t = self.odf.clip_envelope(A_of_t)

            #convolve the envelope with a gaussian of the same size and retrieve the 
            # index location of the peaks
            peaks = self.odf.gausian_convolution(A_of_t, 1.8, 0, 2500)

            #Find the dt between the peaks of the refrence waveform and the 
            # collected waveform
            dts = []
            for j in range(len(peaks)):
                #this is the time shift in seconds due to the temperature change.
                dt = (peaks[j] - self.ref_values[j])
                dts.append(dt)

            #Write these time shifts (dts) to file--correlating them with the
            # temperature measured by the thermocouples.
            myfile.write("{},".format(temp))
            for j in range(len(dts)):
                myfile.write("{},".format(dts[j]))
            myfile.write("\n")

            #wait for the user to be ready to collect the next waveform
            '''I need to automate this eventually'''
            answer = oow.get_value(self.rootwindow, "Do you need to collect another waveform?",'yn').show()

class Temperautre_sensing():

    def __init__(self,rootwindow,strvar):
        self.rootwindow = rootwindow
        self.strvar = strvar
        self.use_previouse_reference()
        self.osf = oscillo_collection_functions.data_collection(self.rootwindow,self.strvar)
        self.odf = oscillo_data_processing_functions.data_process(self.rootwindow,self.strvar)
        return

    def myprint(self,text):
        self.strvar.set(text)
        self.rootwindow.update()

    def use_previouse_reference(self):

        ref_file = open("reference.txt","r")
        ref_line = ref_file.readline()
        self.ref_values = ref_line.split(',')

        for index in range(len(self.ref_values)):
            self.ref_values[index] = int(self.ref_values[index])
            
        self.ref_values = np.array(self.ref_values)
        
    def gaussian_sensing(self):

        '''
        This function is intended for the process of calibrating the
        temperature sensing technology. It waits for a signal from the 
        furnace saying that the desired temperature has been reached,
        It then calculates the dt shift of each waveform peak relative
        to the time position of each waveform peak on the reference 
        waveform.
        '''
        
        #setup instrument
        scope = self.osf.setup_scope()    

        #input data-collection parameters
        duration = oow.get_value(self.rootwindow, "For how many minutes would you like to collect?",'int').show()
        rate = oow.get_value(self.rootwindow, "How many waveforms per minute would you like to collect?",'int').show()
        metal, DL, freq, gain = oow.get_value(self.rootwindow, "Please fill out the following parameters.",'parameters').show()
        mytime = self.osf.get_time_stamp()
        path_name = self.osf.make_directory(metal, DL, freq, gain)
        file_name_csv = path_name + "\\" + metal  + "_" + DL + "_" + freq + "_" + gain + "_" + mytime + ".csv"
        myfile = open(file_name_csv,'w')
        self.osf.scope_change_zoom(scope,0.5)

        #Write the column headers to the file.
        myfile.write('temp')

        #create time references
        then = t.time()
        now = t.time()

        #scale the duration to seconds
        duration = duration * 60

        #scale the interval between measurements. 60s is one minute.
        interval = 60 / rate

        i = 1
        while (now - then) < duration:

            now = t.time()

            if (now - then) % interval < 0.9:

                #temps = temps.split(',')

                #The waveform from the waveguide in the furnace is collected here.
                time, volts, xzero, xincr = self.osf.retrieve_waveform(scope)

                #clip off the undeeded portions of the waveform
                time, amplitude = self.odf.clip_tails(time, volts, xzero, xincr, 5.22e-4)

                #Compute the envelope of the waveform
                A_of_t = self.odf.compute_envelope(amplitude)

                #zero the ends of the envelope to prevent convolution artifacts
                A_of_t = self.odf.clip_envelope(A_of_t)

                #convolve the envelope with a gaussian of the same size and retrieve the 
                # index location of the peaks
                peaks = self.odf.gausian_convolution(A_of_t, 1.8, 0, 2500)

                #Find the dt between the peaks of the refrence waveform and the 
                # collected waveform
                dts = []
                for j in range(len(peaks)):
                    #this is the time shift in seconds due to the temperature change.
                    dt = (peaks[j] - self.ref_values[j])
                    dts.append(dt)

                T = 0.3699*dts[4] + 24.681

                self.myprint("{} 'C".format(T))
                myfile.write('{}\n'.format(T))
                    
                i += 1
                t.sleep(1)

        myfile.close()
        self.myprint("Temperature collection complete.")


