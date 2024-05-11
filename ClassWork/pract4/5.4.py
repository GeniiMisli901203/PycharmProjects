import matplotlib.pyplot as plt
import networkx as nx

class TreeNode:
    def __init__(self, val, children=None):
        self.val = val
        self.children = children if children else []

    def visualize_tree(self, G, parent=None, pos=None, x=0, y=0, level=0, vertical_distance=1.0, horizontal_distance=0.5):
        if pos is None:
            pos = {self.val: (x, -y)}  # Изменено для правильной отрисовки по оси Y
        else:
            pos[self.val] = (x, -y)

        if parent is not None:
            G.add_edge(parent, self.val)

        num_children = len(self.children)
        if num_children > 0:
            v_distance = vertical_distance / (level + 1)
            h_distance = horizontal_distance / num_children
            next_x = x - (num_children - 1) * h_distance / 2
            for child in self.children:
                pos = child.visualize_tree(G, self.val, pos, next_x, y - v_distance, level + 1, vertical_distance, horizontal_distance)
                next_x += h_distance

        return pos

# Создание n-арного дерева
tree = TreeNode(1, [
    TreeNode(2, [
        TreeNode(3),
        TreeNode(4),
        TreeNode(5)
    ]),
    TreeNode(6, [
        TreeNode(7),
        TreeNode(8)
    ]),
    TreeNode(9)
])

# Визуализация дерева в виде графа
G = nx.DiGraph()
pos = tree.visualize_tree(G)

plt.figure(figsize=(12, 8))
nx.draw(G, pos, with_labels=True, arrows=True)
plt.show()
