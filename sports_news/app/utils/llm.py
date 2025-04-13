from langchain_ollama.llms import OllamaLLM
from openai import OpenAI
from app.utils.prompts import get_prompt
import psutil
import requests
import time
import os

OLLAMA_MODEL = "mistral"
LLAMA_API_MODEL = "llama3-70b"

def send_request(title: str, subtitle: str = "", body: str = "", highlight: bool = False):
    print(f"=== LLM REQUEST DEBUG ===")
    print(f"Time: {time.ctime()}")
    
    # Check available memory before proceeding
    available_mem_gb = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    print(f"Available memory: {available_mem_gb:.2f} GB")
    
    if available_mem_gb < 6.0:  # Require at least 6GB to be safe
        print(f"WARNING: Not enough memory available ({available_mem_gb:.2f} GB)")
        print("Falling back to direct method...")
        try:
            result = send_api_request(title, subtitle, highlight)
            if not result:
                raise Exception("API request failed")
            else:
                return result
        except:
            return send_request_direct(title, subtitle, highlight)
    
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle[:50]}...")
    print(f"Highlight: {highlight}")
    
    try:
        # Create the Ollama LLM instance
        print("Creating OllamaLLM instance...")
        llm = OllamaLLM(
            model=OLLAMA_MODEL, 
            base_url="http://localhost:11434",
            temperature=0.3,
            max_tokens=250,
            request_timeout=600.0  # 10 minutes timeout
        )
        
        # Define prompt template
        print("Getting prompt template...")
        prompt = get_prompt(title, subtitle, highlight)
        print(f"Prompt template ready (length: {len(str(prompt))})")
        
        # Use the modern pipe syntax
        print("Creating chain...")
        chain = prompt | llm
        
        # Run the chain with the input values
        print(f"Invoking chain at {time.ctime()}...")
        result = chain.invoke({"title": title, "subtitle": subtitle})
        print(f"Chain response received at {time.ctime()}")
        
        # Post-process
        clean_result = result.strip()
        print(f"Result cleaned, length: {len(clean_result)}")
        
        # If result is too long, truncate to 200 characters
        if len(clean_result) > 200:
            clean_result = clean_result[:197] + "..."
            print("Result truncated to 200 chars")
            
        print("=== LLM REQUEST COMPLETE ===")
        return clean_result
    except Exception as e:
        print(f"=== LLM REQUEST FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        print("=== END ERROR ===")
        return None
    
def send_api_request(title: str, subtitle: str, highlight: bool = False):
    print(f"=== API REQUEST DEBUG ===")
    print(f"Time: {time.ctime()}")
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle[:50]}...")
    print(f"Highlight: {highlight}")

    # Check if API token is available
    api_token = os.getenv('LLAMA_API_TOKEN')
    if not api_token:
        print("WARNING: LLAMA_API_TOKEN not found in environment variables")
        return None

    requirements = (
        " - MUST BE NO MORE THAN 250 CHARACTERS TOTAL"
        " - REMEMBER we are in the year 2025 and there are 32 NHL teams"
        " - DO NOT try to guess a player's first name if it is not included"
        " - DO NOT substitute or invent players, teams, or facts"
        " - DO NOT include puzzles, questions, or unrelated content"
        " - DO NOT include any instructions or placeholders"
        " - DO NOT make up information not present in the title or description"
        " - ONLY output the final social media post text with no prefix or explanation"
        " - DO NOT include any placeholders or quotations around the outputted text"
    )

    client = OpenAI(
        api_key = api_token,
        base_url = "https://api.llmapi.com/"
    )

    if highlight:
        prompt = (
            f"Write a short, engaging social media post about this recent hockey game. {subtitle}\n"
            f"{requirements}"
        )
    else:
        prompt = (
            f"Title: {title}\n"
            f"Subtitle: {subtitle}\n"
            "Write a short, engaging social media post about this hockey news article.\n"
            f"{requirements}"
            )
    
    print(f"Constructed prompt (length: {len(prompt)})")
    print(f"Using model: {LLAMA_API_MODEL}")
        
    try:
        print(f"Sending API request at {time.ctime()}...")
        start_time = time.time()
        
        chat_completion = client.chat.completions.create(
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=LLAMA_API_MODEL,
            stream=False
        )
        
        end_time = time.time()
        print(f"Response received in {end_time - start_time:.2f} seconds")
        
        result = chat_completion.choices[0].message.content
        clean_result = result.strip()
        
        print(f"Result cleaned, length: {len(clean_result)}")
        
        if len(clean_result) > 250:
            clean_result = clean_result[:247] + "..."
            print("Result truncated to 250 chars")
            
        print(f"Generated text: {clean_result[:50]}...")
        print("=== API REQUEST COMPLETE ===")
        
        return clean_result
    except Exception as e:
        print(f"=== API REQUEST FAILED ===")
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        print("=== END ERROR ===")
        return None

def send_request_direct(title: str, subtitle: str = "", highlight: bool = False):
    """Direct implementation without using LangChain"""
    
    print(f"Starting direct Ollama request at {time.ctime()}")
    
    # Create a simple prompt
    if highlight:
        prompt = f"Write a short, engaging social media post about this hockey highlight video. Title: {title}. Description: {subtitle}. Keep it under 200 characters."
    else:
        prompt = f"Write a short, engaging social media post about this hockey news article. Title: {title}. Summary: {subtitle}. Keep it under 200 characters."
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 250
        }
    }
    
    try:
        start_time = time.time()
        print(f"Sending direct API request to Ollama...")
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=600  # 10-minute timeout
        )
        
        end_time = time.time()
        print(f"Response received in {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            # Clean up the result
            clean_result = result.strip()
            if len(clean_result) > 200:
                clean_result = clean_result[:197] + "..."
            
            print(f"Generated text (length: {len(clean_result)}): {clean_result[:50]}...")
            return clean_result
        else:
            print(f"Error status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Direct API request failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def list_available_models():
    """List all available models in the local Ollama instance"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("Available models:")
            for model in models:
                print(f"- {model['name']} ({model.get('details', {}).get('parameter_size', 'Unknown size')})")
        else:
            print(f"Failed to get models. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error listing models: {e}")