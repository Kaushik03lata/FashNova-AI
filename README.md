# FashNova AI 👕✨  

A Flask‑based AI outfit recommender that blends **mood**, **style preference**, **gender**, and **real‑time weather** to suggest the perfect look (plus “buy on Amazon / Flipkart” links and Pinterest inspiration).

---

## ✨ Features
- 7 mood buttons (Happy, Lazy, Excited, Sad, Angry, Neutral, Romantic) with live highlight  
- Recommends gender‑aware outfits from a trained Random‑Forest model  
- Weather fetched from **OpenWeather** → converted to _Cold / Mild / Warm_ category  
- Auto‑generated shopping links + Pinterest search  
- Stylish gradient UI (lavender × purple palette)  

---

## 🖥️ Local Setup

```bash
# clone & enter repo
git clone https://github.com/<your‑username>/fashnova-ai.git
cd fashnova-ai

# create venv (optional)
python -m venv venv
source venv/bin/activate  # .\venv\Scripts\activate on Windows

# install dependencies
pip install -r requirements.txt

# set weather key (one‑off)
export WEATHER_API_KEY=<your‑openweather-key>

# run
python app.py
