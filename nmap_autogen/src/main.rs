use dotenv::dotenv;
use std::env;
use std::process::Command;
use tokio::task;
use reqwest::Client;
use serde::{Deserialize, Serialize};

// Function to get the OpenAI API key from environment variables
fn get_api_key() -> String {
    dotenv().ok();
    env::var("OPENAI_API_KEY").expect("OPENAI_API_KEY must be set")
}

// Function to run nmap scan
async fn run_nmap_scan(target: &str) -> Result<String, Box<dyn std::error::Error>> {
    let target = target.to_string();
    let output = task::spawn_blocking(move || {
        Command::new("nmap")
            .arg(target)
            .arg("-sV")
            .arg("-sC")
            .output()
    })
    .await??;

    if !output.status.success() {
        return Err(format!(
            "Nmap command failed with exit code: {}",
            output.status
        ).into());
    }

    let stdout = String::from_utf8(output.stdout)?;
    Ok(stdout)
}

// Structs for OpenAI API request and response
#[derive(Serialize)]
struct OpenAIRequest {
    model: String,
    prompt: String,
    max_tokens: u32,
}

#[derive(Deserialize)]
struct OpenAIResponse {
    choices: Vec<Choice>,
}

#[derive(Deserialize)]
struct Choice {
    text: String,
}

// Function to get response from OpenAI API
async fn get_openai_response(api_key: &str, prompt: &str) -> Result<String, Box<dyn std::error::Error>> {
    let client = Client::new();
    let request = OpenAIRequest {
        model: "gpt-4o-mini".into(),
        prompt: prompt.into(),
        max_tokens: 150,
    };

    let response = client
        .post("https://api.openai.com/v1/completions")
        .header("Authorization", format!("Bearer {}", api_key))
        .json(&request)
        .send()
        .await?
        .json::<OpenAIResponse>()
        .await?;

    Ok(response.choices[0].text.clone())
}

// Main function
#[tokio::main]
async fn main() {
    // Print ASCII art (can be replaced with a function if needed)
    println!("
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
    ");

    // Get the target IP or domain
    let mut target = String::new();
    println!("Please enter the target IP or domain for nmap scan: ");
    std::io::stdin().read_line(&mut target).expect("Failed to read input");
    let target = target.trim();

    if target.is_empty() {
        println!("Target is required. Exiting.");
        return;
    }

    // Run the Nmap scan
    match run_nmap_scan(target).await {
        Ok(scan_result) => {
            println!("\nNmap scan results:\n{}", scan_result);

            // Initiate group chat with scan results (placeholder for actual implementation)
            let api_key = get_api_key();
            let context = format!("Nmap Scan Results:\n{}", scan_result);
            match get_openai_response(&api_key, &context).await {
                Ok(response) => println!("OpenAI response: {}", response),
                Err(e) => eprintln!("Error getting OpenAI response: {}", e),
            }
        }
        Err(e) => eprintln!("Error running nmap scan: {}", e),
    }
}
