class VoiceRecognition:
    def __init__(self):
        import speech_recognition as sr
        self.recognizer = sr.Recognizer()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            return audio

    def recognize(self, audio):
        try:
            command = self.recognizer.recognize_google(audio, language="ro-RO")
            print(f"Recognized command: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

    def process_command(self):
        audio = self.listen()
        command = self.recognize(audio)
        return command