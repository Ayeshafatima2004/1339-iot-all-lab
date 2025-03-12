import network
import socket
import time
from machine import Pin, SoftI2C
from neopixel import NeoPixel
import dht
from ssd1306 import SSD1306_I2C

# Init NeoPixel on Pin 48
pin = Pin(48, Pin.OUT)
neo = NeoPixel(pin, 1)

# Init DHT11 on Pin 4
dht_pin = Pin(4)
sensor = dht.DHT11(dht_pin)

# Init OLED via I2C (SCL=9, SDA=8)
i2c = SoftI2C(scl=Pin(9), sda=Pin(8))
oled = SSD1306_I2C(128, 64, i2c)

# Display a message on OLED
def display_message_on_oled(msg):
    oled.fill(0)
    max_chars_per_line = 16
    max_chars_total = 64
    msg = msg[:max_chars_total]
    words = msg.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += (" " if current_line else "") + word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    y = 0
    for line in lines[:4]:
        oled.text(line, 5, y)
        y += 16
    oled.show()

display_message_on_oled("I AM AYESHA")
print("I AM AYESHA")

# Initialize RGB and sensor values
r = g = b = 0
try:
    sensor.measure()
    temp = str(sensor.temperature())
    humidity = str(sensor.humidity())
    print("Temperature:", temp, "°C")
    print("Humidity:", humidity, "%")
except Exception as e:
    print("Sensor Error:", e)
    temp = "N/A"
    humidity = "N/A"

# Connect to Wi-Fi
SSID = "Tech"
PASS = "ayeshaaa"

sta = network.WLAN(network.STA_IF)
sta.active(True)
time.sleep(1)  # Add a small delay
sta.connect(SSID,PASS)


print("Connecting to Wi-Fi...")
for _ in range(10):
    if sta.isconnected():
        break
    time.sleep(1)

if sta.isconnected():
    print("Connected to Wi-Fi! IP:", sta.ifconfig()[0])
else:
    print("Failed to connect to Wi-Fi.")
    display_message_on_oled("Wi-Fi Failed")
    raise SystemExit()

# Setup Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="sherry-esp", password="12345678")
print("AP Mode IP:", ap.ifconfig()[0])

# Start socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 80))
s.listen(5)

# HTML page generator
def web_page(r=0, g=0, b=0, temp="N/A", humidity="N/A"):
    hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ESP32 RGB & OLED Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            text-align: center;
            background: {hex_color};
            transition: background 0.3s ease;
            margin: 0; padding: 0;
        }}
        .banner {{
            font-size: 22px;
            font-weight: bold;
            padding: 15px;
            color: white;
            background-color: #222;
            text-shadow: 0 0 10px #f0f, 0 0 20px #0ff, 0 0 30px #0ff;
            animation: glow 2s infinite alternate;
        }}
        @keyframes glow {{
            from {{
                text-shadow: 0 0 10px #f0f, 0 0 20px #0ff, 0 0 30px #0ff;
            }}
            to {{
                text-shadow: 0 0 20px #ff0, 0 0 30px #f0f, 0 0 40px #0ff;
            }}
        }}
        .container {{
            max-width: 420px;
            margin: auto;
            margin-top: 30px;
            padding: 25px;
            background: rgba(255,255,255,0.9);
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        p {{ font-size: 18px; color: #555; }}
        label {{ font-weight: bold; }}
        .slider {{ width: 60%; }}
        .color-preview {{
            width: 60px; height: 60px;
            margin: 10px auto;
            background-color: {hex_color};
            border-radius: 50%;
            border: 2px solid #888;
            transition: background-color 0.3s ease;
        }}
        input[type="number"] {{ width: 50px; }}
        input[type="text"] {{
            padding: 8px;
            width: 80%;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="banner">Presented by Ayesha Fatima</div>

    <div class="container">
        <h1>🌈 ESP32 RGB Controller</h1>
        <p>🌡️ Temperature: {temp}°C &nbsp;&nbsp; 💧 Humidity: {humidity}%</p>
        <div class="color-preview" id="colorCircle"></div>
        <label>🔴 Red:</label><br>
        <input class="slider" type="range" id="red" min="0" max="255" value="{r}" oninput="updateRGB('red')">
        <input type="number" id="redValue" min="0" max="255" value="{r}" oninput="syncRGB('red')"><br>
        <label>🟢 Green:</label><br>
        <input class="slider" type="range" id="green" min="0" max="255" value="{g}" oninput="updateRGB('green')">
        <input type="number" id="greenValue" min="0" max="255" value="{g}" oninput="syncRGB('green')"><br>
        <label>🔵 Blue:</label><br>
        <input class="slider" type="range" id="blue" min="0" max="255" value="{b}" oninput="updateRGB('blue')">
        <input type="number" id="blueValue" min="0" max="255" value="{b}" oninput="syncRGB('blue')"><br><br>

        <h2>📺 OLED Display</h2>
        <input type="text" id="msg" placeholder="Enter message (Max 64 chars)" maxlength="64" oninput="sendMessage()">
    </div>

    <script>
        function updateRGB(color) {{
            let value = document.getElementById(color).value;
            document.getElementById(color + "Value").value = value;
            syncAll();
        }}
        function syncRGB(color) {{
            let value = parseInt(document.getElementById(color + "Value").value);
            value = Math.min(255, Math.max(0, value));
            document.getElementById(color).value = value;
            syncAll();
        }}
        function syncAll() {{
            let r = document.getElementById("red").value;
            let g = document.getElementById("green").value;
            let b = document.getElementById("blue").value;
            fetch("/?r=" + r + "&g=" + g + "&b=" + b);
            let colorHex = "#" + [r,g,b].map(x => ("0" + parseInt(x).toString(16)).slice(-2)).join('');
            document.getElementById("colorCircle").style.backgroundColor = colorHex;
            document.body.style.backgroundColor = colorHex;
        }}
        function sendMessage() {{
            let msg = document.getElementById("msg").value;
            fetch("/?msg=" + encodeURIComponent(msg));
        }}
    </script>
</body>
</html>"""
    return html

# Web Server Loop
while True:
    conn, addr = s.accept()
    print("Connection from:", addr)
    request = conn.recv(1024).decode()
    print("Request:", request)

    if "/?r=" in request and "&g=" in request and "&b=" in request:
        try:
            parts = request.split("/?")[1].split(" ")[0]
            params = {kv.split("=")[0]: kv.split("=")[1] for kv in parts.split("&")}
            r = min(255, max(0, int(params["r"])))
            g = min(255, max(0, int(params["g"])))
            b = min(255, max(0, int(params["b"])))
            neo[0] = (r, g, b)
            neo.write()
        except Exception as e:
            print("RGB Error:", e)

    elif "/?msg=" in request:
        try:
            msg = request.split("/?msg=")[1].split(" ")[0]
            msg = msg.replace("%20", " ")
            display_message_on_oled(msg)
        except Exception as e:
            print("OLED Msg Error:", e)

    response = web_page(r, g, b, temp, humidity)
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response)
    conn.close()



