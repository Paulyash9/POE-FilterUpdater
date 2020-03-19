import re
import settings
from pymongo import MongoClient


def remove_hash_sign(line):
    line = line[1:]
    return line


class Tiers:
    def __init__(self, items=None, contents=None, parse_file='parse.json',
                 tierlist=('1', '2', '3', '4'),
                 tier_1_price=12, tier_2_price=5, tier_3_price=2,
                 file_strings=None,
                 exception=(
                         'Timeworn Reliquary Key', 'Ancient Reliquary Key'
                 )):
        self.contents = contents
        self.parse_file = parse_file
        self.tierlist = tierlist
        self.tier_1_price = abs(float(tier_1_price))
        self.tier_2_price = abs(float(tier_2_price))
        self.tier_3_price = abs(float(tier_3_price))
        if self.tier_2_price >= self.tier_1_price:
            raise ValueError(
                'Wrong tier prices. Tier 1 price must be more than Tier 2'
            )
        if self.tier_3_price >= self.tier_2_price:
            raise ValueError(
                'Wrong tier prices. Tier 2 price must be more than Tier 3'
            )
        self.file_strings = file_strings
        self.exception = exception
        self.items = items

    def open_filter(self, filter_file):
        with open(filter_file, 'r', encoding='utf-8') as openf:
            self.file_strings = openf.readlines()
            openf.close()
        return self.file_strings

    def save_filter(self, all_lines, all_bases):
        """сортировка индексов найденных строк в открытом файле фильтра"""
        sort_lines = {k: v for k, v in sorted(all_lines.items(),
                                              key=lambda item: item[1])}
        """запись копии файла с заменой данных"""
        with open('tmp.txt', 'w', encoding='utf-8') as tmp_file:
            for key in sort_lines.keys():
                if key in all_bases.keys():
                    line_base = f'BaseType {all_bases[key]} \n'
                    to_replace = (('[', ''), (']', ''), (',', ''), ('\' ', '\" '), (' \'', ' \"'))
                    for value in to_replace:
                        line_base = line_base.replace(value[0], value[1])
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

    def find_lines(self, filter_file):
        all_lines = dict()
        for tier in self.tierlist:
            for index in range(len(self.open_filter(filter_file))):
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
        if re.match('Show', self.file_strings[index + i]) or \
                re.match('#Show', self.file_strings[index + i]):
            return True

    def find_method(self, tier, line):
        pass

    def take_items(self, league='Current SC'):
        client = MongoClient(settings.mongo_client)
        db_collection = client.Items_base.Items
        standard = db_collection.find({'league': league})
        items = []
        for doc in standard:
            items += [doc]
        self.items = items[0]
        return self.items

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '2'): [],
            (self.contents, '3'): [],
            (self.contents, '4'): []
        }
        for name, price in self.items[self.contents].items():
            if self.remove_exception(name):
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
    def __init__(self, items, contents='fragment', parse_file='parse.json',
                 tierlist=('1', '1p', '2', '3', '4'),
                 tier_1_price=12, tier_2_price=5,
                 tier_3_price=2, tier_4_price=1):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price, tier_3_price)
        self.tier_4_price = abs(float(tier_4_price))

    def find_method(self, tier, line):
        if f'{tier} ' in line \
                and f'type->fragments' in line \
                and 'scarabs' not in line:
            return True

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '1p'): [],
            (self.contents, '2'): [],
            (self.contents, '3'): [],
            (self.contents, '4'): []
        }
        if not self.items:
            self.take_items()
        for name in self.items[self.contents]:
            price = self.items[self.contents][name]
            if self.remove_exception(name):
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
    def __init__(self, items, contents='oil', parse_file='parse.json',
                 tierlist=('1', '2', '3', '4'),
                 tier_1_price=12, tier_2_price=5, tier_3_price=2):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price, tier_3_price)

    def find_method(self, tier, line):
        if tier in line and f'currency->oil' in line:
            return True


class Resonators(Tiers):
    def __init__(self, items, contents='resonator', parse_file='parse.json',
                 tierlist=('1', '2', '3')):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price=12, tier_2_price=5)

    def find_method(self, tier, line):
        if tier in line and 'resonator' in line:
            return True

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '2'): [],
            (self.contents, '3'): []
        }
        for name in self.items[self.contents]:
            price = self.items[self.contents][name]
            if self.remove_exception(name):
                if price > self.tier_1_price:
                    all_bases[self.contents, '1'].append(name)
                elif self.tier_2_price < price <= self.tier_1_price:
                    all_bases[self.contents, '2'].append(name)
                else:
                    all_bases[self.contents, '3'].append(name)
        return all_bases


class Fossils(Tiers):
    def __init__(self, items, contents='fossil', parse_file='parse.json',
                 tierlist=('1', '2', '4'),
                 tier_1_price=12, tier_2_price=5):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price)

    def find_method(self, tier, line):
        if str(tier) in line and 'fossil' in line:
            return True

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '2'): [],
            (self.contents, '4'): []
        }
        for name in self.items[self.contents]:
            price = self.items[self.contents][name]
            if self.remove_exception(name):
                if price > self.tier_1_price:
                    all_bases[self.contents, '1'].append(name)
                elif self.tier_2_price < price <= self.tier_1_price:
                    all_bases[self.contents, '2'].append(name)
                else:
                    all_bases[self.contents, '4'].append(name)
        return all_bases


class DivinationCards(Tiers):
    def __init__(self, items, contents='card', parse_file='parse.json',
                 tierlist=('1', '2', '3', '4'),
                 tier_1_price=12, tier_2_price=5, tier_3_price=0.65,
                 exception=(
                         'The Demoness', 'The Wolf\'s Shadow', "The Wolf\'s Legacy", 'The Master Artisan',
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
                         'Demigod\'s Wager', 'Emperor\'s Luck', 'Harmony of Souls', 'Imperial Legacy',
                         'Loyalty', 'Lucky Connections', 'Monochrome', 'More is Never Enough', 'No Traces',
                         'Sambodhi\'s Vow', 'The Cacophony', 'The Catalyst', 'The Deal', 'The Fool',
                         'The Gemcutter', 'The Innocent', 'The Inventor', 'The Puzzle', 'The Survivalist',
                         'The Union', 'The Wrath', 'Three Faces in the Dark', 'Three Voices',
                         'Vinia\'s Token', 'The Seeker', 'Buried Treasure', 'The Journey', 'Rain of Chaos',
                         'Her Mask', 'The Gambler', 'The Flora\'s Gift', 'The Scholar'
                 )):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price, tier_3_price)
        self.exception = exception

    def find_method(self, tier, line):
        if 'divination' in line and tier in line and "%H" not in line:
            return True


class UniqueMaps(Tiers):
    def __init__(self, items, contents='unique', parse_file='parse.json',
                 tierlist=('1', '2', '3'),
                 tier_1_price=12, tier_2_price=5):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price)

    def find_method(self, tier, line):
        if f'{tier} ' in line and f'unique->maps' in line:
            return True

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '2'): [],
            (self.contents, '3'): []
        }
        for name in self.items[self.contents]:
            price = self.items[self.contents][name]
            if self.remove_exception(name):
                if price > self.tier_1_price:
                    all_bases[self.contents, '1'].append(name)
                elif self.tier_2_price < price <= self.tier_1_price:
                    all_bases[self.contents, '2'].append(name)
                else:
                    all_bases[self.contents, '3'].append(name)
        return all_bases


class Uniques(Tiers):
    def __init__(self, items, contents='uniques', parse_file='parse.json',
                 tierlist=('1', '2', '4'),
                 tier_1_price=12, tier_2_price=5, tier_3_price=2,
                 exception=(
                         'Amber Amulet', 'Assassin Bow', 'Sapphire Ring', 'Triumphant Lamellar',
                         'Agate Amulet', 'Topaz Ring', 'Saint\'s Hauberk', 'Penetrating Arrow Quiver',
                         'Jade Amulet', 'Two-Stone Ring', 'Leather Belt', 'Imperial Skean', 'Iron Ring',
                         'Magistrate Crown', 'Murder Mitts', 'Onyx Amulet', 'Crusader Gloves',
                         'Studded Belt', 'Sulphur Flask', 'Turquoise Amulet', 'Sorcerer Boots',
                         'Judgement Staff', 'Stibnite Flask', 'Brass Maul', 'Clasped Boots',
                         'Cleaver', 'Coral Ring', 'Crude Bow', 'Crusader Plate', 'Crystal Wand',
                         'Death Bow', 'Fire Arrow Quiver', 'Gavel', 'Gilded Sallet', 'Gnarled Branch',
                         'Goathide Gloves', 'Gold Amulet', 'Golden Buckler', 'Great Crown',
                         'Great Mallet', 'Iron Circlet', 'Iron Hat', 'Iron Mask', 'Iron Staff',
                         'Ironscale Boots', 'Jade Hatchet', 'Jagged Maul', 'Latticed Ringmail',
                         'Leather Hood', 'Long Bow', 'Moonstone Ring', 'Ornate Sword', 'Painted Buckler',
                         'Plank Kite Shield', 'Plate Vest', 'Reaver Sword', 'Reinforced Greaves',
                         'Royal Bow', 'Royal Staff', 'Rusted Sword', 'Scholar Boots',
                         'Serrated Arrow Quiver', 'Sharktooth Arrow Quiver', 'Skinning Knife',
                         'Sledgehammer', 'Spiraled Wand', 'Strapped Leather', 'Tarnished Spirit Shield',
                         'Velvet Gloves', 'Velvet Slippers', 'Vine Circlet', 'War Buckler',
                         'Wild Leather', 'Woodsplitter', 'Cobalt Jewel', 'Crimson Jewel',
                         'Viridian Jewel', 'Simple Robe', 'Cobalt Jewel', 'Crimson Jewel',
                         'Viridian Jewel', 'Amethyst Ring', 'Blue Pearl Amulet', 'Chain Belt',
                         'Citrine Amulet', 'Cloth Belt', 'Clutching Talisman', 'Coral Amulet',
                         'Diamond Ring', 'Greatwolf Talisman', 'Heavy Belt', 'Lapis Amulet',
                         'Opal Ring', 'Paua Amulet', 'Paua Ring', 'Prismatic Ring',
                         'Rotfeather Talisman', 'Ruby Amulet', 'Ruby Ring', 'Rustic Sash',
                         'Wereclaw Talisman', 'Large Cluster Jewel', 'Medium Cluster Jewel',
                         'Small Cluster Jewel', 'Agate Amulet', 'Amethyst Ring', 'Carnal Armour',
                         'Chain Belt', 'Ebony Tower Shield', 'Eternal Sword', 'Goathide Boots',
                         'Golden Plate', 'Harlequin Mask', 'Heavy Belt', 'Hubris Circlet',
                         'Infernal Sword', 'Legion Sword', 'Necromancer Circlet', 'Praetor Crown',
                         'Prophet Crown', 'Ruby Ring', 'Sacrificial Garb', 'Sage Wand', 'Silver Flask',
                         'Terror Claw', 'Topaz Flask', 'Vaal Axe', 'Vaal Gauntlets'
                 ),
                 unique_types=(
                         'flask', 'weapon', 'jewel', 'armour', 'accessory'
                 )):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price, tier_3_price)
        self.unique_types = unique_types
        self.exception = exception

    def find_method(self, tier, line):
        if tier in line \
                and f'type->uniques' in line \
                and 'prophecy' not in line:
            return True

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '2'): [],
            (self.contents, '4'): []
        }
        for contents in self.unique_types:
            for name in self.items[contents]:
                price = self.items[contents][name]
                if self.remove_exception(name):
                    if price > self.tier_1_price:
                        all_bases[self.contents, '1'].append(name)
                    elif self.tier_2_price < price <= self.tier_1_price:
                        all_bases[self.contents, '2'].append(name)
                    else:
                        all_bases[self.contents, '4'].append(name)
        return all_bases


class Scarabs(Tiers):
    def __init__(self, items, contents='scarab', parse_file='parse.json',
                 tierlist=('1', '2'),
                 tier_1_price=12, tier_2_price=5):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price)

    def find_method(self, tier, line):
        if tier in line and self.contents.lower() in line:
            return True

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '2'): []
        }
        for name in self.items[self.contents]:
            price = self.items[self.contents][name]
            if self.remove_exception(name):
                if price > self.tier_1_price:
                    all_bases[self.contents, '1'].append(name)
                elif self.tier_2_price < price <= self.tier_1_price:
                    all_bases[self.contents, '2'].append(name)
        return all_bases


class Incubators(Tiers):
    def __init__(self, items, contents='incubator', parse_file='parse.json',
                 tierlist=('1', '2'),
                 tier_1_price=12, tier_2_price=5):
        super().__init__(items, contents, parse_file, tierlist,
                         tier_1_price, tier_2_price)

    def find_method(self, tier, line):
        if tier in line and self.contents.lower() in line:
            return True

    def take_bases(self):
        all_bases = {
            (self.contents, '1'): [],
            (self.contents, '2'): []
        }
        for name in self.items[self.contents]:
            price = self.items[self.contents][name]
            if self.remove_exception(name):
                if price > self.tier_1_price:
                    all_bases[self.contents, '1'].append(name)
                elif self.tier_2_price < price <= self.tier_1_price:
                    all_bases[self.contents, '2'].append(name)
        return all_bases


items = Tiers().take_items()  # тянем предметы из базы данных

tiers = Tiers(items)
fragments = Fragments(items)
oils = Oils(items)
resonators = Resonators(items)
fossils = Fossils(items)  # tiers are (1, 2, 4) in NeverSink's filter
div_cards = DivinationCards(items)
uni_maps = UniqueMaps(items)  # has only 2 tiers
uniques = Uniques(items)
scarabs = Scarabs(items)
incubators = Incubators(items)

if __name__ == "__main__":
    lines = dict()
    bases = dict()
    filter_file = 'HiEnd.filter'
    tiers.open_filter(filter_file)

    bases.update(fragments.take_bases())
    bases.update(uniques.take_bases())
    bases.update(div_cards.take_bases())
    bases.update(fossils.take_bases())
    bases.update(resonators.take_bases())
    bases.update(scarabs.take_bases())
    bases.update(oils.take_bases())
    bases.update(incubators.take_bases())
    bases.update(uni_maps.take_bases())

    lines.update(uniques.find_lines(filter_file))
    lines.update(fossils.find_lines(filter_file))
    lines.update(oils.find_lines(filter_file))
    lines.update(fragments.find_lines(filter_file))
    lines.update(div_cards.find_lines(filter_file))
    lines.update(resonators.find_lines(filter_file))
    lines.update(incubators.find_lines(filter_file))
    lines.update(uni_maps.find_lines(filter_file))
    lines.update(scarabs.find_lines(filter_file))

    print(f'Lines sorted by values: {tiers.save_filter(lines, bases)}')
    print(bases)
