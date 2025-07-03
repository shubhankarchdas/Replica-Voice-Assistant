from bs4 import BeautifulSoup
import geocoder
import pygame
import speech_recognition as sr
import webbrowser
import os
import musicLibrary
import requests
from gtts import gTTS
import datetime
import random
import wikipedia
import time

# Initialize pygame mixer once
pygame.mixer.init()

# API keys
NEWS_API_KEY = "<your_news_api_key>"  # Get your API key from https://newsapi.org/
DEEPAI_API_KEY = "<your_deepai_api_key>"  # Get free API key from https://deepai.org/

def speak(text):
    """Convert text to speech using gTTS and play with pygame"""
    tts = gTTS(text=text, lang='en')
    tts.save('temp.mp3')
    
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()
    
    # Wait for audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3")

def aiProcess(command):
    """Use free DeepAI API as alternative to OpenAI"""
    try:
        response = requests.post(
            "https://api.deepai.org/api/text-generator",
            data={'text': command},
            headers={'api-key': DEEPAI_API_KEY}
        )
        return response.json()['output']
    except Exception as e:
        print(f"AI Error: {e}")
        return "I'm having trouble connecting to the AI service."

def get_news():
    """Fetch top 5 news headlines"""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        news_data = response.json()
        
        if news_data['status'] == 'ok' and news_data['totalResults'] > 0:
            headlines = [article['title'] for article in news_data['articles'][:5]]
            return "Here are the top news headlines: " + ". ".join(headlines)
        return "Sorry, I couldn't fetch news at the moment."
    except Exception as e:
        print(f"News Error: {e}")
        return "News service unavailable."

def get_weather(city=None):
    """Get weather information without API keys"""
    try:
        if not city:
            # Automatically detect location based on IP
            g = geocoder.ip('me')
            city = g.city
        
        # Use free weather API without key
        response = requests.get(f"https://wttr.in/{city}?format=%C+%t+%w")
        
        if response.status_code == 200:
            weather_data = response.text.split()
            condition = weather_data[0]
            temp = weather_data[1]
            wind = weather_data[2]
            
            return f"The weather in {city} is {condition} with temperature {temp} and wind {wind}"
        
        # Fallback to web scraping
        return get_weather_scraping(city)
    except Exception as e:
        print(f"Weather Error: {e}")
        return "I couldn't retrieve weather information."

def get_weather_scraping(city):
    """Fallback weather using web scraping"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        city = city.replace(" ", "+")
        res = requests.get(f'https://www.google.com/search?q=weather+in+{city}', headers=headers)
        
        soup = BeautifulSoup(res.text, 'html.parser')
        location = soup.select('#wob_loc')[0].getText().strip()
        time = soup.select('#wob_dts')[0].getText().strip()
        info = soup.select('#wob_dc')[0].getText().strip()
        weather = soup.select('#wob_tm')[0].getText().strip()
        
        return f"In {location}, it's currently {weather}°C and {info.lower()}"
    except:
        return "Weather information not available."


def tell_joke():
    """Tell a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What did one ocean say to the other ocean? Nothing, they just waved!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "How do you organize a space party? You planet!",
        "Why don't skeletons fight each other? They don't have the guts!"
    ]
    return random.choice(jokes)

def processCommand(command):
    """Process voice commands"""
    cmd = command.lower()
    
    # Website commands
    site_commands = {
        "open google": "https://google.com",
        "open facebook": "https://facebook.com",
        "open youtube": "https://youtube.com",
        "open linkedin": "https://linkedin.com",
        "open github": "https://github.com"
    }
    
    for key, url in site_commands.items():
        if key in cmd:
            webbrowser.open(url)
            return
    
    # Music commands
    if cmd.startswith("play "):
        song = cmd.split("play ", 1)[1]
        if song in musicLibrary.music:
            webbrowser.open(musicLibrary.music[song])
            return f"Playing {song}"
    
    # Special commands
    if "news" in cmd:
        return get_news()
    
    if "weather" in cmd:
        if " in " in cmd:
            city = cmd.split(" in ", 1)[1]
            return get_weather(city)
        return get_weather()
    
    if "time" in cmd:
        return f"It's {datetime.datetime.now().strftime('%I:%M %p')}"
    
    if "joke" in cmd:
        return tell_joke()
    
    if "thank you" in cmd:
        return "You're welcome!"
    
    if "who are you" in cmd:
        return "I'm Replica, your virtual assistant!"
    
    # Wikipedia search
    if "wikipedia" in cmd or "who is" in cmd or "what is" in cmd:
        try:
            search_term = cmd.split(" ", 2)[2] if "search" in cmd else cmd.split(" ", 1)[1]
            summary = wikipedia.summary(search_term, sentences=2)
            return summary
        except:
            return "I couldn't find information on that topic."
    
    # Default AI processing
    return aiProcess(command)

def listen_for_command():
    """Listen for voice commands"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = r.listen(source, timeout=5, phrase_time_limit=8)
    
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print(f"Recognition Error: {e}")
        return ""

if __name__ == "__main__":
    speak("Initializing Replica... Ready to assist you!")
    
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                audio = sr.Recognizer().listen(source, timeout=3, phrase_time_limit=2)
                
            wake_word = sr.Recognizer().recognize_google(audio).lower()
            if wake_word == "replica":
                speak("Yes? How can I help you?")
                command = listen_for_command()
                
                if command:
                    print(f"Command: {command}")
                    response = processCommand(command)
                    if response:
                        speak(response)
                else:
                    speak("I didn't catch that. Please try again.")
        
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"Main Error: {e}")
            time.sleep(1)
           
