import json

def clean_rating(r):
    try:
        if not r or r.strip() == '-' or r.strip() == 'New': return 3.5
        return float(r)
    except:
        return 3.5

def clean_time(t):
    try:
        t = t.replace('min', '').strip()
        if not t: return "25-40"
        val = int(t)
        return f"{max(10, val-5)}-{val+10}"
    except:
        return "25-40"

def get_tag(cuisines, raw_text=""):
    combined = " ".join(cuisines).lower() + " " + raw_text.lower()
    if 'pizza' in combined or 'italian' in combined: return 'pizza'
    if 'biryani' in combined: return 'biryani'
    if 'chinese' in combined or 'asian' in combined: return 'chinese'
    if 'burger' in combined or 'fast food' in combined: return 'fast'
    if 'cafe' in combined or 'coffee' in combined or 'tea' in combined: return 'cafe'
    if 'healthy' in combined or 'salad' in combined: return 'healthy'
    if 'indian' in combined or 'north indian' in combined or 'mughlai' in combined: return 'indian'
    if 'bakery' in combined or 'dessert' in combined or 'cake' in combined or 'ice cream' in combined: return 'cafe'
    if 'street food' in combined or 'chaat' in combined: return 'indian'
    return 'indian'

# 10 diverse menu templates
MENUS = {
    'pizza': [
        {"section": "Pizzas", "items": [
            {"name": "Margherita Pizza", "desc": "Classic mozzarella and basil on tomato sauce", "price": 199, "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=200&h=200&fit=crop"},
            {"name": "Farmhouse Pizza", "desc": "Capsicum, onion, tomato and mushroom", "price": 349, "image": "https://images.unsplash.com/photo-1594007654729-407eedc4be65?w=200&h=200&fit=crop"},
            {"name": "Peppy Paneer Pizza", "desc": "Paneer cubes with capsicum and spicy sauce", "price": 299, "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=200&h=200&fit=crop"},
            {"name": "Chicken Supreme", "desc": "Loaded with chicken tikka and veggies", "price": 449, "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=200&h=200&fit=crop"},
            {"name": "Garlic Breadsticks", "desc": "Cheesy garlic bread with dip", "price": 129, "image": "https://images.unsplash.com/photo-1619535860434-ba1d8fa12536?w=200&h=200&fit=crop"},
            {"name": "Pasta Alfredo", "desc": "Creamy white sauce penne pasta", "price": 249, "image": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=200&h=200&fit=crop"},
            {"name": "Choco Lava Cake", "desc": "Warm molten chocolate cake", "price": 99, "image": "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=200&h=200&fit=crop"},
        ]},
    ],
    'indian': [
        {"section": "Main Course", "items": [
            {"name": "Butter Chicken", "desc": "Tender chicken in rich tomato-butter gravy", "price": 320, "image": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=200&h=200&fit=crop"},
            {"name": "Dal Makhani", "desc": "Slow-cooked black lentils with cream", "price": 220, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=200&h=200&fit=crop"},
            {"name": "Paneer Tikka Masala", "desc": "Grilled paneer in spiced onion-tomato gravy", "price": 280, "image": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=200&h=200&fit=crop"},
            {"name": "Chole Bhature", "desc": "Spiced chickpeas served with fried bread", "price": 150, "image": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=200&h=200&fit=crop"},
            {"name": "Kadhai Paneer", "desc": "Cottage cheese with bell peppers in kadhai masala", "price": 260, "image": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=200&h=200&fit=crop"},
            {"name": "Garlic Naan", "desc": "Tandoori naan brushed with garlic butter", "price": 60, "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=200&h=200&fit=crop"},
            {"name": "Jeera Rice", "desc": "Basmati rice tempered with cumin seeds", "price": 130, "image": "https://images.unsplash.com/photo-1596560548464-f010549b84d7?w=200&h=200&fit=crop"},
            {"name": "Gulab Jamun (2 pcs)", "desc": "Deep-fried milk dumplings in sugar syrup", "price": 80, "image": "https://images.unsplash.com/photo-1666190073498-c4706e30f531?w=200&h=200&fit=crop"},
        ]},
    ],
    'indian2': [
        {"section": "Specials", "items": [
            {"name": "Amritsari Kulcha", "desc": "Stuffed kulcha with chole and pickle", "price": 140, "image": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=200&h=200&fit=crop"},
            {"name": "Tandoori Chicken (Half)", "desc": "Charcoal grilled marinated chicken", "price": 250, "image": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=200&h=200&fit=crop"},
            {"name": "Shahi Paneer", "desc": "Paneer in rich cashew and cream gravy", "price": 260, "image": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=200&h=200&fit=crop"},
            {"name": "Chicken Biryani", "desc": "Dum-cooked aromatic rice with chicken", "price": 280, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=200&h=200&fit=crop"},
            {"name": "Aloo Paratha", "desc": "Stuffed potato flatbread with butter and curd", "price": 80, "image": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=200&h=200&fit=crop"},
            {"name": "Lassi (Sweet)", "desc": "Thick creamy yogurt drink", "price": 60, "image": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=200&h=200&fit=crop"},
            {"name": "Raita", "desc": "Seasoned yogurt with cucumber and onion", "price": 50, "image": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=200&h=200&fit=crop"},
            {"name": "Samosa (2 pcs)", "desc": "Crispy fried pastry with spiced potato filling", "price": 40, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=200&h=200&fit=crop"},
        ]},
    ],
    'fast': [
        {"section": "Burgers and Sides", "items": [
            {"name": "Classic Veg Burger", "desc": "Crispy aloo tikki patty with lettuce and mayo", "price": 99, "image": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=200&h=200&fit=crop"},
            {"name": "Chicken Zinger", "desc": "Crispy fried chicken fillet with spicy mayo", "price": 179, "image": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=200&h=200&fit=crop"},
            {"name": "Paneer Wrap", "desc": "Grilled paneer tikka in a soft tortilla", "price": 149, "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=200&h=200&fit=crop"},
            {"name": "French Fries (Large)", "desc": "Golden crispy salted fries", "price": 119, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=200&h=200&fit=crop"},
            {"name": "Chicken Wings (6 pcs)", "desc": "Spicy fried chicken wings with dip", "price": 199, "image": "https://images.unsplash.com/photo-1608039829572-9b0189250165?w=200&h=200&fit=crop"},
            {"name": "Cold Coffee", "desc": "Iced blended coffee with cream", "price": 129, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=200&h=200&fit=crop"},
            {"name": "Chocolate Shake", "desc": "Thick chocolate milkshake", "price": 149, "image": "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=200&h=200&fit=crop"},
        ]},
    ],
    'chinese': [
        {"section": "Chinese Favourites", "items": [
            {"name": "Veg Hakka Noodles", "desc": "Stir-fried noodles with mixed vegetables", "price": 160, "image": "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=200&h=200&fit=crop"},
            {"name": "Chilli Chicken (Dry)", "desc": "Indo-Chinese style spicy chicken", "price": 250, "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=200&h=200&fit=crop"},
            {"name": "Veg Manchurian (Gravy)", "desc": "Crispy veg balls in soy-chilli gravy", "price": 180, "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=200&h=200&fit=crop"},
            {"name": "Fried Rice", "desc": "Wok-tossed rice with vegetables and soy sauce", "price": 170, "image": "https://images.unsplash.com/photo-1596560548464-f010549b84d7?w=200&h=200&fit=crop"},
            {"name": "Momos (8 pcs)", "desc": "Steamed dumplings with spicy red chutney", "price": 120, "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=200&h=200&fit=crop"},
            {"name": "Spring Rolls (4 pcs)", "desc": "Crispy rolls stuffed with vegetables", "price": 140, "image": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=200&h=200&fit=crop"},
            {"name": "Honey Chilli Potato", "desc": "Crispy potatoes in sweet and spicy sauce", "price": 160, "image": "https://images.unsplash.com/photo-1562967914-608f82629710?w=200&h=200&fit=crop"},
        ]},
    ],
    'biryani': [
        {"section": "Biryani and More", "items": [
            {"name": "Chicken Dum Biryani", "desc": "Slow-cooked aromatic basmati with chicken", "price": 280, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=200&h=200&fit=crop"},
            {"name": "Veg Biryani", "desc": "Fragrant rice with mixed vegetables and spices", "price": 220, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=200&h=200&fit=crop"},
            {"name": "Mutton Biryani", "desc": "Rich goat meat biryani with saffron", "price": 380, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=200&h=200&fit=crop"},
            {"name": "Chicken Tikka", "desc": "Charcoal grilled boneless chicken pieces", "price": 220, "image": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=200&h=200&fit=crop"},
            {"name": "Seekh Kebab (4 pcs)", "desc": "Minced mutton kebabs from the grill", "price": 260, "image": "https://images.unsplash.com/photo-1603360946369-dc9bb6258143?w=200&h=200&fit=crop"},
            {"name": "Raita", "desc": "Cool yogurt with cucumber and mint", "price": 50, "image": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=200&h=200&fit=crop"},
            {"name": "Gulab Jamun (4 pcs)", "desc": "Warm fried milk dumplings in syrup", "price": 80, "image": "https://images.unsplash.com/photo-1666190073498-c4706e30f531?w=200&h=200&fit=crop"},
        ]},
    ],
    'cafe': [
        {"section": "Beverages and Snacks", "items": [
            {"name": "Cappuccino", "desc": "Espresso with steamed milk foam", "price": 159, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=200&h=200&fit=crop"},
            {"name": "Cold Coffee", "desc": "Iced blended coffee with cream", "price": 179, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=200&h=200&fit=crop"},
            {"name": "Veg Grilled Sandwich", "desc": "Toasted sandwich with cheese and veggies", "price": 149, "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=200&h=200&fit=crop"},
            {"name": "Chocolate Brownie", "desc": "Warm gooey chocolate brownie with ice cream", "price": 169, "image": "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=200&h=200&fit=crop"},
            {"name": "Masala Chai", "desc": "Traditional spiced Indian tea", "price": 49, "image": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=200&h=200&fit=crop"},
            {"name": "Maggi Noodles", "desc": "Classic Indian-style instant noodles with veggies", "price": 89, "image": "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=200&h=200&fit=crop"},
            {"name": "Cheese Garlic Bread", "desc": "Toasted garlic bread with mozzarella", "price": 129, "image": "https://images.unsplash.com/photo-1619535860434-ba1d8fa12536?w=200&h=200&fit=crop"},
        ]},
    ],
    'healthy': [
        {"section": "Healthy Bites", "items": [
            {"name": "Veg Sub Sandwich", "desc": "Fresh veggies in a sub roll with choice of sauce", "price": 179, "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=200&h=200&fit=crop"},
            {"name": "Chicken Teriyaki Sub", "desc": "Grilled chicken with teriyaki glaze", "price": 249, "image": "https://images.unsplash.com/photo-1521390188846-e2a3a97453a0?w=200&h=200&fit=crop"},
            {"name": "Paneer Tikka Wrap", "desc": "Grilled paneer in a whole wheat wrap", "price": 199, "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=200&h=200&fit=crop"},
            {"name": "Caesar Salad", "desc": "Romaine lettuce with croutons and dressing", "price": 179, "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop"},
            {"name": "Fresh Fruit Juice", "desc": "Seasonal fresh-pressed juice", "price": 99, "image": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=200&h=200&fit=crop"},
            {"name": "Corn and Cheese Sandwich", "desc": "Sweet corn with melted cheese on toast", "price": 149, "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=200&h=200&fit=crop"},
        ]},
    ],
}

# Alternating indian menus to add variety
def get_menu(tag, idx):
    if tag == 'indian':
        return MENUS['indian'] if idx % 2 == 0 else MENUS['indian2']
    if tag in MENUS:
        return MENUS[tag]
    # fallback cycle
    fallback = ['indian', 'fast', 'chinese', 'cafe']
    return MENUS[fallback[idx % len(fallback)]]

def generate_js_file(city_name, json_file, js_var_name, out_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data = data[:50]
    out_list = []
    prefix = city_name[:3].lower()
    default_img = 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=250&fit=crop'
    
    for i, r in enumerate(data):
        img = r.get('image', '')
        if not img or 'zomato.com/' in img and '/delivery' in img:
            img = default_img
        
        tag = get_tag(r.get('cuisines', []), r.get('raw_text', ''))
        rating = clean_rating(r.get('rating'))
        
        badge = None
        if rating >= 4.3: badge = "Top Rated"
        elif rating >= 4.0: badge = "Popular"
        
        res_obj = {
            "id": f"{prefix}-{i+1}",
            "name": r.get('name', 'Restaurant'),
            "city": city_name,
            "image": img,
            "bg": "#ffffff",
            "rating": rating,
            "time": clean_time(r.get('delivery_time', '')),
            "fee": 0 if i % 5 == 0 else 20,
            "tag": tag,
            "badge": badge,
            "address": r.get('raw_text', '').split('\n')[0] + ', ' + city_name if r.get('raw_text') else f"{city_name}",
            "menu": get_menu(tag, i)
        }
        # Clean address to just restaurant name + city
        res_obj["address"] = f"{city_name}"
        out_list.append(res_obj)
    
    js_content = f"// {city_name} Restaurants - 50 entries\nconst {js_var_name} = " + json.dumps(out_list, indent=2, ensure_ascii=False) + ";\n"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"  {out_file}: {len(out_list)} restaurants")

if __name__ == "__main__":
    print("Generating restaurant data files...")
    generate_js_file("Chandigarh", "restaurants.json", "CHANDIGARH_RESTAURANTS", "data-chandigarh.js")
    generate_js_file("Patiala", "restaurants_Patiala.json", "PATIALA_RESTAURANTS", "data-patiala.js")
    generate_js_file("Rajpura", "restaurants_rajpura.json", "RAJPURA_RESTAURANTS", "data-rajpura.js")
    print("Done!")
