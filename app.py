from flask import Flask, render_template, request
import requests
from datetime import datetime
from timezonefinderL import TimezoneFinder
from pytz import timezone

app = Flask(__name__)

API_KEY = "YOUR  Openweathermap  API KEY"

@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    if request.method == 'POST':
        city = request.form['city'].strip()
        if city:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()

            if data.get("cod") != 200:
                weather_data = {"error": "City not found. Please try again."}
            else:
                # Get latitude and longitude from weather data
                lon = data['coord']['lon']
                lat = data['coord']['lat']

                # Get the timezone name from coordinates
                tf = TimezoneFinder()
                city_timezone = tf.timezone_at(lng=lon, lat=lat)

                # If timezone lookup fails, fallback to UTC
                if city_timezone is None:
                    city_timezone = 'UTC'

                # Use WorldTimeAPI to get accurate local time
                try:
                    time_api_url = f"http://worldtimeapi.org/api/timezone/{city_timezone}"
                    time_response = requests.get(time_api_url)
                    time_data = time_response.json()
                    local_time = datetime.fromisoformat(time_data["datetime"][:-1]).strftime("%A, %d %B %Y | %H:%M:%S")
                except Exception:
                # fallback if API fails
                    local_time = datetime.now(timezone(city_timezone)).strftime("%A, %d %B %Y | %H:%M:%S")


                weather_data = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temp": round(data["main"]["temp"]),
                    "description": data["weather"][0]["description"].title(),
                    "icon": data["weather"][0]["icon"],
                    "time": local_time
                }

    return render_template("index.html", weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)

