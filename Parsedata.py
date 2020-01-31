import requests
import json
import pandas as pd


class Getdata:
    def __init__(self, active_leagues=None, all_categories=None):
        if active_leagues is None:
            active_leagues = {'Standard': 'Standard', 'Hardcore': 'Hardcore'}  # постоянно действующие лиги
        if all_categories is None:
            all_categories = dict()
        self.active_leagues = active_leagues
        self.all_categories = all_categories

    def go_url(self, league, category):
        urls = f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}' \
               f'&category={self.get_categories()[category]}'
        response = requests.get(urls).json()
        return response

    def get_current_leagues(self):  # собираем словарь с действующими лигами
        leagues_url = requests.get("https://api.poe.watch/leagues").json()
        for league in leagues_url:
            if league['active'] and league['name'] is not self.active_leagues:
                if league['hardcore']:
                    self.active_leagues.update({'Current HC': league['name']})
                else:
                    self.active_leagues.update({'Current SC': league['name']})
        return self.active_leagues

    def get_categories(self):  # форимирование словаря с категориями + убираем ненужные категории
        unnecessary_categories = ('gem', 'base', 'prophecy', 'enchantment', 'beast', 'net', 'vial', 'splinter',
                                  'currency', 'essence', 'piece', 'catalyst', 'influence', 'watchstone',
                                  'map')
        cat_list = requests.get("https://api.poe.watch/categories").json()
        for category in cat_list:
            if category['name'] == 'currency' or category['name'] == 'map':
                for group in category['groups']:
                    self.all_categories[group['name']] = group['name']
            else:
                self.all_categories[category['name']] = category['name']
        for category in unnecessary_categories:
            self.all_categories.pop(category)
        return self.all_categories

    def parse(self, league, category):  # выборка конкретной категории в конкретной лиге
        if category == 'scarab' or category == 'fragment':
            return self.make_name_list(league, category)
        if category == 'unique':
            return self.make_type_list(league, category)
        if self.currency_check(category):
            return self.make_currency_list(league, category)
        df = pd.DataFrame(self.go_url(league, category), columns=['type', 'mean'])
        df = df.rename(columns={'mean': 'med'})
        df = df.groupby('type', as_index=False)['med'].max()
        items = pd.Series(df.med.values, index=df.type).to_dict()
        if items == {}:
            df = pd.DataFrame(self.go_url(league, category), columns=['name', 'mean'])
            df = df.rename(columns={'mean': 'med'})
            df = df.groupby('name', as_index=False)['med'].max()
            items = pd.Series(df.med.values, index=df.name).to_dict()
        return items

    def make_name_list(self, league, category):  # выборка по имени предмета
        items = dict()
        response = requests.get(f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}'
                                f'&category=map').json()
        df = pd.DataFrame(response, columns=['group', 'name', 'mean'])
        df = df.rename(columns={'mean': 'med'})
        df = df.loc[df['group'] == category]
        df = df.groupby('name', as_index=False)['med'].max()
        items = pd.Series(df.med.values, index=df.name).to_dict()
        return items

    def make_type_list(self, league, category):  # выборка по "базе предмета"
        response = requests.get(f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}'
                                f'&category=map').json()
        df = pd.DataFrame(response, columns=['group', 'type', 'mean'])
        df = df.rename(columns={'mean': 'med'})
        df = df.loc[df['group'] == category]
        df = df.groupby('type', as_index=False)['med'].max()
        items = pd.Series(df.med.values, index=df.type).to_dict()
        return items

    def currency_check(self, category):  # является ли выбранная категория подкатегорией в 'currency'
        currency_categories = ('fossil', 'resonator', 'incubator', 'oil', 'fragment')
        for currency in currency_categories:
            if currency == category:
                return True

    def make_currency_list(self, league, category):  # выборка предметов подкатегории в 'currency'
        response = requests.get(f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}'
                                f'&category=currency').json()
        df = pd.DataFrame(response, columns=['group', 'name', 'mean'])
        df = df.rename(columns={'mean': 'med'})
        df = df.loc[df['group'] == category]
        df = df.groupby('name', as_index=False)['med'].max()
        items = pd.Series(df.med.values, index=df.name).to_dict()
        return items

    def parse_all(self, league):  # выборка по ВСЕМ категориям, полученным из self.get_categories()
        itemlist = dict()
        for category in self.get_categories().keys():
            item = self.parse(league, category)
            itemlist[category] = item
        return itemlist

    def save_parser(self, league):  # сохранение в формате .json
        with open('parse.json', 'w', encoding='utf-8') as file:
            json.dump(self.parse_all(league), file)
        pass


if __name__ == '__main__':
    print(Getdata().get_categories())
    Getdata().save_parser('Current SC')
