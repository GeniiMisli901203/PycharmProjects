import math
from random import randint
from tkinter import Tk, Canvas, Button

CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600

NODE_R = 15

C1, C2, C3, C4 = 200, 500, 20000, 0.005

DELAY = 10


class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Node:
    def __init__(self, text):
        self.text = text
        self.targets = []
        self.vec = Vec(0, 0)

    def to(self, *nodes):
        for n in nodes:
            self.targets.append(n)
            n.targets.append(self)
        return self


class Graph:
    def __init__(self):
        self.nodes = []

    def add(self, text):
        self.nodes.append(Node(text))
        return self.nodes[-1]


class GUI:
    def __init__(self, root):
        self.canvas = Canvas(root, width=CANVAS_WIDTH,
                             height=CANVAS_HEIGHT, bg="white")
        self.draw_button = Button(root, text="Draw", command=self.start_draw)
        self.canvas.pack()
        self.draw_button.pack()
        self.nodes = None
        self.busy = None

    def draw_node(self, x, y, text, r=NODE_R):
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="MistyRose2")
        self.canvas.create_text(x, y, text=text)

    def draw_graph(self):
        for n in self.nodes:
            for t in n.targets:
                self.canvas.create_line(n.vec.x, n.vec.y, t.vec.x, t.vec.y)
        for n in self.nodes:
            self.draw_node(n.vec.x, n.vec.y, n.text)

    def start_draw(self):
        self.canvas.delete("all")
        if self.busy:
            root.after_cancel(self.busy)
        random_layout(self.nodes)
        self.animate()

    def animate(self):
        self.canvas.delete("all")
        for _ in range(DELAY):
            force_layout(self.nodes)
        self.draw_graph()
        self.busy = root.after(5, self.animate)


def random_layout(nodes):
    for n in nodes:
        n.vec.x = randint(NODE_R * 4, CANVAS_WIDTH - NODE_R * 4 - 1)
        n.vec.y = randint(NODE_R * 4, CANVAS_HEIGHT - NODE_R * 4 - 1)


def f_spring(u, v):
    pass # TODO


def f_ball(u, v):
    pass # TODO


def force_layout(nodes):
    forces = {}
    for n in nodes:
        pass # TODO


def f_spring(u, v):
    k = 0.1  # коэффициент пружины
    x_diff = v.vec.x - u.vec.x
    y_diff = v.vec.y - u.vec.y
    distance = math.sqrt(x_diff ** 2 + y_diff ** 2)

    return Vec(k * x_diff, k * y_diff)


def f_ball(u, v):
    k = 1  # коэффициент отталкивания
    x_diff = u.vec.x - v.vec.x
    y_diff = u.vec.y - v.vec.y
    distance = math.sqrt(x_diff ** 2 + y_diff ** 2)

    return Vec(k * x_diff / distance, k * y_diff / distance)


def force_layout(nodes):
    forces = {}
    for u in nodes:
        forces[u] = Vec(0, 0)
        for v in nodes:
            if u != v and v not in u.targets:  # Проверка, не связаны ли узлы общим ребром-пружиной
                force = f_ball(u, v)
                forces[u].x += force.x
                forces[u].y += force.y

        for v in u.targets:
            force = f_spring(u, v)
            forces[u].x += force.x
            forces[u].y += force.y

        u.vec.x += forces[u].x * C4
        u.vec.y += forces[u].y * C4


g = Graph()
n1 = g.add("1")
n2 = g.add("2")
n3 = g.add("3")
n4 = g.add("4")
n5 = g.add("5")
n6 = g.add("6")
n7 = g.add("7")
n1.to(n2, n3, n4, n5)
n2.to(n5)
n3.to(n2, n4)
n6.to(n4, n1, n7)
n7.to(n5, n1)

root = Tk()
w = GUI(root)
w.nodes = g.nodes
root.mainloop()
