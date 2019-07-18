import csv
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from multiprocessing import Process, Queue
start = time.time()
sboxInv = [
           0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
           0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
           0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
           0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
           0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
           0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
           0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
           0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
           0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
           0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
           0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
           0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
           0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
           0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
           0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
           0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
           ]
trace = []
final_key = []
shiftedRow = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]
ciphers = [[] for i in range(16)]
correlations = [[0 for i in range(256)] for j in range(16)]
correlation_queue = Queue()

def Decipher(cipher_list, k, index):
    list1 = []
    Sboxed = []
    for i in cipher_list:
        list1.append(i ^ k)
    for g in list1:
        Sboxed.append(sboxInv[g])
    list1.clear()
    j = 0
    for x in Sboxed:
        y = ciphers[shiftedRow[index]][j]
        n = x ^ y
        h = 0
        while n:
            h += n & 1
            n >>= 1
        list1.append(h)
        j += 1
    coef = np.corrcoef(list1, trace)
    correlation_queue.put((k, coef[0][1]))

def gen_allocation(number_jobs, number_threads):
    num_range = int(number_jobs/number_threads)
    ranges = {n:(n*num_range,(n+1)*num_range) for n in range(number_threads)}
    return ranges

global allocation 
allocation = []

def process_data(tid, k_idx):
    global allocation
    for key1 in range(allocation[tid][0], allocation[tid][1]):
        Decipher(ciphers[k_idx], key1, k_idx)

if __name__ == '__main__':
    with open('PowerTraces_collected.txt') as csv_file:
        power_reader = csv.reader(csv_file, delimiter=',')
        for row in power_reader:
            trace.append(int(row[18968]))


    with open('ciphers_collected.txt') as csv_file:
        cipher_reader = csv.reader(csv_file, delimiter=' ')
        for row in cipher_reader:
            for x in range(16):
                ciphers[x].append(int(row[x], 16))

    number_threads = 8
    if len(sys.argv) > 1:
        number_threads = int(sys.argv[1])
    allocation = gen_allocation(256, number_threads)
    for i in range(16):
        ps = list()
        for j in range(number_threads):
            p = Process(target=process_data,args=(j,i))
            p.daemon = True
            p.start()
            ps.append(p)

        for j in range(number_threads):
            ps[j].join()
        while correlation_queue.empty() != True:
            a = correlation_queue.get()
            correlations[i][a[0]]=(a[1])

        final_key.append(correlations[i].index(min(correlations[i])))
    
    print(final_key)
    end = time.time()
    fig, axs = plt.subplots(4, 4)
    for i in range(4):
        for j in range(4):
            axs[i, j].plot(correlations[i*4+j])
            axs[i, j].set_title('Byte '+str(i*4+j))
    plt.show()
    print(end - start)