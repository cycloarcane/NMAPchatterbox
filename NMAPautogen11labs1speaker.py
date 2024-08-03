import os
import subprocess
import threading
import openai
import autogen
import requests
import pygame
import time
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Ensure the OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
openai.api_key = api_key

# Initialize Pygame mixer for audio playback
pygame.mixer.init()

# Function to generate and play audio
def generate_and_play_audio(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {
        "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        audio_file = f"output_{voice_id}.mp3"
        with open(audio_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Audio file size: {os.path.getsize(audio_file)} bytes")
        if os.path.getsize(audio_file) == 0:
            print("Error: Generated audio file is empty")
            return

        print(f"Playing audio file: {audio_file}")
        # Use pygame to play the audio
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print("Audio playback finished")
    except requests.exceptions.RequestException as e:
        print(f"Error in API request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Function to run nmap scan
def run_nmap_scan(target):
    command = f"nmap {target} -sV -sC"
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        return result.stdout
    except subprocess.TimeoutExpired:
        return "nmap command timed out"
    except Exception as e:
        return f"nmap command failed with exception: {e}"

# Function to initiate group chat using autogen
def initiate_group_chat(scan_results):
    config_list = [
        {
            "model": "gpt-4o-mini",
            "api_key": api_key,
            "tags": ["gpt-4o-mini"]
        }
    ]

    llm_config = {"config_list": config_list, "cache_seed": 42}

    agents = [
        autogen.AssistantAgent(
            name="RedTeamLead",
            system_message="You are a Red Team Lead. Focus on offensive security and exploitation strategies.",
            llm_config=llm_config,
        ),
        autogen.AssistantAgent(
            name="BlueTeamLead",
            system_message="You are a Blue Team Lead. Focus on defensive security and mitigation strategies.",
            llm_config=llm_config,
        ),
        autogen.AssistantAgent(
            name="ThreatAnalyst",
            system_message="You are a Threat Analyst. Analyze potential threats and vulnerabilities.",
            llm_config=llm_config,
        ),
        autogen.AssistantAgent(
            name="IncidentResponder",
            system_message="You are an Incident Responder. Provide steps for incident response and remediation.",
            llm_config=llm_config,
        ),
    ]

    voice_id = os.getenv("ELEVENLABS_VOICE_ID_1")  # Use the same voice ID for all agents

    if not voice_id:
        print("Voice ID is required. Exiting.")
        return

    groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=10)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    context = f"""
    Nmap Scan Results:
    {scan_results}
    """

    def capture_and_speak(self, messages=None, sender=None, config=None):
        if messages and len(messages) > 0:
            last_message = messages[-1]["content"]
            print(f"{sender.name}: {last_message}")

            def play_audio():
                try:
                    generate_and_play_audio(last_message, voice_id)
                except Exception as e:
                    print(f"Error generating or playing audio: {e}")
                finally:
                    audio_event.set()

            audio_thread = threading.Thread(target=play_audio)
            audio_thread.start()

            # Wait for audio to finish playing before continuing
            audio_event.wait()
            audio_event.clear()

        return False, None  # Return False to allow the original reply to proceed

    audio_event = threading.Event()

    # Register the capture and speak function for all agents
    for agent in groupchat.agents:
        agent.register_reply([autogen.Agent, None], capture_and_speak, position=0)

    agents[0].initiate_chat(manager, message=f"Discuss the following context and strategize the next steps:\n{context}")
    manager.run_chat()

def main():
    target = input("Please enter the target IP or domain for nmap scan: ").strip()

    if not target:
        print("Target is required. Exiting.")
        return

    scan_result = run_nmap_scan(target)
    print("\nNmap scan results:")
    print(scan_result)

    initiate_group_chat(scan_result)

if __name__ == "__main__":
    main()
