from time import time
from itertools import chain

time1 = 0
time2 = 0
for i in range(300):
    l = list(range(300+i))
    start = time()
    tuple(chain(l,l))
    end = time()
    time1 += end - start

    start = time()
    list(chain(l,l))
    end = time()
    time2 += end - start

print(f"tuple: {time1}, lists: {time2}")