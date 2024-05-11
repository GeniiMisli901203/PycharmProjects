import csv

def Scan(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def Print(parent):
    for row in parent:
        print(row)

# Читаем файл talks.csv
talks = Scan('talks.csv')

# Печатаем все строки таблицы
Print(talks)
