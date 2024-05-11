class Tag:
    def __init__(self, name):
        self.name = name
        self.children = []

    def __enter__(self):
        print(f"<{self.name}>")
        return self

    def __exit__(self, type, value, traceback):
        print(f"</{self.name}>")

    def __call__(self, *args, **kwargs):
        if args:
            for arg in args:
                print(arg)


class HTML:
    def __init__(self):
        self.body = Tag('body')
        self.div = Tag('div')
        self.p = Tag('p')

    def get_code(self):
        pass


html = HTML()
with html.body:
    with html.div:
        with html.div:
            html.p('Первая строка.')
            html.p('Вторая строка.')
        with html.div:
            html.p('Третья строка.')
