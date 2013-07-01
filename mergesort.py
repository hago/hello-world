import sys

def ms(l):
	if len(l)<=1:
		return l
	print "enter ",
	print l
	mid = len(l) / 2
	l1 = l[:mid]
	l2 = l[mid:]
	if len(l1)>1:
		l1 = ms(l1)
	if len(l2)>1:
		l2 = ms(l2)
	if len(l1)==0 or len(l2)==0:
		return l1 + l2
	i1 = 0
	i2 = 0
	newl = []
	while True:
		if l1[i1] < l2[i2]:
			newl.append(l1[i1])
			i1+=1
		else:
			newl.append(l2[i2])
			i2+=1
		if i1 >= len(l1):
			newl += l2[i2:]
			break
		if i2 >= len(l2):
			newl += l1[i1:]
			break
	return newl

list = sys.argv[1:]
for i in range(len(list)):
	list[i] = int(list[i])
list = ms(list)
print list

