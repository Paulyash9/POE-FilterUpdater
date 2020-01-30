import json
import re


def save_filter(all_lines, file):  # INCOMPLETED!!!
    index = 0
    # сортировка строк
    sort_lines = {k: v for k, v in sorted(all_lines.items(), key=lambda item: item[1])}
    with open(file, 'r', encoding='utf-8') as openf:
        with open('tmp.txt', 'w', encoding='utf-8') as tmpf:
            for str_value in sort_lines.values():
                for indexof in openf.readlines():
                    if index < str_value:
                        tmpf.write(indexof)  # запись содержимого файла фильтра
                        index += 1
                    # tmpf.write(f'BaseType {}')  # обновленная запись предметов
                    else:
                        pass
    return sort_lines


class Tiers:
    def __init__(self, contents, parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5,
                 tier_3_price=2,
                 exception=('Timeworn Reliquary Key', 'Ancient Reliquary Key')):
        self.contents = contents
        self.parse_file = parse_file
        if tierlist is None:
            tierlist = ['1', '2', '3', '4']
        self.tierlist = tierlist
        self.tier_1_price = abs(float(tier_1_price))
        self.tier_2_price = abs(float(tier_2_price))
        self.tier_3_price = abs(float(tier_3_price))
        if self.tier_2_price >= self.tier_1_price:
            raise ValueError("Wrong tier prices. Tier 1 price must be more than Tier 2")
        if self.tier_3_price >= self.tier_2_price:
            raise ValueError("Wrong tier prices. Tier 2 price must be more than Tier 3")
        self.exception = exception

    def find_lines(self, file):
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if tier in line and self.contents.lower() in line:
                        if re.match('#', line) and self.take_bases():
                            self.remove_hash_sign(line)
                            for found_index, found_line in enumerate(filter_file):
                                index += 1
                                if re.match('Show', found_line):
                                    index -= 1
                                    break
                                else:
                                    if 'BaseType ' in found_line:
                                        break
                        all_lines.update({(self.contents, tier): index})
        return all_lines

    def remove_hash_sign(self, line):
        line = line[1:]
        pass

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '2'): [],
                     (self.contents, '3'): [], (self.contents, '4'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for name in parsed[self.contents]:
                price = parsed[self.contents][name]
                if self.remove_exception(name) is not None:
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '2'].append(name)
                    elif self.tier_3_price < price <= self.tier_2_price:
                        all_bases[self.contents, '3'].append(name)
                    else:
                        all_bases[self.contents, '4'].append(name)
            return all_bases

    def remove_exception(self, item_name):
        if item_name in self.exception:
            return None
        else:
            return item_name

    def __repr__(self):
        return f'<{self.contents}>'


class Fragments(Tiers):
    def __init__(self, contents, parse_file='parse.json', tierlist=None, tier_4_price=1):
        super().__init__(contents, parse_file, tier_1_price=12, tier_2_price=5, tier_3_price=2)
        self.tier_4_price = abs(float(tier_4_price))
        if tierlist is None:
            self.tierlist = ['1', '1p', '2', '3', '4']

    def find_lines(self, file):
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if tier in line and f'type->{self.contents.lower()}' in line and 'scarabs' not in line:
                        for found_index, found_line in enumerate(filter_file):
                            index += 1
                            if 'BaseType ' in found_line:
                                break
                        all_lines.update({(self.contents, tier): index})
        if all_lines == {}:
            print('find Nothing')
        return all_lines

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '1p'): [], (self.contents, '2'): [],
                     (self.contents, '3'): [], (self.contents, '4'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for name in parsed[self.contents]:
                price = parsed[self.contents][name]
                if self.remove_exception(name) is not None:
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '1p'].append(name)
                    elif self.tier_3_price < price <= self.tier_2_price:
                        all_bases[self.contents, '2'].append(name)
                    elif self.tier_4_price < price <= self.tier_3_price:
                        all_bases[self.contents, '3'].append(name)
                    else:
                        all_bases[self.contents, '4'].append(name)
            return all_bases


class Oils(Tiers):
    def __init__(self, contents, parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5,
                 tier_3_price=2):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price, tier_3_price)
        if tierlist is None:
            self.tierlist = ['1', '2', '3', '4']

    def find_lines(self, file):
        contents = 'oil'
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if tier in line and f'currency->{contents}' in line:
                        for found_index, found_line in enumerate(filter_file):
                            index += 1
                            if 'BaseType ' in found_line:
                                break
                        all_lines.update({(self.contents, tier): index})
        return all_lines


class Resonators(Tiers):
    def __init__(self, contents, parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price)
        if tierlist is None:
            self.tierlist = ['1', '2', '3']

    def find_lines(self, file):
        contents = 'resonator'
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if tier in line and contents in line:
                        for found_index, found_line in enumerate(filter_file):
                            index += 1
                            if 'BaseType ' in found_line:
                                break
                        all_lines.update({(self.contents, tier): index})
        return all_lines

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '2'): [],
                     (self.contents, '3'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for name in parsed[self.contents]:
                price = parsed[self.contents][name]
                if self.remove_exception(name) is not None:
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '2'].append(name)
                    else:
                        all_bases[self.contents, '3'].append(name)
        return all_bases


class Fossils(Tiers):
    def __init__(self, contents, parse_file='parse.json', tierlist=None):
        super().__init__(contents, parse_file, tier_1_price=12, tier_2_price=5)
        if tierlist is None:
            self.tierlist = ['1', '2', '4']

    def find_lines(self, file):
        contents = 'fossil'
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if str(tier) in line and contents in line:
                        for found_index, found_line in enumerate(filter_file):
                            index += 1
                            if 'BaseType' in found_line:
                                break
                        all_lines.update({(self.contents, tier): index})
        return all_lines

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '2'): [], (self.contents, '4'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for name in parsed[self.contents]:
                price = parsed[self.contents][name]
                if self.remove_exception(name) is not None:
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '2'].append(name)
                    else:
                        all_bases[self.contents, '4'].append(name)
        return all_bases


class Divination_cards(Tiers):
    def __init__(self, contents, parse_file='parse.json', tierlist=None,
                 tier_1_price=12, tier_2_price=5, tier_3_price=0.65,
                 exception=('The Demoness', 'The Wolf\'s Shadow', "The Wolf\'s Legacy", 'The Master Artisan',
                            'A Mother\'s Parting Gift', 'Birth of the Three', 'Dark Temptation',
                            'Destined to Crumble', 'Dying Anguish', 'Lantador\'s Lost Love', 'Might is Right',
                            'Prosperity', 'Rats', 'Struck by Lightning', 'The Blazing Fire', 'The Carrion Crow',
                            'The Coming Storm', 'The Twins', 'The Hermit', 'The Incantation', 'The Inoculated',
                            'The King\'s Blade', 'The Lich', 'The Lover', 'The Surgeon', 'The Metalsmith\'s Gift',
                            'The Oath', 'The Rabid Rhoa', 'The Scarred Meadow', 'The Sigil', 'The Warden',
                            'The Watcher', 'The Web', 'The Witch', 'Thunderous Skies', 'The Deceiver',
                            'Anarchy\'s Price', 'The Wolf\'s Shadow', 'The Battle Born', 'The Feast',
                            'Assassin\'s Favour', 'Hubris', 'Rain of Chaos', 'Emperor\'s Luck', 'Her Mask',
                            'The Flora\'s Gift', 'The Puzzle', 'Boon of Justice', 'Coveted Possession',
                            'Demigod\'s Wager', 'Emperor\'s Luck', 'Harmony of Souls', 'Imperial Legacy', 'Loyalty',
                            'Lucky Connections', 'Monochrome', 'More is Never Enough', 'No Traces', 'Sambodhi\'s Vow',
                            'The Cacophony', 'The Catalyst', 'The Deal', 'The Fool', 'The Gemcutter', 'The Innocent',
                            'The Inventor', 'The Puzzle', 'The Survivalist', 'The Union', 'The Wrath',
                            'Three Faces in the Dark', 'Three Voices', 'Vinia\'s Token', 'The Seeker',
                            'Buried Treasure', 'The Journey', 'Rain of Chaos', 'Her Mask', 'The Gambler',
                            'The Flora\'s Gift', 'The Scholar')):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price, tier_3_price, exception)
        if tierlist is None:
            self.tierlist = ['1', '2', '3', '4']

    def find_lines(self, file):
        contents = 'divination'
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if contents in line and tier in line and "%H" not in line:
                        for found_index, found_line in enumerate(filter_file):
                            index += 1
                            if 'BaseType ' in found_line:
                                break
                        all_lines.update({(self.contents, tier): index})
        return all_lines


class Unique_Maps(Tiers):
    def __init__(self, contents, parse_file='parse.json', tierlist=None,
                 tier_1_price=12, tier_2_price=5):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price)
        if tierlist is None:
            self.tierlist = ['1', '2', '3']

    def find_lines(self, file):
        contents = 'maps'
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if tier in line and f'unique->{contents}' in line:
                        for found_index, found_line in enumerate(filter_file):
                            index += 1
                            if 'BaseType' in found_line:
                                break
                        all_lines.update({(self.contents, tier): index})
        return all_lines

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '2'): [],
                     (self.contents, '3'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for name in parsed[self.contents]:
                price = parsed[self.contents][name]
                if self.remove_exception(name) is not None:
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '2'].append(name)
                    else:
                        all_bases[self.contents, '3'].append(name)
        return all_bases


class Uniques(Tiers):
    def __init__(self, contents=None, parse_file='parse.json', tierlist=None,
                 tier_1_price=12, tier_2_price=5, tier_3_price=2,
                 exception=('Amber Amulet', 'Assassin Bow', 'Sapphire Ring', 'Triumphant Lamellar', 'Agate Amulet',
                            'Topaz Ring', 'Saint\'s Hauberk', 'Penetrating Arrow Quiver', 'Jade Amulet',
                            'Two-Stone Ring', 'Leather Belt', 'Imperial Skean', 'Iron Ring', 'Magistrate Crown',
                            'Murder Mitts', 'Onyx Amulet', 'Crusader Gloves', 'Studded Belt', 'Sulphur Flask',
                            'Turquoise Amulet', 'Sorcerer Boots', 'Judgement Staff', 'Stibnite Flask', 'Brass Maul',
                            'Clasped Boots', 'Cleaver', 'Coral Ring', 'Crude Bow', 'Crusader Plate', 'Crystal Wand',
                            'Death Bow', 'Fire Arrow Quiver', 'Gavel', 'Gilded Sallet', 'Gnarled Branch',
                            'Goathide Gloves', 'Gold Amulet', 'Golden Buckler', 'Great Crown', 'Great Mallet',
                            'Iron Circlet', 'Iron Hat', 'Iron Mask', 'Iron Staff', 'Ironscale Boots', 'Jade Hatchet',
                            'Jagged Maul', 'Latticed Ringmail', 'Leather Hood', 'Long Bow', 'Moonstone Ring',
                            'Ornate Sword', 'Painted Buckler', 'Plank Kite Shield', 'Plate Vest', 'Reaver Sword',
                            'Reinforced Greaves', 'Royal Bow', 'Royal Staff', 'Rusted Sword', 'Scholar Boots',
                            'Serrated Arrow Quiver', 'Sharktooth Arrow Quiver', 'Skinning Knife', 'Sledgehammer',
                            'Spiraled Wand', 'Strapped Leather', 'Tarnished Spirit Shield', 'Velvet Gloves',
                            'Velvet Slippers', 'Vine Circlet', 'War Buckler', 'Wild Leather', 'Woodsplitter',
                            'Cobalt Jewel', 'Crimson Jewel', 'Viridian Jewel', 'Simple Robe', 'Cobalt Jewel',
                            'Crimson Jewel', 'Viridian Jewel'),
                 unique_types=('flask', 'weapon', 'jewel', 'armour', 'accessory')):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price, tier_3_price, exception)
        self.unique_types = unique_types
        if tierlist is None:
            self.tierlist = ['1', '2', '4']

    def find_lines(self, file):
        all_lines = dict()
        for tier in self.tierlist:
            with open(file, 'r', encoding='utf-8') as filter_file:
                for index, line in enumerate(filter_file):
                    if f'type->{self.contents.lower()}' in line and 'prophecy' not in line:
                        for found_index, found_line in enumerate(filter_file):
                            index += 1
                            if 'BaseType' in found_line:
                                break
                        all_lines.update({(self.contents, tier): index})
        return all_lines

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '2'): [], (self.contents, '4'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for contents in self.unique_types:
                if contents in parsed.keys():
                    for name in parsed[contents]:
                        price = parsed[contents][name]
                        if self.remove_exception(name) is not None:
                            if price > self.tier_1_price:
                                all_bases[self.contents, '1'].append(name)
                            elif self.tier_2_price < price <= self.tier_1_price:
                                all_bases[self.contents, '2'].append(name)
                            else:
                                all_bases[self.contents, '4'].append(name)
        return all_bases


uniques = Uniques('uniques')
fragments = Fragments('fragment')
div_cards = Divination_cards('card')
fossils = Fossils('fossil')  # tiers are (1, 2, 4) in NeverSink's filter
resonators = Resonators('resonator')
scarabs = Tiers('scarab')
oils = Oils('oil')
incubators = Tiers('incubator')
uni_maps = Unique_Maps('unique')  # has only 2 tiers

if __name__ == "__main__":
    bases = dict()
    bases.update(uniques.take_bases())
    bases.update(fragments.take_bases())
    bases.update(div_cards.take_bases())
    bases.update(fossils.take_bases())
    bases.update(resonators.take_bases())
    bases.update(scarabs.take_bases())
    bases.update(oils.take_bases())
    bases.update(incubators.take_bases())
    bases.update(uni_maps.take_bases())
    print(bases)
    file_filter = 'FilterBlade.filter'
    lines = dict()
    lines.update(uniques.find_lines(file_filter))
    lines.update(fossils.find_lines(file_filter))
    lines.update(oils.find_lines(file_filter))
    lines.update(fragments.find_lines(file_filter))
    lines.update(div_cards.find_lines(file_filter))
    lines.update(resonators.find_lines(file_filter))
    lines.update(incubators.find_lines(file_filter))
    lines.update(uni_maps.find_lines(file_filter))
    lines.update(scarabs.find_lines(file_filter))
    print(f'Not sorted:{lines}')
    lines = {k: v for k, v in sorted(lines.items(), key=lambda item: item[1])}
    print(f'Sorted by values: {lines}')

'''
!!!!!!!!!!!!!!!!!!!
- Доделать поиск по категориям со знаками #
если есть в tier предметы, а категория за #, то убрать в файле # 
- ОШИБКА С OILS (можно добавить в конце категории в строку после CustomAlertSound)

'''
