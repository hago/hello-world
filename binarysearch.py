import sys

def bs(l):
	if len(l)==0:
		return []
	print "enter ",
	print l
	sep = l[0]
	l1 = []
	l2 = []
	for ele in l[1:]:
		if sep>ele:
			l1.append(ele)
		else:
			l2.append(ele)
	print l1, l2
	if len(l1)<=1:
		leftl = l1
	else:
		leftl = bs(l1)
	if len(l2)<=1:
		rightl = l2
	else:
		rightl = bs(l2)
	print "after\t",
	print leftl, rightl
	newl = leftl + [sep] + rightl
	return newl

list = sys.argv[1:]
for i in range(len(list)):
	list[i] = int(list[i])
list = bs(list)
print list

