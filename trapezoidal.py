def trapezoidal(f, x: float, dx: float):
    return dx*(f(x)+f(x+dx))/2 