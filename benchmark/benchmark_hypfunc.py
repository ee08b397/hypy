import math
import timeit

# Inverse Hyperbolic Cosine
def asinh(x):
	return math.log(x + math.sqrt(x * x + 1.0))

def acosh(x):
	return math.log(x + math.sqrt(x * x - 1.0))

print "Result"
print "asinh lib\t"   , math.asinh(9.5)
print "asinh built\t" , asinh(9.5)

print "acosh lib\t"   , math.acosh(9.5)
print "acosh built\t" , acosh(9.5)

print "\nPerf"
print "asinh lib\t" , timeit.timeit('math.asinh(1.2)', setup='import math;', number=10000)
print "asinh built\t", timeit.timeit('math.log(0.2+math.sqrt(1.2*1.2+1.0))', setup='import math;', number=10000)

print "acosh lib\t"   , timeit.timeit('math.acosh(1.2)', setup='import math;', number=10000)
print "acosh built\t" , timeit.timeit('math.log(1.2+math.sqrt(1.2*1.2-1.0))', setup='import math;', number=10000)
