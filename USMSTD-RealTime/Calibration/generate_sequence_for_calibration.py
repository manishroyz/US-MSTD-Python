from numpy.random import seed
from numpy.random import shuffle


# Creates a map for all the Temperature values to be used for calibration curve
def create_temp_mapper(temp_min, temp_max, temp_interval):

    # List of Temperature data points based on the Temperature range and interval
    temp_list = list(range(temp_min, temp_max+1, temp_interval))
    temp_index_map = {i+1:x for i,x in enumerate(temp_list)}
    # print(temp_list)
    # print(temp_index_map)

    return temp_index_map

#
def get_random_exp_seq(temp_index_map):
    l = len(temp_index_map)
    sequence = [i for i in range(1,l+1)]
    # randomly shuffle the sequence
    shuffle(sequence)
    print(sequence)

    return sequence




temp_min = 50
temp_max = 1000
temp_interval = 50

temp_index_map = create_temp_mapper(temp_min, temp_max, temp_interval)
shuffled_sequence = get_random_exp_seq(temp_index_map)
shuffled_temp_sequence = []

print("Order of Temperature -data collection is:")
for x in shuffled_sequence:
    shuffled_temp_sequence.append(temp_index_map.get(x))

print(shuffled_temp_sequence)