# -*- coding:utf-8 -*-
from mvc import *

# DEBUG

import time


def graph_dist(l):
    for i, s in enumerate(l):
        w = Word(s)
        for j in range(i, len(l)):
            if l[j] != s:
                print("{},{} : {}".format(s, l[j], w.dist_jaro(Word(l[j]))))


# MAIN

model = Model()
view = View()
controller = Controller()
link_mvc(model, [view], controller)

computeFromRawFiles = True

if computeFromRawFiles:
    print("-- Opening files, clustering data and saving")
    try:
        model.txt1.open_raw("livres/MIS_fr.txt")
        model.txt2.open_raw("livres/MIS_en.txt")
    except FileNotFound as err:
        print(err)

    view.change_task("Clustering french text")
    model.txt1.process_raw()
    model.txt1.select_range(minfreq=20)
    # model.txt1.cluster_data(offset=0.97)
    model.txt1.save_data("MISFR.txt")

    view.change_task("Clustering english text")
    model.txt2.process_raw()
    model.txt2.select_range(minfreq=20)
    # model.txt2.cluster_data(offset=0.97)
    model.txt2.save_data("MISEN.txt")
else:
    print("-- Reading data")
    model.txt1.open_data("data/MISFR.txt")
    model.txt2.open_data("data/MISEN.txt")

print(len(model.txt1.data))

print("-- Associating close words")
model.associate_words(1.5)

#print("-- Tests")
print('Avion ->', model.dist_word('avion'))


def write_dist(s):
    model.dist_word(s)
    a = sorted(model._distWords[s], key=lambda w: model._distWords[s][w], reverse=True)
    for p in a:
        print(p, "->", model._distWords[s][p])


print("-- Exporting Dictionary")
view.change_task("Exporting Dictionary")
start_time = time.time()
model.compute_dictionary("dictMIS.csv")
# model.save_dists("Result.txt")
elapsed_time = time.time() - start_time
print("Done ! in {} seconds".format(elapsed_time))
