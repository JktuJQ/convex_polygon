from pytest import approx
from math import sqrt
from r2point import R2Point
from mock import mock


class TestR2Point:

    # Точку можно создать через стандартный поток ввода
    def test_r2point_input(self):
        coords = iter(["1", "2"])
        with mock.patch('builtins.input', lambda _: next(coords)):
            assert R2Point() == R2Point(1.0, 2.0)

    # Расстояние от точки до самой себя равно нулю
    def test_dist1(self):
        a = R2Point(1.0, 1.0)
        assert a.dist(R2Point(1.0, 1.0)) == approx(0.0)

    # Расстояние между двумя различными точками положительно
    def test_dist2(self):
        a = R2Point(1.0, 1.0)
        assert a.dist(R2Point(1.0, 0.0)) == approx(1.0)

    def test_dist3(self):
        a = R2Point(1.0, 1.0)
        assert a.dist(R2Point(0.0, 0.0)) == approx(sqrt(2.0))

    # Площадь треугольника равна нулю, если все вершины совпадают
    def test_area1(self):
        a = R2Point(1.0, 1.0)
        assert R2Point.area(a, a, a) == approx(0.0)

    # Площадь треугольника равна нулю, если все вершины лежат на одной прямой
    def test_area2(self):
        a, b, c = R2Point(0.0, 0.0), R2Point(1.0, 1.0), R2Point(2.0, 2.0)
        assert R2Point.area(a, b, c) == approx(0.0)

    # Площадь треугольника положительна при обходе вершин против часовой
    # стрелки
    def test_area3(self):
        a, b, c = R2Point(0.0, 0.0), R2Point(1.0, 0.0), R2Point(1.0, 1.0)
        assert R2Point.area(a, b, c) > 0.0

    # Площадь треугольника отрицательна при обходе вершин по часовой стрелке
    def test_area4(self):
        a, b, c = R2Point(0.0, 0.0), R2Point(1.0, 0.0), R2Point(1.0, 1.0)
        assert R2Point.area(a, c, b) < 0.0

    # Точки могут лежать внутри и вне "стандартного" прямоугольника с
    # противоположными вершинами (0,0) и (2,1)
    def test_is_inside1(self):
        a, b = R2Point(0.0, 0.0), R2Point(2.0, 1.0)
        assert R2Point(1.0, 0.5).is_inside(a, b)

    def test_is_inside2(self):
        a, b = R2Point(0.0, 0.0), R2Point(2.0, 1.0)
        assert R2Point(1.0, 0.5).is_inside(b, a)

    def test_is_inside3(self):
        a, b = R2Point(0.0, 0.0), R2Point(2.0, 1.0)
        assert not R2Point(1.0, 1.5).is_inside(a, b)

    # Ребро [(0,0), (1,0)] может быть освещено или нет из определённой точки
    def test_is_light1(self):
        a, b = R2Point(0.0, 0.0), R2Point(1.0, 0.0)
        assert not R2Point(0.5, 0.0).is_light(a, b)

    def test_is_light2(self):
        a, b = R2Point(0.0, 0.0), R2Point(1.0, 0.0)
        assert R2Point(2.0, 0.0).is_light(a, b)

    def test_is_light3(self):
        a, b = R2Point(0.0, 0.0), R2Point(1.0, 0.0)
        assert not R2Point(0.5, 0.5).is_light(a, b)

    def test_is_light4(self):
        a, b = R2Point(0.0, 0.0), R2Point(1.0, 0.0)
        assert R2Point(0.5, -0.5).is_light(a, b)

    # Две точки различны
    def test_eq1(self):
        assert R2Point(1.0, 1.0) != R2Point(2.0, 2.0)

    # Точка и кортеж отличаются
    def test_eq2(self):
        assert R2Point(1.0, 1.0) != (1.0, 1.0)
