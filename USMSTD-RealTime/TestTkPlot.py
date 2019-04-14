import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter


showleft = False
showRight = False

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

def plotGraph(x_values, y_values):
    fig_left = Figure()
    ax = fig_left.add_subplot(111)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid()
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.plot(x_values, y_values)
    return fig_left




def app():
    rootwindow = tk.Tk()
    rootwindow.geometry("1000x700")
    rootwindow.title("test plot")

    left_frame = tk.LabelFrame(rootwindow, width="1000",text="Summary Plot")

    right_frame = tk.LabelFrame(rootwindow, text="Zoomed Summary Plot")
    left_frame.pack(side='left',expand='yes',fill='both',padx=5,pady=5)
    right_frame.pack(side='left',expand='yes',fill='both',padx=5,pady=5)

    lf_button_left = tk.Button(left_frame,text="Plot Reference", command='', width=30)
    lf_button_right = tk.Button(left_frame, text="Plot Current", command='', width=30)
    lf_button_left.pack(side='bottom',padx=5,pady=5)
    lf_button_right.pack(side='bottom', padx=5, pady=5)

    L1 = tk.Label(right_frame, text="TOF" , width=30)
    L1.pack(side='bottom', padx=5, pady=5)
    # E1 = tk.Entry(right_frame, width=30)
    # E1.pack(side='bottom', padx=5, pady=5)

    TOF = 311
    t1 = tk.Text(right_frame, width=30, height=1, borderwidth=2)
    t1.pack(side='bottom', padx=5, pady=5)

    def compute_tof():
        TOF = 302
        print('helllllo')
        t1.insert('1.0', TOF)

    rf_button_left = tk.Button(right_frame, text="Compute TOF", command=compute_tof(), width=30)
    # rf_button_right = tk.Button(right_frame, text="plot-D", command='', width=30)
    rf_button_left.pack(side='bottom', padx=5, pady=5)
    # rf_button_right.pack(side='bottom', padx=5, pady=5)

    # rf_button_left.pack(side='bottom', padx=5, pady=5)
    # rf_button_right.pack(side='bottom', padx=5, pady=5)
    x_values, y_values = data_points()

    fig_left = plotGraph(x_values, y_values)


    graph = FigureCanvasTkAgg(fig_left, master=left_frame)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)

    x_values = x_values[14000:25000]
    y_values = y_values[14000:25000]
    fig_right = plotGraph(x_values, y_values)
    graph = FigureCanvasTkAgg(fig_right, master=right_frame)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)



    rootwindow.mainloop()





if __name__ == '__main__':
    app()




