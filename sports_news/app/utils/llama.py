from langchain_ollama.llms import OllamaLLM
from app.utils.prompts import get_prompt
import psutil

MODEL_NAME = "mistral"

def send_request(title: str, subtitle: str = "", body: str = "", highlight: bool = False):
    print(f"=== LLM REQUEST DEBUG ===")
    print(f"Time: {time.ctime()}")
    
    # Check available memory before proceeding
    available_mem_gb = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    print(f"Available memory: {available_mem_gb:.2f} GB")
    
    if available_mem_gb < 6.0:  # Require at least 6GB to be safe
        print(f"WARNING: Not enough memory available ({available_mem_gb:.2f} GB)")
        print("Falling back to direct method...")
        return send_request_direct(title, subtitle, highlight)
    
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle[:50]}...")
    print(f"Highlight: {highlight}")
    
    try:
        # Create the Ollama LLM instance
        print("Creating OllamaLLM instance...")
        llm = OllamaLLM(
            model=MODEL_NAME, 
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

def send_request_direct(title: str, subtitle: str = "", highlight: bool = False):
    """Direct implementation without using LangChain"""
    import requests
    import time
    
    print(f"Starting direct Ollama request at {time.ctime()}")
    
    # Create a simple prompt
    if highlight:
        prompt = f"Write a short, engaging social media post about this hockey highlight video. Title: {title}. Description: {subtitle}. Keep it under 200 characters."
    else:
        prompt = f"Write a short, engaging social media post about this hockey news article. Title: {title}. Summary: {subtitle}. Keep it under 200 characters."
    
    payload = {
        "model": MODEL_NAME,
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
        import requests
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

import time

def main():
    # Show available models
    list_available_models()
    
    # Test data for the request
    title = "Hamilton out remainder of regular season for Devils"
    subtitle = "Defenseman leads New Jersey defensemen in scoring, could return during playoffs"
    
    try:
        print(f"\nSending request to model: {MODEL_NAME}")
        
        # Start timing
        start_time = time.time()
        
        # Make the request
        chat_resp = send_request(title, subtitle)
        
        # End timing
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Print results
        print("\nGenerated Summary:")
        print(chat_resp)
        print(f"Character count: {len(chat_resp)}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()