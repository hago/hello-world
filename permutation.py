#!/usr/bin/python
# -*- coding: UTF-8 -*-

olist = ['a', 'b', 'b1', 'c', 'd', 'e']
#olist = ['a', 'b']

def permutate(list, m):
    if m==0:
        return []
    if m==1:
        l = []
        for i in range(len(list)):
            l.append([list[i-1]])
        return l
    else:
        l = []
        for i in range(len(list)):
            e = list[i]
            print e, list[:i]+list[i+1:]
            l1 = permutate(list[:i]+list[i+1:], m-1)
            print e, l1
            for item in l1:
                l.append([e]+item)
        return l

if __name__=='__main__':
    r = {}
    for i in range(len(olist)+1):
        if i!=4:
            continue
        print olist, i
        l = permutate(olist, i)
        print l
        print len(l)
