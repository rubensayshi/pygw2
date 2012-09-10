from __future__ import division

from urllib import urlencode
import requests
import json

ITEM_RARITY = {
    0: {'name': "Junk", 'color': '#AAAAAA'},
    1: {'name': "Basic", 'color': '#FFFFFF'},
    2: {'name': "Fine", 'color': '#62A4DA'},
    3: {'name': "Masterwork", 'color': '#1A9306'},
    4: {'name': "Rare", 'color': '#FCD00B'},
    5: {'name': "Exotic", 'color': '#FFA405'},
    6: {'name': "Legendary", 'color': '#800080'},
    7: {'name': "Mystic", 'color': '#FD4627'},
}

ITEM_TYPES = {
    0: {'name': "Armor", 'subtypes': {0: 'Coat', 1: 'Leggings', 2: 'Gloves', 3: 'Helm', 4: 'Aquatic Helm', 5: 'Boots', 6: 'Shoulders'}},
    2: {'name': "Bag"},
    3: {'name': "Consumable", 'subtypes': {1: "Food", 3: "Generic", 5: "Transmutation", 6: "Unlock"}},
    4: {'name': "Container", 'subtypes': {0: "Default", 1: "Gift Box"}},
    5: {'name': "Crafting Material"},
    6: {'name': "Gathering", 'subtypes': {0: "Foraging", 1: "Logging", 2: "Mining"}},
    7: {'name': "Gizmo", 'subtypes': {0: "Default", 2: "Salvage"}},
    11: {'name': "Mini"},
    13: {'name': "Tool", 'subtypes': {2: "Salvage"}},
    15: {'name': "Trinket", 'subtypes': {0: "Accessory", 1: "Amulet", 2: "Ring"}},
    16: {'name': "Trophy"},
    17: {'name': "Upgrade Component", 'subtypes': {0: "Weapon", 2: "Armor"}},
    18: {'name': "Weapon", 'subtypes': {
        4: 'Axe',
        5: 'Dagger',
        13: 'Focus',
        6: 'Greatsword',
        1: 'Hammer',
        20: 'Harpoon Gun',
        2: 'Longbow',
        7: 'Mace',
        8: 'Pistol',
        10: 'Rifle',
        11: 'Scepter',
        16: 'Shield',
        3: 'Short Bow',
        19: 'Spear',
        12: 'Staff',
        0: 'Sword',
        14: 'Torch',
        22: 'Toy',
        21: 'Trident',
        15: 'Warhorn',
    }},
}

class API(object):
    def __init__(self, session_id):
        self.session_id = session_id
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1003.1 Safari/535.19 Awesomium/1.7.1'

        self.trading_post_headers = {
            'Accept-Language': 'en',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest', # I think this one is absolutely needed
            'Referer': 'https://tradingpost-live.ncplatform.net/',
        }

    def is_trading_post_online(self):
        """Determine the status of the trading post, if it is online or not."""
        url = 'https://tradingpost-live.ncplatform.net/'
        headers = {'Accept-Language': 'en', 'User-Agent': self.user_agent}
        response = requests.get(url, headers=headers, cookies={'s': self.session_id})
        if response.status_code != requests.codes.ok:
            return False
        return True

    def get_currency_rates(self):
        # Numbers to query, too high causes inaccuracies, too low is inaccurate
        gems = 100000
        coins = 10000000

        url = 'https://exchange-live.ncplatform.net/ws/rates.json?gems=%d&coins=%d' % (gems, coins)

        headers = {
            'Accept-Language': 'en',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://exchange-live.ncplatform.net/',
        }

        response = requests.get(url, headers=headers, cookies={'s': self.session_id})
        response.raise_for_status()

        # Information is JSON encoded
        data = json.loads(response.content)

        sell = int(data['results']['coins']['quantity']) / gems
        buy = coins / int(data['results']['gems']['quantity'])

        return {'buy': buy, 'sell': sell}

    def get_currency_supply(self):
        gems = 10000000000000000
        coins = 10000000000000000
        url = 'https://exchange-live.ncplatform.net/ws/rates.json?gems=%d&coins=%d' % (gems, coins)        
        headers = {
            'Accept-Language': 'en',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://exchange-live.ncplatform.net/',
        }

        response = requests.get(url, headers=headers, cookies={'s': self.session_id})
        response.raise_for_status()

        # Information is JSON encoded
        data = json.loads(response.content)

        return {'gems': int(data['results']['gems']['quantity']), 'coins': int(data['results']['coins']['quantity'])}

    def get_item_info(self, item_id):
        """Get information about the provided item id."""
        url = 'https://tradingpost-live.ncplatform.net/ws/search.json?ids=%d' % item_id

        # Try to look legit
        headers = {
            'Accept-Language': 'en',
            'User-Agent': self.user_agent,
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://tradingpost-live.ncplatform.net/',
        }

        # Get the response
        response = requests.get(url, headers=headers, cookies={'s': self.session_id})
        response.raise_for_status()

        result = json.loads(response.content)

        item_data = result['results'][0]
        return item_data

        #json_data = '{"args":{"offset":1,"count":10,"text":""},"total":1,"results":[{"type_id":"3","data_id":"19697","restriction_level":"0","rarity":"1","vendor_sell_price":"1","max_offer_unit_price":"18","offer_availability":"239870","min_sale_unit_price":"23","sale_availability":"55067","name":"Copper Ore","description":"Refine into Copper Ingots or use Tin to refine into Bronze Ingots.","gem_store_description":"","gem_store_blurb":"","img":"https://dfach8bufmqqv.cloudfront.net/gw2/img/content/c1a3e75a.png","rarity_word":"Basic"}]}'
        #result = json.loads(json_data)
        

    def _request(self, url):
        """Convenience method to make a request to the GW2 HTTPS server."""
        # Make the request
        response = requests.get(url, headers=self.trading_post_headers, cookies={'s': self.session_id})
        # Raise any erroneous states
        response.raise_for_status()
        # The response should be a JSON document
        assert response.headers['Content-Type'] == 'application/json', "Response isn't JSON"
        # All done :)
        return json.loads(response.content)

    def _process_item(self, item):
        """Make structures of item information a little more presentable."""
        # Numbers should be numbers
        for key_name in ['data_id', 'type_id', 'vendor_sell_price', 'min_sale_unit_price', 
            'max_offer_unit_price', 'rarity', 'restriction_level', 'offer_availability', 'sale_availability']:
            if key_name in item and item[key_name].isdigit():
                item[key_name] = int(item[key_name])

        # Nothing should be nothing
        for key_name in ['gem_store_description', 'gem_store_blurb', 'description']:
            if key_name in item and item[key_name] == '':
                item[key_name] = None

        # All done :)
        return item

    def get_listings(self, item_id, type):
        if type not in ['buys', 'sells']:
            raise ValueError("Type is invalid, expected 'buys' or 'sells' got: %r" % type)
        
        url = 'https://tradingpost-live.ncplatform.net/ws/listings.json?' + urlencode({'id': item_id, 'type': type})

        listings = self._request(url)

        result = {}

        for listing_info in listings['listings'][type]:
            result[int(listing_info['unit_price'])] = {'quantity': int(listing_info['quantity']), 'listings': int(listing_info['listings'])}

        return result

    def search_trading_post(self, text=None, type=None, subtype=None, levelmin=0, levelmax=80, rarity=0, removeunavailable=False):
        """Iterates over Trading Post search results.

        Arguments:
            text: Piece of text to search by, AFAICT this string can appear anywhere in the name of the item for a match.
            type: Item type to limit results by, see the ITEM_TYPES structure for more info.
            subtype: Item subtype to limit results by, see the ITEM_TYPES structure for more info.
            levelmin: Only return items that are higher than this level (not sure if it is inclusive).
            levelmax: Only return items that are lower than this level (not sure if it is inclusive).
            rarity: Minimum rarity level, see the ITEM_RARITY structure.
            removeunavailable: Not sure what this does, only returns items that can be purchased?
        """

        # URL-arguments for expressing the kind of items we want
        args = {
            'text': text or '',
            'levelmin': levelmin,
            'levelmax': levelmax,

            # Pagination uses offsets (skip) and is 1-based
            'offset': 1
        }
        # Don't include these arguments unless they are needed (try to look legit)
        if rarity: args['rarity'] = rarity
        if type is not None: args['type'] = type
        if subtype is not None: args['subtype'] = subtype
        if removeunavailable: args['removeunavailable'] = 'true'

        # This behaves oddly, offset doesn't work with ids queries
        #if ids is not None:
        #    if not isinstance(ids, list): ids = [ids]
        #    args['ids'] = ','.join([str(item_id) for item_id in ids])

        # Endlessly loop until we've exhausted all the items
        while True: 
            # Construct URL
            url = 'https://tradingpost-live.ncplatform.net/ws/search.json?' + urlencode(args)

            # Make the request
            results = self._request(url)

            # When we've got a page that doesn't contain any items: we're done here
            if len(results['results']) == 0: break

            # Pass out each item
            for item in results['results']:
                yield self._process_item(item)

            # Add to the offset so the next loop gets the next 'page'
            args['offset'] += int(results['args']['count'])

def main():
    api = API('ENTER_YOUR_SESSION_KEY_HERE')
    print api.get_currency_rates()

if __name__ == '__main__':
    main()