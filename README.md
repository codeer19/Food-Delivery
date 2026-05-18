# 🍛 Plat — Food Delivery App

A beautiful, modern food delivery web application featuring **real Indian restaurants** from Chandigarh with authentic menus and ₹ pricing.

![HTML](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)

---

## ✨ Features

- **10 Real Indian Restaurants** — Haveli, Pizza Hut, McDonald's, Haldiram's, Barbeque Nation, Behrouz Biryani, Subway, Amritsari Kulcha Hub, Domino's, Sagar Ratna
- **Authentic Menus** — Butter Chicken, Chole Bhature, Masala Dosa, Amritsari Kulcha, Biryani and more with realistic ₹ pricing
- **Category Filters** — Filter by Indian, Fast Food, Pizza, Biryani, Healthy
- **Search** — Search for restaurants or specific dishes
- **Cart System** — Add items, adjust quantities, view subtotal with delivery charges
- **Order Tracking** — Place orders and view history with status tracking
- **Responsive Design** — Works on desktop, tablet, and mobile
- **Premium UI** — Warm editorial design with Fraunces + DM Sans typography, smooth animations, and micro-interactions

---

## 🚀 Getting Started

### Option 1: Open directly in browser

Simply open `index.html` in your browser:

```bash
# Double-click index.html, or:
start index.html        # Windows
open index.html         # macOS
xdg-open index.html     # Linux
```

### Option 2: Use a local server (recommended)

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .

# Using VS Code
# Install "Live Server" extension → Right-click index.html → "Open with Live Server"
```

Then visit `http://localhost:8000`

---

## 📁 Project Structure

```
food delivery/
├── index.html      # Main HTML page (nav, hero, filters, modals, cart drawer)
├── style.css       # Complete styling (warm editorial theme, responsive)
├── app.js          # Application logic (data, rendering, cart, orders)
└── README.md       # This file
```

---

## 🍽️ Restaurants & Menus

| # | Restaurant | Cuisine | Price Range | Delivery |
|---|-----------|---------|-------------|----------|
| 1 | Haveli | North Indian | ₹60 – ₹320 | ₹30 |
| 2 | Pizza Hut | Pizza | ₹139 – ₹529 | Free |
| 3 | McDonald's | Fast Food | ₹59 – ₹219 | ₹20 |
| 4 | Haldiram's | Indian Snacks | ₹60 – ₹160 | ₹25 |
| 5 | Barbeque Nation | Premium Indian | ₹295 – ₹420 | ₹40 |
| 6 | Behrouz Biryani | Biryani | ₹69 – ₹449 | ₹15 |
| 7 | Subway | Healthy/Subs | ₹179 – ₹299 | Free |
| 8 | Amritsari Kulcha Hub | Punjabi | ₹30 – ₹140 | ₹30 |
| 9 | Domino's Pizza | Pizza | ₹199 – ₹459 | Free |
| 10 | Sagar Ratna | South Indian | ₹60 – ₹160 | ₹20 |

---

## 🎨 Design System

- **Typography**: Fraunces (headings) + DM Sans (body)
- **Colors**: Warm paper background (`#faf8f5`), terracotta accent (`#c8502a`)
- **Layout**: CSS Grid for restaurant cards, Flexbox for components
- **Animations**: Smooth transitions on hover, slide-in cart drawer, bottom-sheet modal

---

## 🛠️ Customization

### Change City / Restaurants

Edit the `APP_LOCATION` and `data` object in `app.js`:

```javascript
const APP_LOCATION = 'Mumbai'; // Change city name

const data = {
  featured: [ /* your trending items */ ],
  restaurants: [ /* your restaurants with menus */ ],
};
```

### Add a New Restaurant

Add an entry to `data.restaurants` in `app.js`:

```javascript
{
  id: 11,
  name: 'Your Restaurant',
  emoji: '🍲',
  bg: '#fef3c7',           // Card background color
  rating: 4.5,
  time: '25–35',           // Delivery time
  fee: 25,                 // Delivery fee in ₹ (0 = free)
  tag: 'indian',           // Filter category
  badge: 'New',            // Badge text (or null)
  address: 'Your Address',
  menu: [
    {
      section: 'Section Name',
      items: [
        { emoji: '🍲', name: 'Dish Name', desc: 'Description', price: 250 },
      ],
    },
  ],
}
```

### Available Filter Tags

`indian` · `fast` · `pizza` · `biryani` · `healthy`

---

## 📝 Why Not a Live API?

No free public API provides **both restaurant names and menus** for India:

| API | Restaurant Names | Menu Items | India Coverage | Free Tier |
|-----|:---:|:---:|:---:|:---:|
| Zomato | ✅ | ✅ | ✅ | ❌ (API shut down) |
| Swiggy | ✅ | ✅ | ✅ | ❌ (No public API) |
| Foursquare | ✅ | ❌ | Partial | ✅ |
| Google Places | ✅ | ❌ | ✅ | Paid only |

This app uses a **curated dataset** of real Indian restaurant chains with authentic menus and pricing, which provides a better UX than broken API calls with placeholder menus.

---

## 📄 License

MIT — free to use and modify.
