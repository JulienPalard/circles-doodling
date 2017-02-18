#!/usr/bin/env python3

import math
import numpy
import itertools
import pngcanvas

whiteb = b'\xff\xff\xff'
red = (0xff, 0x0, 0x0, 0xff)

class PNGCanvas(pngcanvas.PNGCanvas):
    def get(self, x, y):
        if x < 0 or y < 0 or x > self.width - 1 or y > self.height - 1:
            return
        o = self._offset(x, y)
        return self.canvas[o:o + 3]

    def points_of_color(self, color):
        for x in range(self.width):
            for y in range(self.height):
                if self.get(x, y) == color:
                    yield x, y

    def flood_fill(self, x, y, color):
        """
        For each pixel of the given column:
            For each line of the given pixel:
                Color line, and recurse at the end of the line.
        """
        todo = [(x, y)]
        while len(todo) != 0:
            x, y = todo.pop()
            if self.get(x, y) != whiteb:
                continue
            todo.append((x + 1, y))
            todo.append((x - 1, y))
            todo.append((x, y + 1))
            todo.append((x, y - 1))
            self.point(x, y, color)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_circle(self, radii):
        return Circle(self, radii)

    def dist(self, other):
        return ((other.x - self.x) ** 2 +
                (other.y - self.y) ** 2) ** .5

    def __add__(self, other):
        return Point(self.x + other.x,
                     self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x,
                     self.y - other.y)

    def __mul__(self, k):
        return Point(self.x * k, self.y * k)

    def __truediv__(self, k):
        return Point(self.x / k, self.y / k)

    def __str__(self):
        return '<Point ({}, {})>'.format(self.x, self.y)


class Circle(object):
    def __init__(self, center, radii):
        self.center = center
        self.radii = radii

    def get_points(self, num=None):
        """
        Iterate over some points of this circle.
        Get `num` points from the circle, by default num is 2πr.
        """
        import math
        if num is None:
            num = 2 * math.pi * self.radii
        for x in numpy.linspace(0, math.pi, num=num):
            yield (Point(self.radii * math.cos(x),
                         self.radii * math.sin(x)) +
                   self.center)
            yield (Point(self.radii * math.cos(x),
                         - self.radii * math.sin(x)) +
                   self.center)

    def __str__(self):
        return "<Circle ({}, {}) -- {}>".format(self.center.x,
                                                self.center.y,
                                                self.radii)

    def intercect_circle(self, other):
        """
        Return a tuple that describe the intersection with another circle.

        This interception have the shape of a lense. We return the
        tuple describing the chord connecting the cusps of the lense.

        (x, a) with:
         - x the distance between self and the chord.
         - a the half-length of the chord.

        May return False, False if circles never intercepts (concentric).

        Or an imaginary result if circles are not concentric but not intercept.
        """
        d = other.center.dist(self.center)
        if d == 0:
            # Concentric circles never intercect:
            return False, False
        r = self.radii
        R = other.radii
        x = (r ** 2 - R ** 2 + d ** 2) / (2 * d)
        a = (r ** 2 - x ** 2) ** .5
        return (x, a)

    def intercect_circle_points(self, other):
        """Returns a tuple of two points, of (False, False).  Points
        represent the intersection between self and other, if they
        intersect.  They may not visually intersect but this method
        may return imaginary points.
        """
        a, h = self.intercect_circle(other)
        if a is False:
            return (False, False)
        d = other.center.dist(self.center)
        p2 = self.center + (other.center - self.center) * a / d
        x = self.center - other.center
        relative = Point(-x.y * (h / d), x.x * (h / d))
        return (p2 + relative, p2 - relative)


def draw():
    import random
    canvas = PNGCanvas(1000, 1000,
                       bgcolor=(255, 255, 255, 255),
                       color=(0, 0, 0, 255))
    circles = []
    for _ in range(15):
        circles.append(Circle(Point(random.randint(0, 1000),
                                    random.randint(0, 1000)),
                              random.randint(0, 500)))
    for circle in circles:
        for point in circle.get_points():
            canvas.point(int(point.x), int(point.y), (0x0, 0x0, 0x0, 0xFF))

    # for left, right in itertools.combinations(circles, 2):
    #     for interseption_point in left.intercect_circle_points(right):
    #         if type(interseption_point.x) is complex:
    #             continue
    #         canvas.point(interseption_point.x, interseption_point.y, red)
    #         # for p in interseption_point.as_circle(4).get_points():
    #         #     if p is False or type(p.x) is complex:
    #         #         continue
    #         #     canvas.point(p.x, p.y,

    for x, y in canvas.points_of_color(whiteb):
        print(x, y)
        canvas.flood_fill(x, y,
                          (random.randint(0, 255),
                           random.randint(0, 255),
                           random.randint(0, 255),
                           0XFF))

    with open('circles.png', 'wb') as png:
        png.write(canvas.dump())

if __name__ == '__main__':
    draw()
