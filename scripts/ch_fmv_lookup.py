import sys, json
sys.path.insert(0, 'scripts')
from cardhedger_client import CardHedgerClient

client = CardHedgerClient()

# Get FMV for key players we analyzed
players = [
    ('Juan Soto', 'Juan Soto'),
    ('Bobby Witt Jr', 'Bobby Witt Jr'),
    ('Aaron Judge', 'Aaron Judge'),
    ('Pete Alonso', 'Pete Alonso'),
    ('Garrett Crochet', 'Garrett Crochet'),
    ('Tarik Skubal', 'Tarik Skubal'),
    ('Paul Skenes', 'Paul Skenes'),
    ('Sandy Alcantara', 'Sandy Alcantara'),
    ('Justin Verlander', 'Justin Verlander'),
    ('Max Scherzer', 'Max Scherzer'),
]

print('=== CARD HEDGE FMV DATA ===')
print()
for search_name, display_name in players:
    print(f'--- {display_name} ---')
    try:
        results = client.search_cards(player=search_name, category='Baseball')
        if 'cards' in results:
            rcs = [c for c in results['cards'] if c.get('rookie')]
            if rcs:
                for c in rcs[:3]:
                    card_id = c.get('card_id')
                    name = c.get('description', '?')
                    try:
                        fmv = client.get_fmv(card_id=card_id, grade='PSA 10')
                        price = fmv.get('price', '?')
                        conf = fmv.get('confidence', '?')
                        print(f'  {name}')
                        print(f'    FMV: ${price} (conf: {conf})')
                    except Exception as e:
                        print(f'  {name}: FMV error - {e}')
            else:
                print('  No RC found')
        else:
            print('  No cards found')
    except Exception as e:
        print(f'  Error: {e}')
    print()
