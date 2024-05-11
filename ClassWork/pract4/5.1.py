class SVG:
    def __init__(self):
        self.content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg">\n'.format(100, 100)

    def line(self, x1, y1, x2, y2, color='black'):
        line_str = '\t<line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:{};"/>\n'.format(x1, y1, x2, y2, color)
        self.content += line_str

    def circle(self, cx, cy, r, color='red'):
        circle_str = '\t<circle cx="{}" cy="{}" r="{}" fill="{}"/>\n'.format(cx, cy, r, color)
        self.content += circle_str

    def save(self, filename, width, height):
        self.content += '</svg>'
        with open(filename, 'w') as file:
            file.write(self.content.format(width, height))


svg = SVG()

svg.line(10, 10, 60, 10, color='black')
svg.line(60, 10, 60, 60, color='black')
svg.line(60, 60, 10, 60, color='black')
svg.line(10, 60, 10, 10, color='black')

svg.circle(10, 10, 5, color='red')
svg.circle(60, 10, 5, color='red')
svg.circle(60, 60, 5, color='red')
svg.circle(10, 60, 5, color='red')

svg.save('pic.svg', 100, 100)
