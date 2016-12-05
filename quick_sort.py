# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:39:02 2016

@author: Toulemont
"""

def quick_sort_dict(adict, list_of_keys, left, right, checkpoint):
    """
    This function aims to build a quicksort algorithm for dictionaries where keys
    are of type string.
    """
    def partition(adict, alist, le, ri):
        """
        Return the splitpoint for the quicksort.
        """
        i = ri + 1
        j = ri
        while j > le:
            if adict[alist[j]] > adict[alist[le]]:
                i -= 1
                a = alist[i]
                b = alist[j]
                alist[i] = b
                alist[j] = a
            j -= 1
        c = alist[i - 1]
        d = alist[le]
        alist[i - 1] = d
        alist[le] = c
        return i - 1

    if left < right:
        splitpoint = partition(adict, list_of_keys, left, right)
        quick_sort_dict(adict, list_of_keys, left, splitpoint - 1, checkpoint + 1)
        quick_sort_dict(adict, list_of_keys, splitpoint + 1, right, checkpoint + 1)

    if checkpoint == 0:
        return list_of_keys
