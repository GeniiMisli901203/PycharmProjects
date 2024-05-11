def main(inp):
    unique_rows = remove_duplicates_and_empties(inp)
    transformed_table = transform_rows(unique_rows)
    sorted_table = sort_table(transformed_table, 3)
    return sorted_table



def remove_duplicates_and_empties(input_data):
    unique_rows = []
    for row in input_data:
        if row not in unique_rows and all(cell != '' for cell in row):
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
        if transformed_row:  # Добавьте эту проверку
            transformed_table.append(transformed_row)
    return transformed_table


def transform_cell(index, cell):
    if cell is not None:
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
    return '{:.4f}'.format(float(value.strip("%")) / 100)


def replace_dash_with_slash(value):
    return value.replace("-", "/")


def extract_last_word(value):
    return value.split(" ")[-1]


def format_phone_number(number):
    pho = ''.join(filter(str.isdigit, number))
    return pho[0:3] + ' ' + pho[3:6] + '-' + pho[6:10]


def sort_table(t, col):
    t = sorted(t, key=lambda x: x[3] if x[3] is not None else "")
    return t


t = [
    [None,"81%", "04-06-23", "Арсен Е. Рабобев", "349-055-8327"],
    [None,"81%", "04-06-23", "Арсен Е. Рабобев", "349-055-8327"],
    [None,"28%","04-05-13 ", "Сткпан В. Мабодук", "066-168-9902"],
    [None,"81%", "04-06-23", "Арсен Е. Рабобев", "349-055-8327"],
    [None,"95%", "00-10-27", "Степан В. Мавман", "553-054-0552"],
    [None, None, None, None, None]
]

