import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np



import oscillo_collection_functions

class App:
    def __init__(self, master):

        # instantiate the class in the collection functions module
        self.ocf = oscillo_collection_functions.data_collection()

        # Create a container
        self.master = master
        self.master.geometry("1500x700")
        self.master.title("USMSTD-Dashboard")
        self.after_first_time = False

        # Left Frame......
        self.left_frame = tk.LabelFrame(self.master, width="400", text="Summary Plot")
        self.left_frame_buttons = tk.LabelFrame(self.left_frame, width="300", text="")

        # Right Frame....
        self.right_frame = tk.LabelFrame(self.master, width="600", text="Zoomed in Plot")
        self.right_frame_data = tk.LabelFrame(self.right_frame, width="600", text="")
        self.right_frame_data2 = tk.LabelFrame(self.right_frame, width="600", text="")
        # self.right_frame_data3 = tk.LabelFrame(self.right_frame, width="600", text="")

        self.L1 = tk.Label(self.right_frame_data, text="Reference TOF (seconds)", width=22, font=("Helvetica", 18))
        self.L1.pack(side='left', padx=5, pady=5)
        self.t1 = tk.Text(self.right_frame_data, width=15, height=1, borderwidth=2, font=("Helvetica", 18))
        self.t1.pack(side='right', padx=5, pady=5)

        self.L2 = tk.Label(self.right_frame_data2, text="Real-Time TOF (seconds)", width=22, font=("Helvetica", 18))
        self.L2.pack(side='left', padx=5, pady=5)
        self.t2 = tk.Text(self.right_frame_data2, width=15, height=1, borderwidth=2, font=("Helvetica", 18))
        self.t2.pack(side='right', padx=5, pady=5)

        # self.L3 = tk.Label(self.right_frame_data3, text="Real-Time Temperature (C)", width=22, font=("Helvetica", 18))
        # self.L3.pack(side='left', padx=5, pady=5)
        # self.t3 = tk.Text(self.right_frame_data3, width=15, height=1, borderwidth=2, font=("Helvetica", 18))
        # self.t3.pack(side='right', padx=5, pady=5)



        # Packing Left Frame items......
        self.left_frame_buttons.pack(side='bottom', padx=5, pady=5)
        self.left_frame.pack(side='left', expand='yes', fill='both', padx=5, pady=5)

        # Packing Right Frame items......
        self.right_frame.pack(side='right', fill='both', padx=5, pady=5)
        # self.right_frame_data3.pack(side='top', expand='yes',  padx=5)
        self.right_frame_data2.pack(side='top', expand='yes',  padx=5)
        self.right_frame_data.pack(side='top', expand='yes',  padx=5)


        # Create Left frame buttons and packing....
        self.button_left = tk.Button(self.left_frame_buttons,text="Plot Reference data", command=self.plot_ref_data, width=20)
        self.button_left.pack(side="left")
        self.button_right = tk.Button(self.left_frame_buttons,text="Plot Real_Time Data", command=self.plot_current_data, width=20)
        self.button_right.pack(side="left")
        self.button_zoom_in = tk.Button(self.left_frame_buttons, text="Plot Zoomed in Data", command=self.plot_zoomed_in,  width=20)
        self.button_zoom_in.pack(side="left")
        self.button_clear = tk.Button(self.left_frame_buttons, text="Clear Real-Time Data", command=self.clear_curr_plot_right_window,  width=20)
        self.button_clear.pack(side="left")


        # Set data
        self.x_values, self.y_values = self.get_ref_data()

        self.x_values_curr = []
        self.y_values_curr = []

        # Left Frame Figure Handles
        self.fig1 = Figure()
        ax = self.fig1.add_subplot(111)
        ax.set_xlabel("Time (sec)")
        ax.set_ylabel("Amplitude (Volts)")
        ax.grid()
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        self.line, = ax.plot(self.x_values,self.y_values, linewidth=0.5)
        self.canvas = FigureCanvasTkAgg(self.fig1,master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        # Right Frame Figure Handles
        self.fig2 = Figure()
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_xlabel("Time  (sec)")
        self.ax2.set_ylabel("Amplitude (Volts)")
        self.ax2.grid()
        self.ax2.xaxis.set_ticks_position('none')
        self.ax2.yaxis.set_ticks_position('none')
        
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        self.canvas_right = FigureCanvasTkAgg(self.fig2,master=self.right_frame)
        self.canvas_right.get_tk_widget().pack(side='top', fill='both', expand=1)    


    def get_ref_data(self):

        filepath = 'Al_sample_20C_no_DL_5MHz_22dB_12_04_2019_12_18_41131601.avg'
        my_list_x = []
        my_list_y = []
        with open(filepath) as ref_data:
            line = ref_data.readline()
            cnt = 1
            while line:
                raw_out = line.strip().split()
                my_list_x.append(float(raw_out[0]))
                my_list_y.append(float(raw_out[1]))
                line = ref_data.readline()
                cnt += 1

        # Slicing data array
        end_index = [n for n, i in enumerate(my_list_x) if i > 0.000572][0]
        my_list_x = my_list_x[0:end_index]
        my_list_y = my_list_y[0:end_index]

        return my_list_x, my_list_y

    def get_current_data(self):

        filepath = 'Al_sample_75C_no_DL_5MHz_22dB_12_04_2019_17_16_33280082.avg'
        my_list_x = []
        my_list_y = []
        with open(filepath) as ref_data:
            line = ref_data.readline()
            cnt = 1
            while line:
                ##print("Line {}: {}".format(cnt, line.strip()))
                raw_out = line.strip().split()
                my_list_x.append(float(raw_out[0]))
                my_list_y.append(float(raw_out[1]))
                line = ref_data.readline()
                cnt += 1

        # Slicing data array
        end_index = [n for n, i in enumerate(my_list_x) if i > 0.000572][0]
        my_list_x = my_list_x[0:end_index]
        my_list_y = my_list_y[0:end_index]

        return my_list_x, my_list_y




    def plot_ref_data(self):
        print('In plot_ref_data...')

        #x, y = self.get_ref_data()
        # self.fig1.clear()
        self.line.set_ydata(self.y_values)
        self.canvas.draw()


    def plot_current_data(self):
        print('In plot_current_data')


        self.x_values_curr, self.y_values_curr = self.get_single_waveform()

        #self.x_values_curr, self.y_values_curr = self.get_current_data()
        #y2_new = [val + 10 for val in self.y_values_curr]

        self.line.set_ydata(self.y_values_curr)
        self.canvas.draw()

    def plot_zoomed_in(self):
        print('In plot_zoomed_in...')
        #self.x_values_curr, self.y_values_curr = self.get_single_waveform()
        #x_values, y_values = self.get_ref_data()

        x_values_curr = self.x_values_curr[20000:25000]
        y_values_curr= self.y_values_curr[20000:25000]
        x_values = self.x_values[20000:25000]
        y_values = self.y_values[20000:25000]


        if self.after_first_time == True:
            for i in range(len(self.ax2.lines)):
                self.ax2.lines.remove(self.ax2.lines[0])


        self.ax2.plot(x_values,y_values,'r-', label='Reference', linewidth=1.0)
        self.ax2.plot(x_values_curr,y_values_curr, 'g-', label='Real-Time', linewidth=1.0)
        self.after_first_time = True
        self.ax2.legend()
        self.canvas_right.draw_idle()
        self.compute_tof()


    def compute_tof(self):
        t1 = self.find_peak_time_in_window(self.x_values,self.y_values)
        print("TOF Reference:")
        print(t1)
        self.t1.delete('1.0', tk.END)
        self.t1.insert('1.0', round(t1,11))

        t2 = self.find_peak_time_in_window(self.x_values_curr, self.y_values_curr)
        print("TOF Real Time:")
        print(t2)
        self.t2.delete('1.0', tk.END)
        self.t2.insert('1.0', round(t2,11))




    def find_peak_time_in_window(self, x, y):

        # Values of x vector that bound the respective windows
        window_1_x_vals = [0.000494, 0.0004973]
        window_2_x_vals = [0.0004978, 0.0005007]
        # Vector indices for the windows
        window_1_x_indx = []
        window_2_x_indx = []

        for i in range(2):
            window_1_x_indx.append(self.slicer_index(x, window_1_x_vals[i]))
            window_2_x_indx.append(self.slicer_index(x, window_2_x_vals[i]))

        print(window_1_x_indx)
        print(window_2_x_indx)

        x_trimmed1 = x[window_1_x_indx[0]:window_1_x_indx[1]]
        y_trimmed1 = y[window_1_x_indx[0]:window_1_x_indx[1]]
        wind_1_peak_indx = self.find_indx_for_max_amplitude(y_trimmed1, window_1_x_indx[0])

        print('wind_1_peak_amp corresponding time')
        print(x[wind_1_peak_indx])
        print('wind_1_peak_amp')
        print(y[wind_1_peak_indx])

        x_trimmed2 = x[window_2_x_indx[0]:window_2_x_indx[1]]
        y_trimmed2 = y[window_2_x_indx[0]:window_2_x_indx[1]]

        # self.plot_single_waveform(x_trimmed1,y_trimmed1)
        # self.plot_single_waveform(x_trimmed2,y_trimmed2)


        wind_2_peak_indx = self.find_indx_for_max_amplitude(y_trimmed2, window_2_x_indx[0])

        print('wind_2_peak_amp corresponding time')
        print(x[wind_2_peak_indx])
        print('wind_2_peak_amp')
        print(y[wind_2_peak_indx])
        if isinstance(y, np.ndarray):
            time = x[wind_2_peak_indx][0] - x[wind_1_peak_indx][0]
        else:
            time = x[wind_2_peak_indx] - x[wind_1_peak_indx]
        return time


    def find_indx_for_max_amplitude(self,y, ref_indx):

        max_value = max(y)

        print(type(y))
        if isinstance(y, np.ndarray):
            print("yes")
            max_index = np.where(y == max_value)
            print(max_index)
            wind_max_indx = ref_indx + max_index[0]
        else:
            max_index = y.index(max_value)
            wind_max_indx = ref_indx + max_index
        return wind_max_indx

    def slicer_index(self, my_list, val):
        index = [n for n, i in enumerate(my_list) if i > val][0]
        return index




    def clear_curr_plot_right_window(self):
        print(self.after_first_time)
        if self.after_first_time == True and self.ax2.lines[1]:
            self.ax2.lines.remove(self.ax2.lines[1])
            self.canvas_right.draw_idle()


    def get_single_waveform(self):

        print("IN get_single_waveform..")
        # This method collects a single waveform from the oscilloscope

        #retrieve the oscilloscope object handle
        scope = self.ocf.setup_scope()

        #set the vertical scale to the desired value
        self.ocf.scope_change_zoom(scope,5)

        #retrieve the waveform, time axis, trigger point, and horizontal scale
        time, amplitude, xzero, xincr = self.ocf.retrieve_waveform(scope)
        print(xzero)
        #self.ocf.plot_waveform(time,amplitude)

        time, amplitude = self.ocf.clip_tails(time, amplitude, xzero, xincr, 7e-4)
        print(amplitude[1])

        # Slicing data array
        end_index = [n for n, i in enumerate(time) if i > 0.000572][0]
        time = time[0:end_index]
        amplitude = amplitude[0:end_index]

        return time, amplitude




    def plot_single_waveform(self, time, amplitude):
        '''
        see the documentation online for matplotlib.pyplot
        '''
        plt.plot(time, amplitude, 'b-', label='Current')
        plt.xlabel('Time (microseconds)')
        plt.ylabel('Amplitude (V)')
        plt.legend()
        plt.show()
        plt.close()

    # def plot_both_waveform(self, time, amplitude):
    #     '''
    #     see the documentation online for matplotlib.pyplot
    #     '''
    #     plt.plot(time, amplitude, 'b-', label='Current')
    #     plt.plot(self.x_values,self.y_values,'r-', label='Reference')
    #     plt.xlabel('Time (microseconds)')
    #     plt.ylabel('Amplitude (V)')
    #     plt.legend()
    #     plt.show()
    #     plt.close()




root = tk.Tk()
app = App(root)
root.mainloop()