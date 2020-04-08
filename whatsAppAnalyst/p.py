# importing line_profiler module 
from line_profiler import LineProfiler

def p(rk): 
	for i in range(5):
		print(rk)

def geek(rk): 
	for i in range(5):
		print(p(rk) )


rk ="geeks"
profile = LineProfiler(geek(rk)) 
profile.print_stats() 
