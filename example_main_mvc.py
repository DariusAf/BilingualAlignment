# -*- coding:utf-8 -*-
from mvc import *

# DEBUG

import time
import matplotlib.pyplot as plt

def graphDist(l):
    for i,s in enumerate(l):
        w = Word(s)
        for j in range(i,len(l)):
            if l[j] != s:
                print("{},{} : {}".format(s, l[j], w.dist_jaro(Word(l[j]))))


# MAIN

model = Model()
view = View()
model.mvc_link(view)

computeFromRawFiles = False

if computeFromRawFiles:
    print("-- Opening files, clustering data and saving")
    try:
        model.txt1.open_raw("../livres/HP1_fr.txt")
        model.txt2.open_raw("../livres/HP1_en.txt")
    except FileNotFound as err:
        print(err)
    except:
        print("Error")

    view.change_task("Clustering french text")
    model.txt1.process_raw()
    model.txt1.select_range(minfreq=4)
    model.txt1.cluster_data(offset=0.97)
    model.txt1.save_data("HPFR.txt")

    view.change_task("Clustering english text")
    model.txt2.process_raw()
    model.txt2.select_range(minfreq=4)
    model.txt2.cluster_data(offset=0.97)
    model.txt2.save_data("HPEN.txt")
else:
    print("-- Reading data")
    model.txt1.open_data("HPFR.txt")
    model.txt2.open_data("HPEN.txt")

print("-- Associating close words")
model.associate_words(1.5)


print("-- Tests")
print('Chat ->',model.dist_word('chat'))


view.change_task("Exporting Dictionary")
start_time = time.time()
model.compute_dictionary("Dictionnary.txt")
model.save_dists("Result.txt")
elapsed_time = time.time() - start_time
print("Done ! in {} seconds".format(elapsed_time))
