import json
import re


def remove_hash_sign(line):
    line = line[1:]
    return line


class Tiers:
    def __init__(self, contents=None, parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5,
                 tier_3_price=2, file_strings=None,
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
        self.file_strings = file_strings
        self.exception = exception

    def open_filter(self, file='FilterBlade.filter'):
        with open(file, 'r', encoding='utf-8') as openf:
            self.file_strings = openf.readlines()
            openf.close()
        return self.file_strings

    def save_filter(self, all_lines, all_bases):
        """сортировка найденных строк в открытом файле"""
        sort_lines = {k: v for k, v in sorted(all_lines.items(), key=lambda item: item[1])}
        """запись копии файла с заменой данных"""
        with open('tmp.txt', 'w', encoding='utf-8') as tmp_file:
            for key in sort_lines.keys():
                if all_bases[key]:
                    line_base = f'BaseType {all_bases[key]} \n'
                    line_base = line_base.replace('[', '').replace(']', '').replace(',', '')
                    line_base = line_base.replace('\' ', '\" ').replace(' \'', ' \"')
                    self.file_strings[sort_lines[key]] = line_base
                    if 'Show' in self.file_strings[sort_lines[key] + 1]:
                        self.file_strings[sort_lines[key]] = f'{line_base}\n'
                    for i in range(1, 10):
                        prev_line = self.file_strings[sort_lines[key] - i]
                        if re.match('#', prev_line):
                            self.file_strings[sort_lines[key] - i] = remove_hash_sign(prev_line)
                        else:
                            break
            tmp_file.writelines(self.file_strings)
            tmp_file.close()
        return sort_lines

    def find_lines(self):
        all_lines = dict()
        for tier in self.tierlist:
            for index in range(len(self.open_filter())):
                line = self.file_strings[index]
                if self.find_method(tier, line):
                    if re.match('##', line):
                        remove_hash_sign(line)
                    for i in range(1, 50):
                        if 'BaseType' in self.file_strings[index + i]:
                            index += i
                            break
                        if self.show_next_line(index, i):
                            index += i - 1
                            break
                    all_lines.update({(self.contents, tier): index})
        return all_lines

    def show_next_line(self, index, i):
        if re.match('Show', self.file_strings[index + i]) or re.match('#Show', self.file_strings[index + i]):
            return True

    def find_method(self, tier, line):
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
    def __init__(self, contents='fragment', parse_file='parse.json', tierlist=None, tier_4_price=1):
        super().__init__(contents, parse_file, tier_1_price=12, tier_2_price=5, tier_3_price=2)
        self.tier_4_price = abs(float(tier_4_price))
        if tierlist is None:
            self.tierlist = ['1', '1p', '2', '3', '4']

    def find_method(self, tier, line):
        if f'{tier} ' in line and f'type->fragments' in line and 'scarabs' not in line:
            return True

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
    def __init__(self, contents='oil', parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5,
                 tier_3_price=2):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price, tier_3_price)
        if tierlist is None:
            self.tierlist = ['1', '2', '3', '4']

    def find_method(self, tier, line):
        if tier in line and f'currency->oil' in line:
            return True


class Resonators(Tiers):
    def __init__(self, contents='resonator', parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price)
        if tierlist is None:
            self.tierlist = ['1', '2', '3']

    def find_method(self, tier, line):
        if tier in line and 'resonator' in line:
            return True

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
    def __init__(self, contents='fossil', parse_file='parse.json', tierlist=None):
        super().__init__(contents, parse_file, tier_1_price=12, tier_2_price=5)
        if tierlist is None:
            self.tierlist = ['1', '2', '4']

    def find_method(self, tier, line):
        if str(tier) in line and 'fossil' in line:
            return True

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
    def __init__(self, contents='card', parse_file='parse.json', tierlist=None,
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

    def find_method(self, tier, line):
        if 'divination' in line and tier in line and "%H" not in line:
            return True


class Unique_Maps(Tiers):
    def __init__(self, contents='unique', parse_file='parse.json', tierlist=None,
                 tier_1_price=12, tier_2_price=5):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price)
        if tierlist is None:
            self.tierlist = ['1', '2', '3']

    def find_method(self, tier, line):
        if f'{tier} ' in line and f'unique->maps' in line:
            return True

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
    def __init__(self, contents='uniques', parse_file='parse.json', tierlist=None,
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

    def find_method(self, tier, line):
        if tier in line and f'type->uniques' in line and 'prophecy' not in line:
            return True

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


class Scarabs(Tiers):
    def __init__(self, contents='scarab', parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price)
        if tierlist is None:
            self.tierlist = ['1', '2']

    def find_method(self, tier, line):
        if tier in line and self.contents.lower() in line:
            return True

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '2'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for name in parsed[self.contents]:
                price = parsed[self.contents][name]
                if self.remove_exception(name) is not None:
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '2'].append(name)
            return all_bases


class Incubators(Tiers):
    def __init__(self, contents='incubator', parse_file='parse.json', tierlist=None, tier_1_price=12, tier_2_price=5):
        super().__init__(contents, parse_file, tierlist, tier_1_price, tier_2_price)
        if tierlist is None:
            self.tierlist = ['1', '2']

    def find_method(self, tier, line):
        if tier in line and self.contents.lower() in line:
            return True

    def take_bases(self):
        all_bases = {(self.contents, '1'): [], (self.contents, '2'): []}
        with open(self.parse_file, 'r', encoding='utf-8') as parsed:
            parsed = json.load(parsed)
            for name in parsed[self.contents]:
                price = parsed[self.contents][name]
                if self.remove_exception(name) is not None:
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '2'].append(name)
            return all_bases


tiers = Tiers()
fragments = Fragments()
oils = Oils()
resonators = Resonators()
fossils = Fossils()  # tiers are (1, 2, 4) in NeverSink's filter
div_cards = Divination_cards()
uni_maps = Unique_Maps()  # has only 2 tiers
uniques = Uniques()
scarabs = Scarabs()
incubators = Incubators()

if __name__ == "__main__":
    lines = dict()
    bases = dict()
    tiers.open_filter()
    bases.update(uniques.take_bases())
    bases.update(fragments.take_bases())
    bases.update(div_cards.take_bases())
    bases.update(fossils.take_bases())
    bases.update(resonators.take_bases())
    bases.update(scarabs.take_bases())
    bases.update(oils.take_bases())
    bases.update(incubators.take_bases())
    bases.update(uni_maps.take_bases())
    lines.update(uniques.find_lines())
    lines.update(fossils.find_lines())
    lines.update(oils.find_lines())
    lines.update(fragments.find_lines())
    lines.update(div_cards.find_lines())
    lines.update(resonators.find_lines())
    lines.update(incubators.find_lines())
    lines.update(uni_maps.find_lines())
    lines.update(scarabs.find_lines())
    print(f'Lines sorted by values: {tiers.save_filter(lines, bases)}')
