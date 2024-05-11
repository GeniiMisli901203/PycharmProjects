import re

def main(input_str):
    pattern_1 = '"(.*?)"'
    pattern_2 = r'var([^`= ]+)'
    pattern_3 = r'`([^`= ]+)'
    ans_1 = re.findall(pattern_1, input_str)
    ans_2 = re.findall(pattern_2, input_str)
    ans_3 = re.findall(pattern_3, input_str)
    result = dict(zip(ans_1, ans_3))
    return result

print(main(".begin ( var `geabi =: \"geesso_497\".); (var `arso_823=: \"xeare\". );.end"))
