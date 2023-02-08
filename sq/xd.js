let g = (f) => ((x) => f(f(x)));
let r = (F, n) => (n == 0 ? F : r(g(F), n-1));

console.log(
    r(g,
      r(g, 10)
        (x=>2*x)
            (1))
        (x=>2*x)
            (1));

// console.log(g(g(g(g)))((x) => (x+1))(0));
// 
// g: (f) 🠒 f(f(x))
// g(g) 🠒 g(g(x))

// console.log( g(g(g(g)))(x=>x*5)(1) );

// g(g) 🠒 x=>g(g(x))

// g(g)(f) = g(g(f)) x🠒f(f(x))
// g(g(x=>x+1))
// g(x=>x+2)
// x=>x+4