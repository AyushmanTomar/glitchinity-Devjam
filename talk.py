import pyttsx3

def text_to_speech(text):
    # Initialize the TTS engine
    engine = pyttsx3.init()

    # Set properties (optional)
    engine.setProperty('rate', 150)  # Speed of speech (default is 200)
    engine.setProperty('volume', 1)# Volume level (0.0 to 1.0)
    voices=engine.getProperty("voices")
    engine.setProperty('voice', voices[0].id)
    # Speak the provided text
    engine.say(text)

    # Process the speech
    engine.runAndWait()

# Example usage
# text = "Hello, this is a basic text-to-speech implementation."
# text_to_speech(text)