import requests
import json
import pandas


class Data:
    def __init__(self, active_leagues=None, all_categories=None, items=None):
        if active_leagues is None:
            active_leagues = {'Standard': 'Standard', 'Hardcore': 'Hardcore'}
        if all_categories is None:
            all_categories = dict()
        if items is None:
            items = dict()
        self.active_leagues = active_leagues
        self.all_categories = all_categories
        self.items = items

    def go_url(self, league, category):
        urls = f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}' \
               f'&category={self.categories()[category]}'
        response = requests.get(urls).json()
        return response

    def get_current_leagues(self):
        self.active_leagues = {'Standard': 'Standard', 'Hardcore': 'Hardcore'}
        leagues_url = requests.get("https://api.poe.watch/leagues").json()
        for league in leagues_url:
            if league['active'] and league['name'] is not self.active_leagues:
                if league['hardcore']:
                    self.active_leagues.update({'Current HC': league['name']})
                else:
                    self.active_leagues.update({'Current SC': league['name']})
        return self.active_leagues

    def categories(self):
        unnecessary_categories = ('gem', 'base', 'prophecy', 'enchantment', 'beast', 'net', 'vial', 'splinter',
                                  'currency', 'essence', 'piece', 'catalyst', 'influence')
        cat_list = requests.get("https://api.poe.watch/categories").json()
        for category in cat_list:
            if category['name'] == 'currency':
                for group in category['groups']:
                    self.all_categories[group['name']] = group['name']
            else:
                self.all_categories[category['name']] = category['name']
        for category in unnecessary_categories:
            self.all_categories.pop(category)
        return self.all_categories

    def parse(self, league, category):
        if self.currency_check(category):
            return self.make_currency_list(league, category)
        try:
            for index in self.go_url(league, category):
                if index['type'] not in self.items.keys():
                    self.items[index['type']] = index['mean']
            return self.items
        except KeyError:
            for index in self.go_url(league, category):
                if index['name'] not in self.items.keys():
                    self.items[index['name']] = index['mean']
            return self.items

    def uniques_check(self, category):
        uniques = ('accessory', 'armour', 'flask', 'jewel', 'weapon')
        for unique in uniques:
            if category == unique:
                return True

    def make_unique_list(self, league, category):
        unique_list = {'Uniques': {}}
        for index in self.go_url(league, category):
            unique_list['Uniques'][index['type']] = index['mean']
        return unique_list

    def currency_check(self, category):
        currency_categories = ('fossil', 'resonator', 'incubator', 'oil', 'flask')
        for currency in currency_categories:
            if currency == category:
                return True

    def make_currency_list(self, league, category):
        for index in requests.get(f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}'
                                  f'&category=currency').json():
            if index['group'] == category:
                self.items[index['name']] = index['mean']
        return self.items

    def parse_all(self, league):
        for category in self.categories().keys():
            self.all_categories.update({self.all_categories[category]: self.parse(league, category)})
        return self.all_categories

    def save_parser(self, league, category):
        with open('parser.json', 'w', encoding='utf-8') as file:
            json.dump(self.parse(league, category), file)


print(Data().categories())
