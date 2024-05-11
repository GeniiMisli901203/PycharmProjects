def main(input_dict):
    input_data = {
        'data': ".do<section>option#(mazaso_418 . usve_230 ) =:edus_420.</section>;<section> option#( oronla . tezara . edte ) =:xebiin_309.</section>;<section> option #( rilala_893 . ensoaa_898 . rera ) =:tiatri.</section> <section> option #( ares_430 . temabi ) =:iscete_34.</section>; ."
    }
    input_string = input_dict['data'].replace(".do", "").replace("</section>;<section>", " ").replace("</section>;", "").replace("<section>option#(", "").replace("):", "").replace(".", "").replace("\n", "").replace(" =", ":")
    input_list = input_string.split()
    result = {}
    temp_key = ''
    for i in range(len(input_list)):
        if input_list[i].startswith(':'):
            temp_key = input_list[i].replace(':', '')
            result[temp_key] = []
        else:
            result[temp_key].append(input_list[i])
    return result

print(main({'edus_420': ['mazaso_418', 'usve_230'],
 'xebiin_309': ['oronla', 'tezara', 'edte'],
 'tiatri': ['rilala_893', 'ensoaa_898', 'rera'],
 'iscete_34': ['ares_430', 'temabi']}))


