import os
import subprocess
import time
import threading
import openai
import autogen

# Ensure the OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize the OpenAI client with the custom API endpoint
try:
    openai.api_key = api_key
except Exception as e:
    raise ConnectionError(f"Failed to initialize OpenAI client: {e}")

# ASCII Art Function
def cuddles_art():
    art = """

 ▄████▄   ██░ ██  ▄▄▄     ▄▄▄█████▓▄▄▄█████▓▓█████  ██▀███      ▄▄▄▄    ▒█████  ▒██   ██▒   
▒██▀ ▀█  ▓██░ ██▒▒████▄   ▓  ██▒ ▓▒▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒   ▓█████▄ ▒██▒  ██▒▒▒ █ █ ▒░   
▒▓█    ▄ ▒██▀▀██░▒██  ▀█▄ ▒ ▓██░ ▒░▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒   ▒██▒ ▄██▒██░  ██▒░░  █   ░   
▒▓▓▄ ▄██▒░▓█ ░██ ░██▄▄▄▄██░ ▓██▓ ░ ░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄     ▒██░█▀  ▒██   ██░ ░ █ █ ▒    
▒ ▓███▀ ░░▓█▒░██▓ ▓█   ▓██▒ ▒██▒ ░   ▒██▒ ░ ░▒████▒░██▓ ▒██▒   ░▓█  ▀█▓░ ████▓▒░▒██▒ ▒██▒   
░ ░▒ ▒  ░ ▒ ░░▒░▒ ▒▒   ▓▒█░ ▒ ░░     ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░   ░▒▓███▀▒░ ▒░▒░▒░ ▒▒ ░ ░▓ ░   
  ░  ▒    ▒ ░▒░ ░  ▒   ▒▒ ░   ░        ░     ░ ░  ░  ░▒ ░ ▒░   ▒░▒   ░   ░ ▒ ▒░ ░░   ░▒ ░   
░         ░  ░░ ░  ░   ▒    ░        ░         ░     ░░   ░     ░    ░ ░ ░ ░ ▒   ░    ░     
░ ░       ░  ░  ░      ░  ░                    ░  ░   ░         ░          ░ ░   ░    ░     
░                                                                    ░                         

"""
    return art

# Function to run nmap scan
def run_nmap_scan(target):
    command = f"nmap {target} -sV -sC"
    try:
        print("\nRunning nmap command:")
        print(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        print("\nnmap command stdout:")
        print(result.stdout)
        print("\nnmap command stderr:")
        print(result.stderr)
        if result.returncode != 0:
            print(f"nmap command failed with return code {result.returncode}")
        return result.stdout
    except subprocess.TimeoutExpired:
        print("nmap command timed out")
        return ""
    except Exception as e:
        print(f"nmap command failed with exception: {e}")
        return ""

# Function to initiate group chat using autogen
def initiate_group_chat(scan_results):
    config_list = [
        {
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "tags": ["gpt-4o"]
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

    groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=10)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    context = f"""
    Nmap Scan Results:
    {scan_results}
    """

    agents[0].initiate_chat(
        manager, message=f"Discuss the following context and strategize the next steps:\n{context}"
    )
    manager.run_chat()

# Main function
def main():
    print(cuddles_art())
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
