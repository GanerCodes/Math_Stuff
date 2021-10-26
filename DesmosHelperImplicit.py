import clipboard

def IsConvex(a, b, c):
	crossp = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
	if crossp >= 0:
		return True 
	return False 
def InTriangle(a, b, c, p):
	L = [0, 0, 0]
	eps = 0.0000001
	L[0] = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) \
		  /(((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])) + eps)
	L[1] = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) \
		  /(((b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])) + eps)
	L[2] = 1 - L[0] - L[1]
	for x in L:
		if x > 1 or x < 0:
			return False  
	return True  
def IsClockwise(poly):
	sum = (poly[0][0] - poly[len(poly)-1][0]) * (poly[0][1] + poly[len(poly)-1][1])
	for i in range(len(poly)-1):
		sum += (poly[i+1][0] - poly[i][0]) * (poly[i+1][1] + poly[i][1])
	if sum > 0:
		return True
	return False
def GetEar(poly):
	size = len(poly)
	if size < 3:
		return []
	if size == 3:
		tri = [poly[0], poly[1], poly[2]]
		del poly[:]
		return tri
	for i in range(size):
		tritest = False
		p1 = poly[(i-1) % size]
		p2 = poly[i % size]
		p3 = poly[(i+1) % size]
		if IsConvex(p1, p2, p3):
			for x in poly:
				if not (x in (p1, p2, p3)) and InTriangle(p1, p2, p3, x):
					tritest = True
			if tritest == False:
				del poly[i % size]
				return [p1, p2, p3]
	print('GetEar(): no ear found')
	return []
#Triangulation alg is copy and pasted from github

def getFitter(n):
    return r"""
    var x = Calc.getState();
    x.expressions.list = x.expressions.list.concat([
        { type: `folder`, collapsed: true, id: `v$`, title: `Shape $`, folderId: `v$`},
        {color: `#388c46`, latex: `x_{$}=0`},
        {color: `#6042a6`, latex: `y_{$}=0`},
        {color: `#6042a6`, latex: `s_{x$}=3`},
        {color: `#000000`, latex: `s_{y$}=3`},
        {color: `#c74440`, latex: `a_{$}=0`},
        {color: `#6042a6`, latex: `b_{l$x}=-5`},
        {color: `#000000`, latex: `b_{l$y}=5`},
        {color: `#388c46`, latex: `b_{r$x}=5`},
        {color: `#6042a6`, latex: `b_{r$y}=-5`},
        {color: `#2d70b3`, latex: `v_{$}=\frac{\left(\left|s_{x$}\right|+\left|s_{y$}\right|\right)}{4}`},
        {color: `#2d70b3`, latex: `b_{s$}=\\max\\left(\\frac{\\left|2\\left(x-p_{$}.x\\right)-\\left(b_{l$x}+b_{r$x}\\right)\\right|}{\\left|b_{l$x}-b_{r$x}\\right|},\\frac{\\left|2\\left(y-p_{$}.y\\right)-\\left(b_{l$y}+b_{r$y}\\right)\\right|}{\\left|b_{l$y}-b_{r1y}\\right|}\\right)-1`},
        {color: `#000000`, latex: `c_{$}=v\\left(x,y,\\left(x_{$},y_{$}\\right),\\left(s_{x$},s_{y$}\\right),-a_{$}\\right)`},
        {color: `#6042a6`, latex: `\left(p_{$}.x+b_{l$x},p_{$}.y+b_{l$y}\right)`},
        {color: `#6042a6`, latex: `\left(p_{$}.x+b_{r$x},p_{$}.y+b_{r$y}\right)`},
        {color: `#388c46`, latex: `\left(p_{$}.x+s_{x$},p_{$}.y+s_{y$}\right)`},
        {color: `#000000`, latex: `p_{$}=\left(x_{$},y_{$}\right)`},
        {color: `#388c46`, dragMode: `XY`, latex: `\\left(p_{$}.x+v_{$}\\cos\\left(a_{$}+\\frac{\\pi}{2}\\right),p_{$}.y+v_{$}\\sin\\left(a_{$}+\\frac{\\pi}{2}\\right)\\right)`},
        {color: `#388c46`, parametricDomain: {min: `0`, max: `2\pi`}, lineOpacity: `0.5`, latex: `\\left(x_{$}-v_{$}\\cos\\left(t\\right),y_{$}-v_{$}\\sin\\left(t\\right)\\right)`},
        {color: `#2d70b3`, lineOpacity: `0.6`, latex: `\\max\\left(\\left|\\frac{x-x_{$}}{s_{x$}}\\right|,\\left|\\frac{y-y_{$}}{s_{y$}}\\right|\\right)=1`},
        {color: `#c74440`, lineOpacity: `0.5`, latex: `0=b_{s$}`},
        { type: `expression`, hidden: true, latex: `s_{$}=\\max\\left(f_{$}\\left(c_{$}.x,c_{$}.y\\right),b_{s$}\\right)`},
        { lineOpacity: `1`, type: `expression`, color: `#000000`, latex: `s_{$}\\le0`},
        { lineOpacity: `1`, type: `expression`, color: `#000000`, latex: `f_{$}\\left(x,y\\right)=x^{2}+y^{2}-1`}
    ])
    Calc.setState(x)
    """.strip().replace('{c', '{type: "expression", folderId: "v$", c').replace('\\\\', '\\').replace('\\', '\\\\').replace('$', str(n))

def getPolyThingy(poly, extra = 1):
    plist = poly[::-1] if IsClockwise(poly) else poly[:]
    tri = []
    while len(plist) >= 3:
        a = GetEar(plist)
        if a == []:
            break
        tri.append(a)
    r = ""
    for i in tri:
        x, y = ','.join(str(o[0]) for o in i), ','.join(str(o[1]) for o in i)
        r += f"""c_{{onvex}}\\left(\\left(\\left[{x}\\right],\\left[{y}\\right]\\right),{extra},x,y\\right)\n"""
    r = r[:-1]
    r = '\\min\\left(' + ','.join(r.split('\n')) + '\\right)\\le0'
    return r

"""
document.oncontextmenu = function(e) {
    if(e.target.className.includes("dcg-icon")) {
        e.preventDefault();
        Desmos.$(e.target).trigger('dcg-longhold');
    }
}

var n=1;
if(state=Calc.getState(),"table"==state.expressions.list[n].type){var res="";for(let s=0;s<state.expressions.list[n].columns.length;s++)res+="["+state.expressions.list[n].columns[s].values.toString()+"]",s!=state.expressions.list[n].columns.length-1&&(res+=", ");console.log(res);window.prompt("ctrl+c",res)}
"""

import clipboard
while 1:
    match input("Enter: n[_, e, f], [arr]: ").lower():
        case x if x[0] == '[':
            x = x.strip()
            j = x.split('],')
            if len(j) == 2:
                x, y = j
                extra = 1
            elif len(j) == 3:
                x, y, extra = j
            x = [float(i) for i in x.replace('[', '').split(',')]
            y = [float(i) for i in y.replace('[', '').replace(']', '').split(',')]
            r = getPolyThingy(list(zip(x, y)), float(extra))
            print(r)
            clipboard.copy(r)
        case x if x[0].isdigit():
            match (t := x[-1]):
                case _ if t.isdigit():
                    n = int(x)
                    clipboard.copy(f"""\
t_{{{n}}}=v\\left(x,y,\\left(x_{{{n}}},y_{{{n}}}\\right),\\left(1,1\\right),a_{{{n}}}\\right)
f_{{{n}}}\\left(x\\right)=x^{{2}}
a_{{{n}}}=0
x_{{{n}}}=0
y_{{{n}}}=0
\\left(x_{{{n}}},y_{{{n}}}\\right)
t_{{{n}}}.y=f_{{{n}}}\\left(t_{{{n}}}.x\\right)""")
                case _ if t == 'e':
                    n = int(x[:-1])
                    clipboard.copy(f"""\
t_{{{n}}}=v\\left(x,y,\\left(x_{{{n}}},y_{{{n}}}\\right),\\left(1,1\\right),a_{{{n}}}\\right)
f_{{{n}}}\\left(x\\right)=2^{{x}}
a_{{{n}}}=0
x_{{{n}}}=0
y_{{{n}}}=0
\\left(x_{{{n}}},y_{{{n}}}\\right)
t_{{{n}}}.y=f_{{{n}}}\\left(t_{{{n}}}.x\\right)""")
                case _ if t == 'f':
                    n = int(x[:-1])
                    clipboard.copy(getFitter(n))
                case _:
                    print("Invalid input.")
        case _:
            print("Invalid input.")