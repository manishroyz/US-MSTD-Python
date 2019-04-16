import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class App:
    def __init__(self, master):
        # Create a container
        self.master = master
        self.master.geometry("1500x700")
        self.master.title("USMSTD-Dashboard")
        self.windows = [[]]

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


        # Set data
        self.x_values, self.y_values = self.get_ref_data()
        self.x_values_curr = []
        self.y_values_curr = []

        self.fig1 = Figure()
        ax = self.fig1.add_subplot(111)
        ax.set_xlabel("Time")
        ax.set_ylabel("Amplitude")
        ax.grid()
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        #ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        self.line, = ax.plot(self.x_values,self.y_values)
        self.canvas = FigureCanvasTkAgg(self.fig1,master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        
        
        
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

        self.x_values_curr, self.y_values_curr = self.get_current_data()
        #y2_new = [val + 10 for val in self.y_values_curr]

        self.line.set_ydata(self.y_values_curr)
        self.canvas.draw()

    def plot_zoomed_in(self):
        print('In plot_zoomed_in...')
        x_values_curr, y_values_curr = self.get_current_data()
        x_values, y_values = self.get_ref_data()
        x_values_curr = x_values_curr[20000:25000]
        y_values_curr=y_values_curr[20000:25000]
        x_values=x_values[20000:25000]
        y_values=y_values[20000:25000]
        self.ax2.plot(x_values,y_values)
        self.ax2.plot(x_values_curr,y_values_curr)
        
        self.canvas_right.draw_idle()




root = tk.Tk()
app = App(root)
root.mainloop()