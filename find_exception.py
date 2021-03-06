import tiers as t


def open_filter(filter_file):
    lines = dict()
    lines.update(t.uniques.find_lines(filter_file))
    return lines


def take_items(lines, filter_file):
    need_items = list()
    for value in lines.values():
        with open(filter_file, 'r', encoding='utf-8') as file:
            for index, line in enumerate(file):
                if index == value:
                    need_items.append(line)
    return need_items


def clean_list(file='FilterBlade.filter'):
    need_items = take_items(open_filter(file), file)
    rep = {'\tBaseType': '',
           'BaseType': '',
           '\n': '',
           ' "': '"',
           '""': '" "',
           }
    for ind in range(len(need_items)):
        renamed = need_items[ind]
        for to_replace, value in rep.items():
            renamed = renamed.replace(to_replace, value)
        need_items[ind] = renamed
    return tuple(need_items)


if __name__ == '__main__':
    print(clean_list())
