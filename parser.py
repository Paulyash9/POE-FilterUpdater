import requests
import json
import pandas as pd


class Data:
    def __init__(self, active_leagues=None, all_categories=None):
        if active_leagues is None:
            active_leagues = {'Standard': 'Standard', 'Hardcore': 'Hardcore'}
        if all_categories is None:
            all_categories = dict()
        self.active_leagues = active_leagues
        self.all_categories = all_categories

    def go_url(self, league, category):
        urls = f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}' \
               f'&category={self.get_categories()[category]}'
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

    def get_categories(self):
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
        items = dict()
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

    def currency_check(self, category):
        currency_categories = ('fossil', 'resonator', 'incubator', 'oil', 'flask')
        for currency in currency_categories:
            if currency == category:
                return True

    def make_currency_list(self, league, category):
        items = dict()
        response = requests.get(f'https://api.poe.watch/get?league={self.get_current_leagues()[league]}'
                                f'&category=currency').json()
        df = pd.DataFrame(response, columns=['group', 'name', 'mean'])
        df = df.rename(columns={'mean': 'med'})
        df = df.loc[df['group'] == category]
        df = df.groupby('name', as_index=False)['med'].max()
        items = pd.Series(df.med.values, index=df.name).to_dict()
        return items

    def parse_all(self, league):
        itemlist = dict()
        for category in self.get_categories():
            item = self.parse(league, category)
            itemlist[category] = item
        return itemlist

    def save_parser(self, league, category):
        with open('parser.json', 'w', encoding='utf-8') as file:
            json.dump(self.parse(league, category), file)


if __name__ == '__main__':
    print(Data().get_categories())
    print(Data().parse_all('Current SC'))
