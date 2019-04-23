#
# # seed the pseudo random number generator
# from random import seed
# from random import random
# from random import randint
#
# # seed random number generator
# seed(1)
# # generate some random numbers
# print(random(), random(), random())
#
# # reset the seed
# seed(1)
# # generate some random numbers
# print(random(), random(), random())
#
# # generate some integers
# for i in range(10):
#     # interval[start,stop] ---->randint(0, 10)
#     value = randint(0, 15)
#     print(value, end=" ")


from numpy.random import seed
from numpy.random import randint
from numpy.random import shuffle

# seed random number generator
seed(1)
# generate some integers (start,stop, number_of_vals)
# values = randint(0, 10, 20)
# print(values)

sequence = [i for i in range(20)]
print(sequence)
# randomly shuffle the sequence
shuffle(sequence)
print(sequence)
