import tkinter as tk
from tkinter import messagebox
import requests
from datetime import date, timedelta


# -------------------------------
# API
# -------------------------------
def get_coordinates(city_name):
    geo_url = (
        f"https://geocoding-api.open-meteo.com/v1/search?"
        f"name={city_name}&count=1&language=uk&format=json"
    )

    response = requests.get(geo_url)
    data = response.json()

    if "results" not in data:
        return None

    city = data["results"][0]
    return city["latitude"], city["longitude"], city["name"]


def get_weather(lat, lon, start_date, end_date):
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,weathercode"
        f"&timezone=auto"
        f"&start_date={start_date}&end_date={end_date}"
    )

    response = requests.get(weather_url)
    return response.json()


# -------------------------------
# Поради щодо одягу
# -------------------------------
def clothing_advice(min_temp, max_temp, weather_desc):
    avg_temp = (min_temp + max_temp) / 2
    advice = []

    if avg_temp >= 30:
        advice.append("☀️ Спекотно: футболка, шорти, головний убір.")
    elif avg_temp >= 22:
        advice.append("🌤️ Тепло: легкий одяг.")
    elif avg_temp >= 15:
        advice.append("🍂 Комфортно: кофта або вітровка.")
    elif avg_temp >= 8:
        advice.append("🧥 Прохолодно: куртка, джинси.")
    elif avg_temp >= 0:
        advice.append("❄️ Холодно: тепла куртка.")
    else:
        advice.append("🧣 Дуже холодно: зимовий одяг.")

    if "Дощ" in weather_desc or "Злива" in weather_desc or "мряка" in weather_desc.lower():
        advice.append("☔ Візьміть парасолю.")
    if "Сніг" in weather_desc:
        advice.append("🥾 Потрібне тепле взуття.")
    if "Гроза" in weather_desc:
        advice.append("⚡ Краще скоротити прогулянки.")

    return " ".join(advice)


# -------------------------------
# Коди погоди
# -------------------------------
weather_codes = {
    0: "Ясно",
    1: "Переважно ясно",
    2: "Мінлива хмарність",
    3: "Похмуро",
    45: "Туман",
    48: "Паморозь",
    51: "Легка мряка",
    53: "Мряка",
    55: "Сильна мряка",
    61: "Дощ",
    63: "Помірний дощ",
    65: "Сильний дощ",
    71: "Сніг",
    80: "Злива",
    95: "Гроза",
}


# -------------------------------
# Основна функція
# -------------------------------
def show_weather():
    city_name = city_entry.get()

    if not city_name or city_name.strip().lower() == "введіть місто...":
        messagebox.showwarning("Помилка", "Введіть назву міста.")
        return

    location = get_coordinates(city_name)

    if not location:
        messagebox.showerror("Помилка", "Місто не знайдено.")
        return

    latitude, longitude, found_city = location

    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    weather_data = get_weather(latitude, longitude, yesterday, tomorrow)

    result_text.delete(1.0, tk.END)

    result_text.insert(
        tk.END,
        f"🌍 Погода для {found_city}\n\n"
    )

    for i, day in enumerate(weather_data["daily"]["time"]):
        min_temp = weather_data["daily"]["temperature_2m_min"][i]
        max_temp = weather_data["daily"]["temperature_2m_max"][i]
        code = weather_data["daily"]["weathercode"][i]

        description = weather_codes.get(code, "Невідомо")

        if day == str(yesterday):
            label = "Вчора"
        elif day == str(today):
            label = "Сьогодні"
        elif day == str(tomorrow):
            label = "Завтра"
        else:
            label = day

        advice = clothing_advice(min_temp, max_temp, description)

        result_text.insert(
            tk.END,
            f"📅 {label} ({day})\n"
            f"🌡️ Мін: {min_temp}°C | Макс: {max_temp}°C\n"
            f"☁️ Стан: {description}\n"
            f"👕 Порада: {advice}\n"
            f"{'═'*50}\n"
        )


# -------------------------------
# Інтерфейс
# -------------------------------
root = tk.Tk()
root.title("☀️ Weather Style")
root.geometry("760x700")
root.configure(bg="#FDF6EC")

# Заголовок
title_label = tk.Label(
    root,
    text="☀️ Погода та стиль одягу",
    font=("Georgia", 22, "bold"),
    bg="#FDF6EC",
    fg="#9C5B2E"
)
title_label.pack(pady=20)

# Підзаголовок
subtitle = tk.Label(
    root,
    text="Дізнайся погоду та що краще вдягнути",
    font=("Arial", 12),
    bg="#FDF6EC",
    fg="#B07A4F"
)
subtitle.pack()

# Поле введення
city_entry = tk.Entry(
    root,
    font=("Arial", 14),
    width=30,
    justify="center",
    bg="#FFF3E0",
    fg="#5D4037",
    relief="flat"
)
city_entry.pack(pady=15, ipady=8)
city_entry.insert(0, "Введіть місто...")
city_entry.bind("<FocusIn>", lambda e: city_entry.delete(0, tk.END))

# Кнопка
search_button = tk.Button(
    root,
    text="Показати погоду",
    font=("Arial", 13, "bold"),
    bg="#E89B5B",
    fg="white",
    activebackground="#D9822B",
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=10,
    command=show_weather
)
search_button.pack(pady=10)

# Рамка
frame = tk.Frame(root, bg="#EED9C4", bd=0)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Вивід
result_text = tk.Text(
    frame,
    wrap=tk.WORD,
    font=("Arial", 12),
    bg="#FFF8F0",
    fg="#4E342E",
    relief="flat",
    padx=15,
    pady=15
)
result_text.pack(fill="both", expand=True)

root.mainloop()