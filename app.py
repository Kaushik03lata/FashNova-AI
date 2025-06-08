from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
import pickle
import numpy as np

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("WEATHER_API_KEY")

import joblib

model = joblib.load('outfit_model.pkl')
le_mood = joblib.load('le_mood.pkl')
le_gender = joblib.load('le_gender.pkl')
le_weather = joblib.load('le_weather.pkl')
le_style = joblib.load('le_style.pkl')
le_outfit = joblib.load('le_outfit.pkl')


def interpret_temp(temp):
    if temp < 10:
        return "It's quite cold ❄️. Wear something warm!"
    elif temp < 20:
        return "Chilly outside 🍃. A light jacket would work."
    elif temp < 30:
        return "Pleasant weather ☀️. Go for comfort!"
    else:
        return "It's hot 🔥. Wear something light and airy!"

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    mood = request.form.get('mood')
    city = request.form.get('city')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    style = request.form.get('style')
    gender = request.form.get('gender')

    # Check for missing inputs
    if not mood or not style or not gender:
        return render_template('index.html', error="Please select mood, style, and gender.")

    # Determine weather API URL
    if lat and lon:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    elif city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    else:
        return render_template('index.html', error="Please enter a city or enable location.")

    # Fetch weather
    response = requests.get(url)
    if response.status_code != 200:
        return render_template('index.html', error="Could not fetch weather. Try again.")

    data = response.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"].capitalize()
    city_name = data["name"]

    # Map temperature to weather category label for encoding
    if temp < 15:
        weather_cat = 'Cold'
    elif temp < 25:
        weather_cat = 'Mild'
    else:
        weather_cat = 'Warm'

    # ML Prediction
    try:
        mood_enc = le_mood.transform([mood])[0]
        gender_enc = le_gender.transform([gender])[0]
        style_enc = le_style.transform([style])[0]
        weather_enc = le_weather.transform([weather_cat])[0]   # <-- encode weather here
    except Exception as e:
        return render_template('index.html', error=f"Invalid input values: {e}")

    # Provide all 4 features to the model
    features = np.array([[mood_enc, gender_enc, weather_enc, style_enc]])
    pred_index = model.predict(features)[0]
    outfit = le_outfit.inverse_transform([pred_index])[0]

    # Refine outfit if weather inappropriate
    outfit = refine_outfit_for_weather(outfit, temp)

    # Generate Amazon & Flipkart links
    search_query = outfit.replace(" ", "+")
    amazon_link = f"https://www.amazon.in/s?k={search_query}"
    flipkart_link = f"https://www.flipkart.com/search?q={search_query}"

    weather_tip = interpret_temp(temp)

    return render_template(
        'index.html',
        mood=mood,
        city=city_name,
        temp=temp,
        description=desc,
        outfit=outfit,
        amazon_link=amazon_link,
        flipkart_link=flipkart_link,
        weather_tip=weather_tip,
        style=style,
        gender=gender,
    )


def refine_outfit_for_weather(outfit, temp):
    """Modify the outfit suggestion if it contradicts the weather"""
    outfit_lower = outfit.lower()

    if temp > 35:  # Very hot
        if any(keyword in outfit_lower for keyword in ['blazer', 'jacket', 'sweater', 'coat']):
            return "Light cotton shirt with shorts 👕🩳 (adjusted for hot weather)"
    elif temp < 10:  # Very cold
        if any(keyword in outfit_lower for keyword in ['t-shirt', 'crop top', 'shorts']):
            return "Warm hoodie and jeans 🧥👖 (adjusted for cold weather)"
    
    return outfit


if __name__ == '__main__':
    app.run(debug=True)
