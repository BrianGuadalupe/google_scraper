# 📍 Google Maps Business Scraper

A visual app built with **Streamlit** and **Selenium** to search for businesses on Google Maps and automatically extract their information (name, address, phone number, and website) in a visual and user-friendly way.

---

## 🚀 Features

- Intuitive interface
- Google Maps search
- Scrapes business name, address, phone number, and website
- Results displayed as visual cards
- Option to download as CSV

---

## 📷 Interface Screenshot

![image](https://github.com/user-attachments/assets/6da676ab-fb4a-4df6-9838-107738f14aed)

---

## ⚙️ Requirements

- Python 3.8+
- Google Chrome
- Dependencies:

pip install streamlit selenium webdriver-manager pandas

---

## ▶️ How to Use

1. Clone the repository:

git clone https://github.com/BrianGuadalupe/google_scraper.git
cd google_scraper

2. Install the required packages:

pip install -r requirements.txt

3. Run the app:

streamlit run app.py

---

## 📁 Project Structure

google_scraper/

├── app.py                   # Main Streamlit application

├── scraper_google_maps.py   # Standalone CLI scraper

├── maps_utils.py            # Shared driver and cookie helpers

├── .gitignore

├── requirements.txt         # Required dependencies

└── README.md                # This file

---

## 📦 Generate `requirements.txt`

If you don’t have it yet, you can generate it with:

pip freeze > requirements.txt

---

## ⚠️ Legal Disclaimer

This project is intended **exclusively for educational and research purposes**.

- Using this tool may violate [Google Maps Terms of Service](https://cloud.google.com/maps-platform/terms), which prohibit automated scraping of their platform.
- The author is not responsible for any misuse of this code by third parties.
- **Do not use this tool for commercial purposes or large-scale data collection.**
- For production use, use the official [Google Maps Platform API](https://developers.google.com/maps), which offers a free tier of $200/month in credits.

By using this repository you accept full responsibility for how you use it.

---

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and share it.

---

## ✨ Author

Created with ❤️ by Brian Guadalupe (https://github.com/BrianGuadalupe)
