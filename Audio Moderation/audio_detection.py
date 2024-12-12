import speech_recognition as sr
from pydub import AudioSegment
import numpy as np

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(wav_file_path, format="wav")

# Function to create a beep sound
def create_beep(duration_ms=500, frequency=1000):
    # Generate a sine wave
    sample_rate = 44100  # Sample rate in Hz
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * (duration_ms / 1000)), False)  # Time array
    sine_wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # Generate sine wave
    sine_wave = (sine_wave * 32767).astype(np.int16)  # Convert to 16-bit PCM format

    # Create an AudioSegment from the sine wave
    beep_sound = AudioSegment(
        sine_wave.tobytes(), 
        frame_rate=sample_rate,
        sample_width=2,  # 2 bytes for 16-bit audio
        channels=1  # Mono audio
    )
    return beep_sound

# Function to replace a specific word in the audio with a beep sound
def replace_word_with_beep(original_audio_path, word_to_replace):
    # Convert MP3 to WAV
    wav_audio_path = "temp_audio.wav"
    convert_mp3_to_wav(original_audio_path, wav_audio_path)

    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(wav_audio_path)

    # Transcribe audio
    with sr.AudioFile(wav_audio_path) as source:
        audio_data = recognizer.record(source)
        # Get transcription
        word_timings = recognizer.recognize_google(audio_data, show_all=True)

    # Print the entire transcription result for debugging
    print("Transcription Result:", word_timings)

    # Check if there are alternatives and if they contain transcripts
    if word_timings and 'alternative' in word_timings and len(word_timings['alternative']) > 0:
        full_transcript = word_timings['alternative'][0]['transcript']
        
        # Check if the word to replace is in the transcript
        if word_to_replace in full_transcript:
            # Create a beep sound
            beep_duration_ms = 500  # Duration of the beep sound
            beep_sound = create_beep(duration_ms=beep_duration_ms)

            # Replace the word in the audio
            start_index = full_transcript.index(word_to_replace)
            end_index = start_index + len(word_to_replace)

            # Calculate the timing of the beep
            beep_start_time = (start_index / len(full_transcript)) * len(audio) + 1000  # Add 1000 ms (1 second)
            beep_end_time = beep_start_time + beep_duration_ms

            # Create the modified audio
            modified_audio = audio[:int(beep_start_time)] + beep_sound + audio[int(beep_end_time):]

            # Save the modified audio
            modified_audio.export("modified_audio.mp3", format="mp3")
            print("Modified audio saved as 'modified_audio.mp3'.")
        else:
            print(f"The word '{word_to_replace}' was not found in the transcription.")
    else:
        print("No transcription was found.")

# Example usage
replace_word_with_beep("before_detection.mp3", "delete")
