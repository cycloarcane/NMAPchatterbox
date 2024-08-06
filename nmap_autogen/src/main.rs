use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::env;
use std::error::Error;
use std::process::Command;

#[derive(Serialize)]
struct Message {
    role: String,
    content: String,
}

#[derive(Serialize)]
struct OpenAIRequest {
    model: String,
    messages: Vec<Message>,
    max_tokens: u32,
}

#[derive(Deserialize)]
struct Choice {
    message: MessageContent,
}

#[derive(Deserialize)]
struct MessageContent {
    content: String,
}

#[derive(Deserialize)]
struct OpenAIResponse {
    choices: Vec<Choice>,
}

async fn get_openai_response(prompt: &str, api_key: &str) -> Result<String, Box<dyn Error>> {
    let client = Client::new();
    let request = OpenAIRequest {
        model: "gpt-3.5-turbo".to_string(),
        messages: vec![
            Message {
                role: "user".to_string(),
                content: prompt.to_string(),
            },
        ],
        max_tokens: 150,
    };

    let response = client
        .post("https://api.openai.com/v1/chat/completions")
        .header("Authorization", format!("Bearer {}", api_key))
        .json(&request)
        .send()
        .await?;

    if response.status().is_success() {
        let openai_response = response.json::<OpenAIResponse>().await?;
        let choice = &openai_response.choices[0].message;
        Ok(choice.content.clone())
    } else {
        let error_text = response.text().await?;
        Err(Box::new(std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("API Error: {}", error_text),
        )))
    }
}

fn cuddles_art() {
    println!(
        r#"
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
    "#
    );
}

fn run_nmap_scan(target: &str) -> String {
    let output = Command::new("nmap")
        .arg(target)
        .output()
        .expect("failed to execute nmap");

    if output.status.success() {
        String::from_utf8_lossy(&output.stdout).to_string()
    } else {
        format!(
            "nmap command failed with error: {}",
            String::from_utf8_lossy(&output.stderr)
        )
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    cuddles_art();

    let mut target = String::new();
    println!("Please enter the target IP or domain for nmap scan: ");
    std::io::stdin().read_line(&mut target)?;
    let target = target.trim();

    if target.is_empty() {
        println!("Target is required. Exiting.");
        return Ok(());
    }

    let scan_result = run_nmap_scan(target);
    println!("\nNmap scan results:\n{}", scan_result);

    let api_key = env::var("OPENAI_API_KEY").expect("OPENAI_API_KEY must be set");
    let prompt = format!("Nmap scan results:\n{}", scan_result);

    match get_openai_response(&prompt, &api_key).await {
        Ok(response) => println!("OpenAI response: {}", response),
        Err(err) => eprintln!("Error getting OpenAI response: {}", err),
    }

    Ok(())
}
