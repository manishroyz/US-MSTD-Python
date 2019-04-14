import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter
import threading

flag1 = True

tof_flag = False
ref_plot_flag = False
curr_plot_flag = True
cnt = 0

def change_state():
    global ref_plot_flag
    if ref_plot_flag == True:
        ref_plot_flag = False
    else:
        ref_plot_flag = True


def plot_waveform(self, x, y):

    plt.plot(x, y)
    plt.xlabel('i am x label')
    plt.ylabel('i am y label')
    plt.show()
    plt.close()



def data_points():
    filepath = 'ref_data.avg'
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
    return my_list_x,my_list_y

# defines handle for each figure frame for plot
def plotGraph(x_values, y_values):
    figure1 = Figure()
    ax = figure1.add_subplot(111)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.grid()
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.plot(x_values, y_values)
    return figure1




def app():
    rootwindow = tk.Tk()
    rootwindow.geometry("1500x700")
    rootwindow.title("test plot")

    # Left Frame
    left_frame = tk.LabelFrame(rootwindow, width="600",  text="Summary Plot")
    left_frame_fig = tk.LabelFrame(left_frame, width="500", height="400", text="")
    left_frame_buttons = tk.LabelFrame(left_frame, width="500", text="")

    left_frame_fig.pack(side='top',expand='yes',fill='both',padx=5,pady=5)
    left_frame_buttons.pack(side='bottom', padx=5, pady=5)
    left_frame.pack(side='left', expand='yes', fill='both', padx=5, pady=5)


    def call_plotter():

        global cnt
        print(cnt)
        cnt = cnt + 1
        change_state()
        print(ref_plot_flag)
        if ref_plot_flag == True:
            x_values, y_values = data_points()
            fig_left = plotGraph(x_values, y_values)
            graph = FigureCanvasTkAgg(fig_left, master=left_frame_fig)
            graph.get_tk_widget().pack(side="top", fill='both', expand=True)


        # x_values = x_values[14000:25000]
        # y_values = y_values[14000:25000]
        # fig_right = plotGraph(x_values, y_values)
        # graph = FigureCanvasTkAgg(fig_right, master=right_frame_fig)
        # graph.get_tk_widget().pack(side="top", fill='both', expand=True)


    #Left Frame Buttons
    lf_button_left = tk.Button(left_frame_buttons, text="Plot Reference", command=lambda : call_plotter(), width=20, bg="yellow", fg="black")
    lf_button_right = tk.Button(left_frame_buttons, text="Plot Current", command='', width=20, bg="yellow", fg="black")
    lf_button_left.pack(side='left', padx=5, pady=5)
    lf_button_right.pack(side='right', padx=5, pady=5)

    # Right Frame
    right_frame = tk.LabelFrame(rootwindow, width="400", text="Zoomed Summary Plot")
    right_frame_fig = tk.LabelFrame(right_frame, width="300", height="400", text="")
    right_frame_buttons1 = tk.LabelFrame(right_frame, width="300", text="")
    #right_frame_buttons1_tof = tk.Text(right_frame_buttons1, width=30, height=1, borderwidth=2)
    right_frame_buttons1_tof_text = tk.Text(right_frame_buttons1, width=12, height=1, borderwidth=2)

    def compute_tof():

        if tof_flag == True:
            print("ddd")
            TOF = 302
            right_frame_buttons1_tof_text.insert('1.0', TOF)

    right_frame_buttons1_tof = tk.Button(right_frame_buttons1, text="Computed TOF (seconds)", command=compute_tof(), width=25 , bg="yellow", fg="black")

    right_frame_buttons1_tof_text.pack(side='right', padx=5, pady=5)
    right_frame_buttons1_tof.pack(side='left', padx=5, pady=5)
    right_frame_buttons1.pack(side='bottom', expand='yes', padx=5, pady=5)
    right_frame_fig.pack(side='top', expand='yes', fill='both', padx=5, pady=5)
    right_frame.pack(side='right', expand='yes', fill='both', padx=5, pady=5)



    # x_values = x_values[14000:25000]
    # y_values = y_values[14000:25000]
    # fig_right = plotGraph(x_values, y_values)
    # graph = FigureCanvasTkAgg(fig_right, master=right_frame_fig)
    # graph.get_tk_widget().pack(side="top", fill='both', expand=True)


    #rootwindow.bind(left_frame_buttons, call_plotter())
    rootwindow.mainloop()



if __name__ == '__main__':
    app()











