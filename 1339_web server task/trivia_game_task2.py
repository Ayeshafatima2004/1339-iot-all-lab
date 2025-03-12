import network
import wifi_manager
import socket
import time
from machine import Pin, SoftI2C
from neopixel import NeoPixel
import dht
from ssd1306 import SSD1306_I2C
import urandom

dht_pin = Pin(4)	
sensor = dht.DHT11(dht_pin)

i2c = SoftI2C(scl=Pin(9), sda=Pin(8))
oled = SSD1306_I2C(128, 64, i2c)

rgb_pin = Pin(48, Pin.OUT)
rgb_led = NeoPixel(rgb_pin, 1)

SSID = "Tech"
PASS = "ayesha23"

trivia_data = [
    {"category": "Science", "word": "Einstein", "hints": ["Relativity", "Physicist", "E=mc^2", "Nobel Prize", "Theory of Relativity"]},
    {"category": "Geography", "word": "Nile", "hints": ["Longest river", "Africa", "Egypt", "Flows north", "Cairo"]},
    {"category": "History", "word": "Napoleon", "hints": ["French", "Emperor", "Waterloo", "Short", "Corsica"]},
    {"category": "Technology", "word": "Internet", "hints": ["WWW", "Online", "Browsing", "Data", "Google"]},
    {"category": "Math", "word": "Pythagoras", "hints": ["Triangle", "Theorem", "Greek", "Right angle", "a^2 + b^2 = c^2"]},
    {"category": "Sports", "word": "Messi", "hints": ["Football", "Argentina", "Barcelona", "PSG", "GOAT"]},
    {"category": "Literature", "word": "Shakespeare", "hints": ["Playwright", "Hamlet", "Romeo", "Macbeth", "Elizabethan"]},
    {"category": "Biology", "word": "Cell", "hints": ["Basic unit", "Life", "Organelles", "Microscope", "Membrane"]},
    {"category": "Physics", "word": "Gravity", "hints": ["Apple", "Force", "Earth", "Newton", "Pull"]},
    {"category": "Movies", "word": "Titanic", "hints": ["Ship", "Iceberg", "Jack", "Rose", "Sank"]},
    {"category": "Programming", "word": "Python", "hints": ["Snake", "Language", "Indentation", "Easy", "Popular"]},
    {"category": "Invention", "word": "Telephone", "hints": ["Communication", "Alexander Bell", "Call", "Wires", "Device"]},
    {"category": "Computer", "word": "Keyboard", "hints": ["Typing", "QWERTY", "Keys", "Input", "Device"]},
    {"category": "Space", "word": "Moon", "hints": ["Crater", "Orbit", "Night", "NASA", "Apollo"]},
    {"category": "Animals", "word": "Elephant", "hints": ["Large", "Trunk", "Tusks", "Grey", "Herbivore"]},
    {"category": "Music", "word": "Beethoven", "hints": ["Composer", "Deaf", "Symphony", "Classical", "Piano"]},
    {"category": "Countries", "word": "Japan", "hints": ["Sushi", "Samurai", "Tokyo", "Anime", "Island"]},
    {"category": "Games", "word": "Chess", "hints": ["Board", "Checkmate", "King", "Queen", "Knight"]},
    {"category": "Art", "word": "Mona Lisa", "hints": ["Leonardo", "Painting", "Smile", "Louvre", "Famous"]},
    {"category": "Plants", "word": "Rose", "hints": ["Red", "Thorn", "Flower", "Love", "Petals"]},
    {"category": "Ocean", "word": "Pacific", "hints": ["Largest", "Ocean", "Asia", "Calm", "Water"]},
    {"category": "Insects", "word": "Bee", "hints": ["Honey", "Buzz", "Yellow", "Hive", "Pollinate"]},
    {"category": "Transport", "word": "Bicycle", "hints": ["Pedal", "Wheels", "Helmet", "Chain", "Ride"]},
    {"category": "Fruits", "word": "Banana", "hints": ["Yellow", "Monkey", "Peel", "Fruit", "Sweet"]},
    {"category": "Chemistry", "word": "Oxygen", "hints": ["Gas", "Breath", "Air", "O2", "Life"]},
]

wifi_manager.connect_to_wifi(SSID, PASS)

def display_message_on_oled(msg):
    oled.fill(0)
    y = 0
    for line in msg.split("\n")[:4]:
        oled.text(line, 0, y)
        y += 16
    oled.show()

def flash_rgb(color):
    rgb_led[0] = color
    rgb_led.write()
    time.sleep(0.5)
    rgb_led[0] = (0, 0, 0)
    rgb_led.write()

def initialize_game():
    question = urandom.choice(trivia_data)
    return {
        "category": question["category"],
        "word": question["word"],
        "hints": question["hints"],
        "hints_given": 0,
        "guesses": 0,
        "status": "playing"
    }

def determine_intelligence_score(attempts):
    if attempts == 1:
        return "You are more intelligent than 90% of people! 🎉"
    elif attempts <= 3:
        return "Great job! You performed better than 70% of people!"
    else:
        return "Nice try! Keep improving and challenge yourself!"

def web_page(game_state):
    hint = game_state["hints"][game_state["hints_given"]] if game_state["hints_given"] < len(game_state["hints"]) else "No more hints!"
    status_message = ""
    bg_color = "#00FFFF"

    if game_state["status"] == "won":
        status_message = f"<div class='result win'>🎉 Correct! The answer was <b>{game_state['word']}</b><br>{determine_intelligence_score(game_state['guesses'])}</div>"
        bg_color = "#4CAF50"
        display_message_on_oled("You Won!\nAnswer: " + game_state['word'])
    elif game_state["status"] == "lost":
        status_message = f"<div class='result lose'>❌ Game Over!<br>The correct answer was <b>{game_state['word']}</b></div>"
        bg_color = "#FF0000"
        display_message_on_oled("You Lost!\nAnswer: " + game_state['word'])
    else:
        red_intensity = min(255, game_state["guesses"] * 50)
        bg_color = f"rgb({red_intensity}, 255, 255)"
        display_message_on_oled(f"Hint: {hint}")

    html = f"""\
HTTP/1.1 200 OK

<!DOCTYPE html>
<html><head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trivia Game</title>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; background-color: {bg_color}; margin: 0; padding: 20px; text-align: center; transition: background-color 0.8s ease; }}
    h1 {{ font-size: 2.5em; color: #222; }}
    p, .result {{ font-size: 1.3em; margin: 10px 0; }}
    input[type="text"] {{ padding: 12px; font-size: 1em; width: 80%; max-width: 300px; border: 2px solid #333; border-radius: 8px; outline: none; }}
    button {{ padding: 12px 24px; font-size: 1em; border: none; border-radius: 8px; background: linear-gradient(45deg, #008CBA, #00bcd4); color: white; cursor: pointer; }}
    button:hover {{ transform: scale(1.05); background: linear-gradient(45deg, #007BA7, #00a2b8); }}
    .result {{ margin-top: 20px; padding: 15px; font-weight: bold; border-radius: 12px; }}
    .win {{ background-color: #d4edda; color: #155724; }}
    .lose {{ background-color: #f8d7da; color: #721c24; }}
  </style>
</head>
<body>
 <h1>Trivia: {game_state['category']}</h1>
<p><b>Hint:</b> {hint}</p>
<p>Attempts left: {5 - game_state["guesses"]}</p>
<form action="/guess">
  <input type="text" name="answer" placeholder="Enter your guess" required /><br><br>
  <button type="submit">Submit</button>
</form>

  {status_message}
  <br><br>
  <a href="/restart"><button>Restart Game</button></a>
</body></html>"""
    return html

def handle_client(conn, addr, game_state):
    request = conn.recv(1024).decode()
    if "GET / " in request:
        response = web_page(game_state)
    elif "GET /guess?answer=" in request:
        answer = request.split("answer=")[1].split(" ")[0].replace("%20", " ").lower()
        correct = answer == game_state["word"].lower()
        if correct:
            game_state["status"] = "won"
            flash_rgb((0, 255, 0))  # Green for correct
        else:
            game_state["guesses"] += 1
            flash_rgb((255, 0, 0))  # Red for wrong
            if game_state["guesses"] >= 5:
                game_state["status"] = "lost"
            else:
                game_state["hints_given"] = min(game_state["hints_given"] + 1, len(game_state["hints"]) - 1)
        response = web_page(game_state)
    elif "GET /restart" in request:
        game_state.clear()
        game_state.update(initialize_game())
        response = web_page(game_state)
    else:
        response = "HTTP/1.1 404 Not Found\n\nPage Not Found"
    conn.send(response)
    conn.close()

game_state = initialize_game()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
s.bind(addr)
s.listen(1)

print("Trivia Game server running...")

while True:
    conn, addr = s.accept()
    handle_client(conn, addr, game_state)
