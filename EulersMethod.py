import numpy as np

start = (2, 6)
endLoc = 3
eq = "2*y-4*x"
stepSize = 0.5


y = start[1]
for x in list(np.arange(start[0], endLoc, stepSize)) + [endLoc]:
    d = eval(eq.replace('x', str(x)).replace('y', str(y)))
    print("%s  |  %s  |  %s" % tuple(map(lambda t: str(round(t, 3)).rjust(6), [x, y, d])))
    y += d * stepSize