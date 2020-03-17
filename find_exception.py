import tiers as t


def open_filter(filter_file):
    lines = dict()
    lines.update(t.uniques.find_lines(filter_file))
    return lines, filter_file


def take_items(lines, filter_file):
    need_items = list()
    for value in lines.values():
        with open(filter_file, 'r', encoding='utf-8') as file:
            for index, line in enumerate(file):
                if index == value:
                    need_items.append(line)
    return need_items


def clean_list(file='FilterBlade.filter'):
    need_items = take_items(open_filter(file)[0], open_filter(file)[1])
    rep = {'\tBaseType': '',
           'BaseType': '',
           '\n': '',
           ' "': '"',
           '""': '" "'
           }
    for index in range(len(need_items)):
        renamed = need_items[index]
        for to_replace, value in rep.items():
            renamed = renamed.replace(to_replace, value)
        need_items[index] = renamed
    return tuple(need_items)


if __name__ == '__main__':
    print(clean_list())
