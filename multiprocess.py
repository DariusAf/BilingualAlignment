# multiprocessing

# -*- coding:utf-8 -*-
import multiprocessing
from mvc import *
import time

# MAIN

if __name__ == '__main__':
    model = Model()
    view = View()
    controller = Controller()
    link_mvc(model, [view], controller)
    
    computeFromRawFiles = True
    
    if computeFromRawFiles:
        print("-- Opening files, clustering data and saving")
        try:
            model.txt1.open_raw("../livres/HP1_fr.txt")
            model.txt2.open_raw("../livres/HP1_en.txt")
        except FileNotFound as err:
            print(err)
    
        view.change_task("Clustering french text")
        model.txt1.process_raw()
        model.txt1.select_range(minfreq=4)
        # model.txt1.cluster_data(offset=0.97)
        model.txt1.save_data("HPFR.txt")
    
        view.change_task("Clustering english text")
        model.txt2.process_raw()
        model.txt2.select_range(minfreq=4)
        # model.txt2.cluster_data(offset=0.97)
        model.txt2.save_data("HPEN.txt")
    else:
        print("-- Reading data")
        model.txt1.open_data("HPFR.txt")
        model.txt2.open_data("HPEN.txt")
    
    print("-- Associating close words")
    model.associate_words(1.5)
    
    
    print("-- Exporting Dictionary")
    view.change_task("Exporting Dictionary")
    start_time = time.time()
    
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=model.compute_dictionary, args=("dict{}.csv".format(i)), kwargs={'nb_process':5,'process_number':i})
        jobs.append(p)
        p.start()
    
    
    model.compute_dictionary("dict.csv")

    elapsed_time = time.time() - start_time
    print("Done ! in {} seconds".format(elapsed_time))
