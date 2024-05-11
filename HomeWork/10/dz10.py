def main(inp):
    unique_rows = remove_duplicates(inp)
    transformed_table = transform_rows(unique_rows)
    sorted_table = sort_table(transformed_table, 3)
    removed_empty_rows = remove_empty_rows(sorted_table)
    return removed_empty_rows

def remove_duplicates(input_data):
    unique_rows = []
    for row in input_data:
        if row not in unique_rows:
            unique_rows.append(row)
    return unique_rows

def transform_rows(rows):
    transformed_table = []
    for row in rows:
        transformed_row = []
        for i, cell in enumerate(row):
            transformed_cell = transform_cell(i, cell)
            if transformed_cell is not None:
                transformed_row.append(transformed_cell)
        transformed_table.append(transformed_row)
    return transformed_table

def transform_cell(index, cell):
    if cell is not None and len(cell) > index:
        if index == 1:
            return round_percentage(cell)
        elif index == 2:
            return replace_dash_with_slash(cell)
        elif index == 3:
            return extract_last_word(cell)
        elif index == 4:
            return format_phone_number(cell)
    return None


def round_percentage(value):
    return round(float(value.strip("%")) / 100, 4)

def replace_dash_with_slash(value):
    return value.replace("-", "/")

def extract_last_word(value):
    return value.split(" ")[-1]

def format_phone_number(number):
    phon = "".join(filter(str.isdigit, number))
    return phon[0:3] + " " + phon[3:6] + "-" + phon[6:10]

def sort_table(table, col):
    table.sort(key=lambda x: x[col] if col < len(x) and x[col] is not None else "")
    return table


def remove_empty_rows(table):
    return [row for row in table if any(cell is not None for cell in row)]

def add_empty_columns(table, num_columns):
    for row in table:
        while len(row) < num_columns:
            row.append(None)
    return table

table = [
    [None,"81%", "04-06-23", "Арсен Е. Рабобев", "349-055-8327"],
    [None,"81%", "04-06-23", "Арсен Е. Рабобев", "349-055-8327"],
    [None,"28%","04-05-13 ", "Сткпан В. Мабодук", "066-168-9902"],
    [None,"81%", "04-06-23", "Арсен Е. Рабобев", "349-055-8327"],
    [None,"95%", "00-10-27", "Степан В. Мавман", "553-054-0552"],
    [None, None, None, None, None]
]

table = add_empty_columns(table, 5)
sorted_table = main(table)

for row in sorted_table:
    print("\t".join(str(cell) for cell in row))
