import json
from models import db, Item, Effect, Flavor
from random import randint, choices

db.drop_all()
db.create_all()

def get_data():
    data_lst = []
    with open('./data/additional_data.txt') as json_file:
        data = json.load(json_file)
        for flavor in data['flavors']:
            new_flavor = Flavor(id=int(flavor['id']), name=flavor['name'])
            data_lst.append(new_flavor)
        
        for effect in data['effects']:
            new_effect = Effect(id=int(effect['id']), name=effect['name'], effect_type=effect['effect_type'])
            data_lst.append(new_effect)
        
    db.session.add_all(data_lst)

    try:
        db.session.commit()
        print('success')

    except:
        print('Could not commit to db.')
    
def get_strains():
    data_lst = []
    with open('./data/strains.txt') as json_file:
        data = json.load(json_file)
        for item in data['strains']:
            print(item['id'], item['name'])
            new_item = Item(id=int(item['id']),
                            name=item['name'],
                            description=str(item['description']),
                            race=str(item['race']).title(),
                            price=randint(0, 80))
            data_lst.append(new_item)

    final_items = choices(data_lst, k=500)

    db.session.add_all(final_items)
    db.session.commit()
    print("SUCCESS")
    
def add_attrs_to_items():
    effects = [e.name for e in Effect.query.all()]
    
    with open('./data/strains.txt') as json_file:
        data = json.load(json_file)
        for item in data['strains']:
            comp_strain = Item.query.filter(
                Item.name == item['name']
            ).first()
            effect_lst = item['effects']
            flavor_lst = item['flavors']
            
            if comp_strain != None:
                for effect in effect_lst:
                    if effect in effects:
                        effect_to_add = Effect.query.filter_by(name=effect).first()
                        comp_strain.effects.append(effect_to_add)
                        
                for flavor in flavor_lst:
                    if flavor in flavor_lst:
                        flavor_to_add = Flavor.query.filter_by(name=flavor).first()
                        comp_strain.flavors.append(flavor_to_add)
            else:
                print('pass')
                
        
            
        try:
            db.session.commit()
            print("SUCCESS!")
        except:
            db.session.rollback()
            print("Error associating data. Check logs for details.")

get_data()        
get_strains()
add_attrs_to_items()