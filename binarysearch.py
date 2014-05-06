def binarysearch(lst, needle):
    l = len(lst)
    low = 0
    max = l - 1
    while True:
        #print low, max
        if max < low:
            return None
        m = (max + low + 1) / 2
        if needle == lst[m]:
            return m
        elif needle < lst[m]:
            max = m - 1
        else:
            low = m + 1
    
def binarysearchr(lst, needle):
    l = len(lst)
    if l==0:
        return None
    p = l / 2
    #print lst, l, p, 
    m = lst[p]
    #print m
    if m == needle:
        return p
    elif m > needle:
        return binarysearchr(lst[0:p], needle)
    else:
        r = binarysearchr(lst[p+1:], needle)
        if r == None:
            return None
        else:
            return r + p + 1
    
def binarysearchtr(lst, needle, offset = 0):
    l = len(lst)
    if l==0:
        return None
    p = l / 2
    m = lst[p]
    #print lst, l, p, m, offset
    if m == needle:
        return p + offset
    elif m > needle:
        return binarysearchtr(lst[0:p], needle, offset)
    else:
        return binarysearchtr(lst[p+1:], needle, offset + p + 1)
    
if __name__=='__main__':
    l = [12,34,56,78,90,23,45,67,89,110]
    l.sort()
    n = 78
    print l, n
    print binarysearch(l, n)
    print binarysearchr(l, n)
    print binarysearchtr(l, n)
    n = 12
    print l, n
    print binarysearch(l, n)
    print binarysearchr(l, n)
    print binarysearchtr(l, n)
    