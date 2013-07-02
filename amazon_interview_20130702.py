def encode(input):
    if not isinstance(input, basestring):
        raise Exception("Invalid input, string expected")
    output = ''
    count = 0
    lastchr = None
    for currentchr in input:
        if currentchr != lastchr:
            if lastchr != None:
                output += "%s%d" % (lastchr, count)
            lastchr = currentchr
            count = 1
        else:
            count += 1
    if lastchr != None:
        output += "%s%d" % (lastchr, count)
    return output
        
print encode("dsfdsaaaaaba")