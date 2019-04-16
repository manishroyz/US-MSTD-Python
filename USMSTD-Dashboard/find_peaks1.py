
import peakutils as pu
import matplotlib.pyplot as plt

def slicer_index (my_list, val):
    index = [n for n, i in enumerate(my_list) if i > val][0]
    return index


def get_ref_data():
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


def find_peak(amplitude):

    peak_indicies = pu.indexes(amplitude, thres = .2)

    return max(peak_indicies)


def find_peak_locations():
    print(' ')



x,y = get_ref_data()

# plt.plot(x, y)
# plt.xlabel('Time (microseconds)')
# plt.ylabel('Amplitude (V)')
# plt.show()
# plt.close()

# Values of x vector that bound the respective windows
window_1_x_vals = [0.000494, 0.0004973]
window_2_x_vals = [0.0004978, 0.0005007]
# Vector indices for the windows
window_1_x_indx = []
window_2_x_indx = []

for i in range(2):
    window_1_x_indx.append(slicer_index(x, window_1_x_vals[i]))
    window_2_x_indx.append(slicer_index(x, window_2_x_vals[i]))

print(window_1_x_indx)
print(window_2_x_indx)

x_trimmed1 = x[window_1_x_indx[0]:window_1_x_indx[1]]
y_trimmed1 = y[window_1_x_indx[0]:window_1_x_indx[1]]

x_trimmed2 = x[window_2_x_indx[0]:window_2_x_indx[1]]
y_trimmed2 = y[window_2_x_indx[0]:window_2_x_indx[1]]

# plt.plot(x_trimmed1, y_trimmed1)
# plt.plot(x_trimmed2, y_trimmed2)
#
# plt.xlabel('Time (microseconds)')
# plt.ylabel('Amplitude (V)')
# plt.show()
# plt.close()

max_value = max(y_trimmed1)
max_index = y_trimmed1.index(max_value)

x_loc = window_1_x_indx[0]+max_index
x_val = x[x_loc]
print(x_val)
# peaks = []
# peaks = find_peak(y_trimmed1)