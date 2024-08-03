import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import openai
import autogen
import sys


# Ensure the OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

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
            "model": "gpt-4o",
            "api_key": api_key,
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

# GUI setup
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

def handle_request():
    def run_request():
        target = input_text.get("1.0", tk.END).strip()
        if target:
            scan_result = run_nmap_scan(target)
            output_text.insert(tk.END, f"\nNmap scan results:\n{scan_result}\n")
            initiate_group_chat(scan_result)

    request_thread = threading.Thread(target=run_request)
    request_thread.start()

root = tk.Tk()
root.title("NMAP Chatterbox")
root.configure(bg="pink")

label_font = ("Helvetica", 10, "bold")

input_label = tk.Label(root, text="Enter the target IP or domain for nmap scan:", fg="black", bg="pink", font=label_font)
input_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

input_frame = tk.Frame(root, bg="pink")
input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
input_frame.columnconfigure(0, weight=1)

input_text = tk.Text(input_frame, height=2, width=60, bg="white", fg="black", highlightbackground="pink", highlightcolor="pink", highlightthickness=1, insertbackground="black", wrap=tk.WORD)
input_text.grid(row=0, column=0, sticky="ew", padx=(0, 10))

input_scrollbar = tk.Scrollbar(input_frame, command=input_text.yview, bg="pink")
input_scrollbar.grid(row=0, column=1, sticky="ns")
input_text.config(yscrollcommand=input_scrollbar.set)

start_button = tk.Button(root, text="Start", command=handle_request, fg="white", bg="black")
start_button.grid(row=2, column=0, sticky="w", padx=10, pady=(5, 0))

output_frame = tk.Frame(root, bg="pink")
output_frame.grid(row=3, column=0, columnspan=1, sticky="nsew", padx=10, pady=(10, 10))
output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(0, weight=1)

scrollbar = tk.Scrollbar(output_frame, bg="pink")
scrollbar.grid(row=0, column=1, sticky="ns")

output_text = tk.Text(output_frame, wrap=tk.WORD, fg="black", bg="white", yscrollcommand=scrollbar.set, insertbackground="black")
output_text.grid(row=0, column=0, sticky="nsew")

scrollbar.config(command=output_text.yview)

sys.stdout = TextRedirector(output_text)
sys.stderr = TextRedirector(output_text)

root.rowconfigure(3, weight=1)
root.columnconfigure(0, weight=1)

root.mainloop()
