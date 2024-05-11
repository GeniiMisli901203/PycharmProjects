import matplotlib.pyplot as plt
import networkx as nx

class Tree:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def visualize_tree(self, G, parent=None, pos=None, x=0, y=0, level=0, vertical_distance=1.0, horizontal_distance=1.0):
        if pos is None:
            pos = {self.val: (x, -y)}  # Изменено для правильной отрисовки по оси Y
        else:
            pos[self.val] = (x, -y)

        if parent is not None:
            G.add_edge(parent, self.val)

        if self.left:
            pos = self.left.visualize_tree(G, self.val, pos, x - horizontal_distance, y - vertical_distance, level + 1, vertical_distance, horizontal_distance/2)
        if self.right:
            pos = self.right.visualize_tree(G, self.val, pos, x + horizontal_distance, y - vertical_distance, level + 1, vertical_distance, horizontal_distance/2)

        return pos

# Создание бинарного дерева
tree_2 = Tree(2, Tree(3, Tree(4), Tree(5)), Tree(6, None, Tree(7)))
tree_8 = Tree(8, Tree(9, Tree(10), Tree(11, Tree(12), Tree(13))), Tree(14))
tree = Tree(1, tree_2, tree_8)

# Визуализация дерева в виде графа
G = nx.DiGraph()
pos = tree.visualize_tree(G)

plt.figure(figsize=(12, 8))
nx.draw(G, pos, with_labels=True, arrows=True)
plt.show()
