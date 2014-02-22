import random
import string
import subprocess
import itertools

def chunks_equal(l, n):
    """ Yield n successive chunks from l.
    """
    newn = int(len(l) / n)
    for i in xrange(0, n-1):
        yield l[i*newn:i*newn+newn]
    yield l[n*newn-newn:]

def randstr(n = 4, fixed = True, charset = None):
    
    if not n:
        return ''
    
    if not fixed:
        n = random.randint(1,n)
    
    if not charset:
        charset = string.letters + string.digits
        
    return ''.join(random.choice(charset) for x in range(n))

def sxor(s1,s2):    
    return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(s1,itertools.cycle(s2)))
 
 
def divide(str, min_size, max_size, split_size):
    it = iter(str)
    size = len(str)
    for i in range(split_size - 1,0,-1):
        s = random.randint(min_size, size -  max_size * i)
        yield ''.join(itertools.islice(it,0,s))
        size -= s
    yield ''.join(it)
 
def getstatusoutput(cmd): 
   """Return (status, output) of executing cmd in a shell."""
   """This new implementation should work on all platforms."""
   pipe = subprocess.Popen(cmd, shell=True, universal_newlines=True,
           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   output = str.join("", pipe.stdout.readlines()) 
   sts = pipe.wait()
   if sts is None:
       sts = 0
   return sts, output