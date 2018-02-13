import random

ASV = 'ASV_0'	#Name of ASV
N = 3	#Number of ASV's

ASV_list = []
a = [str(i) for i in range(N)]
for j in a:
	b = ASV.replace(ASV[4],j)
	c = ASV_list.append(b)
	print(ASV_list)

print random.randint(0,N)
