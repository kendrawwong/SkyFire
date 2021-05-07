################################################################
# gradientAscent
# 
# by: Kendra Wong
# andrew ID: kendrawo
################################################################

import math

# Helper function from 15-112
import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

# test functions
def f(x, y):
    return math.sin(x - 0.5) + math.cos(y)

def g(x, y):
    return -((x-2)**2 + (y/2)**2 - 2)

def h(x, y):
    return math.sin(abs(x) + abs(y))

def gradientAscent(x, y, f):
    increment = 0.01
    newX = x + increment
    newY = y + increment
    dx = (f(newX, y) - f(x, y))/ increment
    dy = (f(x, newY) - f(x, y)) / increment
    if math.sqrt(dx ** 2 + dy ** 2) < increment:
        # returns a tuple with the x and y coordinates and the local maximum
        # with optimizing elevation, this would return latitude and longitude
        #   coordinates and the elevation
        return (x, y, f(x, y))
    else:
        return gradientAscent(x + dx * increment, y + dy * increment, f)

def testGradientAscent():
    print('Testing gradient ascent...')
    fX, fY, fVal = gradientAscent(4, 2, f)
    fX = roundHalfUp(fX)
    fY = roundHalfUp(fY)
    fVal = roundHalfUp(fVal)
    assert((fX, fY, fVal) == (2, 0, 2))
    gX, gY, gVal = gradientAscent(3, 2, g)
    gX = roundHalfUp(gX)
    gY = roundHalfUp(gY)
    gVal = roundHalfUp(gVal)
    assert((gX, gY, gVal) == (2, 0, 2))
    hX, hY, hVal = gradientAscent(4, 2, h)
    hX = roundHalfUp(hX)
    hY = roundHalfUp(hY)
    hVal = roundHalfUp(hVal)
    assert((hX, hY, hVal) == (5, 3, 1))
    print('Passed!')

def main():
    testGradientAscent()

if __name__ == '__main__':
    main()