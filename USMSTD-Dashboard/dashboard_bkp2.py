import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



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
        self.left_frame = tk.LabelFrame(self.master, width="600", text="Summary Plot")
        self.left_frame_buttons = tk.LabelFrame(self.left_frame, width="600", text="")

        # Right Frame....
        self.right_frame = tk.LabelFrame(self.master, width="600", text="Zoomed in Plot")

        # Packing Left Frame items......
        self.left_frame_buttons.pack(side='bottom', padx=5, pady=5)
        self.left_frame.pack(side='left', expand='yes', fill='both', padx=5, pady=5)

        # Packing Right Frame items......
        self.right_frame.pack(side='right', expand='yes', fill='both', padx=5, pady=5)

        # Create Left frame buttons and packing....
        self.button_left = tk.Button(self.left_frame_buttons,text="Plot Reference data", command=self.plot_ref_data)
        self.button_left.pack(side="left")
        self.button_right = tk.Button(self.left_frame_buttons,text="Plot Current Data", command=self.plot_current_data)
        self.button_right.pack(side="left")
        self.button_zoom_in = tk.Button(self.left_frame_buttons, text="Plot Zoomed in Data", command=self.plot_zoomed_in)
        self.button_zoom_in.pack(side="left")
        self.button_clear = tk.Button(self.left_frame_buttons, text="Clear Current", command=self.clear_curr_plot_right_window)
        self.button_clear.pack(side="left")


        # Set data
        self.x_values, self.y_values = self.get_ref_data()

        self.x_values_curr = []
        self.y_values_curr = []

        # Left Frame Figure Handles
        self.fig1 = Figure()
        ax = self.fig1.add_subplot(111)
        ax.set_xlabel("Time")
        ax.set_ylabel("Amplitude")
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
        self.ax2.set_xlabel("Time")
        self.ax2.set_ylabel("Amplitude")
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
        self.ax2.plot(x_values_curr,y_values_curr, 'g-', label='Current', linewidth=1.0)
        self.after_first_time = True
        self.ax2.legend()
        self.canvas_right.draw_idle()


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




    # def plot_single_waveform(self, time, amplitude):
    #     '''
    #     see the documentation online for matplotlib.pyplot
    #     '''
    #     plt.plot(time, amplitude, 'b-', label='Current')
    #     plt.xlabel('Time (microseconds)')
    #     plt.ylabel('Amplitude (V)')
    #     plt.legend()
    #     plt.show()
    #     plt.close()

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