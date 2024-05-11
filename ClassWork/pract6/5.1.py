import csv

def Scan(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row

# Запускаем генератор Scan для файла talks.csv
talks = Scan('talks.csv')

# Выводим первые 5 строк таблицы
for i, row in enumerate(talks):
    print(row)
    if i == 4:
        break
