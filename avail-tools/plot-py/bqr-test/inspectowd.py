# 优化检查包
import code
if __name__=='__main__':
	def getLN_G(A):
		ln=100
		t=(ln+50)*1472*8/A
		g=0.01*t
		if g<40:
			g=40
		elif g>400:
			g=400
		t=g*100
		ln=t*A/1472/8-50
		return ln,g
	def getAList(ln,g,A):
		x=(ln+50)*1472*8/A
		ret=[]
		for i in range(100):
			p=(ln+i)*1472*8
			t=x+(i-50)*g
			a=p/t
			ret.append(a)
		return ret
	def pr(a,fmt='{:.2f}'):
		for i,v in enumerate(a):
			print('{:d}:'.format(i)+fmt.format(v))
	lists=[]
	for A in range(50,950+1,100):
		ln,g=getLN_G(A)
		alist=getAList(ln,g,A)
		lists.append(alist)
	code.interact(local=dict(globals(),**locals()))