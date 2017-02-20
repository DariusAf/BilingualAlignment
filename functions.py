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


def quick_sort_list(alist, left, right, checkpoint):
    """
    This function aims to build a quicksort algorithm for lists.
    """
    def partition(alist, le, ri):
        i = ri + 1
        j = ri
        while j > le:
            if alist[j] > alist[le]:
                i -= 1
                a = alist[i]
                b = alist[j]
                alist[i] = b
                alist[j] = a
            j -= 1
        c = alist[i - 1]
        d = alist[le]
        alist[i - 1]
        alist[i - 1] = d
        alist[le] = c
        return i - 1
    if left < right:
        splitpoint = partition(alist, left, right)
        quick_sort_list(alist, left, splitpoint - 1, checkpoint + 1)
        quick_sort_list(alist, splitpoint + 1, right, checkpoint + 1)

    if checkpoint == 0:
        return alist


def jaro_winkler(str1, str2, alpha=0.8):
    """
    Computes the Jaro-winkler distance between two strings given as input.
    https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance
    """
    max_corr = int(max(len(str1), len(str2))/2) - 1
    m = 0
    t = 0
    last_corr = -1
    for i, chr1 in enumerate(str1):
        for j in range(max(i-max_corr, 0), min(i+max_corr+1, len(str2))):
            if chr1 == str2[j]:
                m += 1
                if j > last_corr:
                    last_corr = j
                else:
                    t += 1
                    last_corr = j
    dist = (m/len(str1) + m/len(str2) + (m-t)/max(1, m))/3
    # prefix
    common_prefix = 0
    while common_prefix < min([5, len(str1), len(str2)]) \
        and str1[common_prefix] == str2[common_prefix]:
        common_prefix += 1
    return dist*alpha + (1-dist*alpha)*common_prefix/5


def tolower(s):
    """ To be used with map """
    return s.lower()
