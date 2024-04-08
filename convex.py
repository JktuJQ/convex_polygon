from deq import Deq
from r2point import R2Point

from math import sqrt


# Вычислить мощность множества точек пересечения границы выпуклой
# оболочки с замкнутым единичным кругом с центром в начале координат.


class Figure:
    """ Абстрактная фигура """

    def perimeter(self):
        return 0.0

    def area(self):
        return 0.0

    def set_power(self):
        return 0


class Void(Figure):
    """ "Нульугольник" """

    def add(self, p):
        return Point(p)


class Point(Figure):
    """ "Одноугольник" """

    def __init__(self, p):
        self.p = p

    def add(self, q):
        return self if self.p == q else Segment(self.p, q)

    def set_power(self):
        return int(self.p.x ** 2 + self.p.y ** 2 <= 1.0)


class Segment(Figure):
    """ "Двуугольник" """

    def __init__(self, p, q):
        self.p, self.q = p, q

    def perimeter(self):
        return 2.0 * self.p.dist(self.q)

    def add(self, r):
        if R2Point.is_triangle(self.p, self.q, r):
            return Polygon(self.p, self.q, r)
        elif r.is_inside(self.p, self.q):
            return self
        elif self.p.is_inside(r, self.q):
            return Segment(r, self.q)
        else:
            return Segment(self.p, r)

    def set_power(self):
        x1, y1 = self.p.x, self.p.y
        x2, y2 = self.q.x, self.q.y
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        #  x - x1    y - y1
        # -------- = -------   => ax + by + c = 0 (y = (ax + c) / (-b))
        # x2 - x1    y2 - y1
        a = y2 - y1
        b = x1 - x2
        c = y1 * x2 - x1 * y2
        # { x ** 2 + y ** 2 = 1
        # { ax + by + c = 0
        # D = 4.0 * (b ** 2) * ((a ** 2 + b ** 2) - c ** 2)
        # sqrt(D) = 2.0 * b * sqrt((a ** 2 + b ** 2) - c ** 2)
        d = 4.0 * (b ** 2) * ((a ** 2 + b ** 2) - c ** 2)
        if d < 0:
            return 0
        elif d == 0:  # касательная
            if a == 0:  # горизонтальная
                return int(x_min <= 0 <= x_max)
            if b == 0:  # вертикальная
                x = -c / a
                if abs(x) == 1:
                    return int(y_min <= 0 <= y_max)
                if abs(x) >= 1:
                    return 0
                fy1 = 1 - x ** 2
                fy2 = -(1 - x ** 2)
                fy_min, fy_max = min(fy1, fy2), max(fy1, fy2)
                if y_min == fy_max or y_max == fy_min:
                    return 1
                if y_min <= fy_min and y_max >= fy_max \
                        or abs(y_min) <= 1 or abs(y_max) <= 1:
                    return "continuum"
                return 0
            x = -(a * c) / (a ** 2 + b ** 2)
            if x_min <= x <= x_max:
                return 1
            return 0
        else:
            fx1 = (-2 * (a * c) + sqrt(d)) / (2 * (a ** 2 + b ** 2))
            fx2 = (-2 * (a * c) - sqrt(d)) / (2 * (a ** 2 + b ** 2))
            fx_min, fx_max = min(fx1, fx2), max(fx1, fx2)
            if x_min == fx_max or x_max == fx_min:
                return 1
            if x_min <= fx_min and x_max >= fx_max or \
                    fx_min <= x_min <= fx_max or \
                    fx_min <= x_max <= fx_max:
                return "continuum"
            return 0

    def set_power_without_last_point(self):
        result = self.set_power()
        if result == 1 and Point(self.q).set_power() == 1:
            return 0
        return result


class Polygon(Figure):
    """ Многоугольник """

    def _add_set_power(self, x):
        set_power = x.set_power_without_last_point()
        if set_power == 1:
            self._points += 1
        elif set_power == "continuum":
            self._continuums += 1

    def _decrease_set_power(self, x):
        set_power = x.set_power_without_last_point()
        if set_power == 1:
            self._points -= 1
        elif set_power == "continuum":
            self._continuums -= 1

    def __init__(self, a, b, c):
        self.points = Deq()
        self.points.push_first(b)
        if b.is_light(a, c):
            self.points.push_first(a)
            self.points.push_last(c)
        else:
            self.points.push_last(a)
            self.points.push_first(c)
        self._perimeter = a.dist(b) + b.dist(c) + c.dist(a)
        self._area = abs(R2Point.area(a, b, c))
        self._points = 0
        self._continuums = 0
        self._add_set_power(Segment(a, b))
        self._add_set_power(Segment(b, c))
        self._add_set_power(Segment(c, a))

    def perimeter(self):
        return self._perimeter

    def area(self):
        return self._area

    # добавление новой точки
    def add(self, t):

        # поиск освещённого ребра
        for n in range(self.points.size()):
            if t.is_light(self.points.last(), self.points.first()):
                break
            self.points.push_last(self.points.pop_first())

        # хотя бы одно освещённое ребро есть
        if t.is_light(self.points.last(), self.points.first()):

            # учёт удаления ребра, соединяющего конец и начало дека
            self._perimeter -= self.points.first().dist(self.points.last())
            self._area += abs(R2Point.area(t,
                                           self.points.last(),
                                           self.points.first()))
            self._decrease_set_power(Segment(self.points.first(),
                                             self.points.last()))

            # удаление освещённых рёбер из начала дека
            p = self.points.pop_first()
            while t.is_light(p, self.points.first()):
                self._perimeter -= p.dist(self.points.first())
                self._area += abs(R2Point.area(t, p, self.points.first()))
                self._decrease_set_power(Segment(p, self.points.first()))
                p = self.points.pop_first()
            self.points.push_first(p)

            # удаление освещённых рёбер из конца дека
            p = self.points.pop_last()
            while t.is_light(self.points.last(), p):
                self._perimeter -= p.dist(self.points.last())
                self._area += abs(R2Point.area(t, p, self.points.last()))
                self._decrease_set_power(Segment(self.points.last(), p))
                p = self.points.pop_last()
            self.points.push_last(p)

            # добавление двух новых рёбер
            self._perimeter += t.dist(self.points.first()) + \
                t.dist(self.points.last())
            self._add_set_power(Segment(self.points.first(), t))
            self._add_set_power(Segment(t, self.points.last()))
            self.points.push_first(t)

        return self

    def set_power(self):
        if self._continuums > 0:
            return "continuum"
        else:
            return self._points


if __name__ == "__main__":
    f = Void()
    print(type(f), f.__dict__)
    f = f.add(R2Point(0.0, 0.0))
    print(type(f), f.__dict__)
    f = f.add(R2Point(1.0, 0.0))
    print(type(f), f.__dict__)
    f = f.add(R2Point(1.0, 2.0))
    print(type(f), f.__dict__)
