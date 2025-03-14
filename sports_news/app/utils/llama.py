import os
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate

# Set the model name - using phi from your available models
MODEL_NAME = "mistral"

def send_request(title: str, subtitle: str = "", body: str = ""):
    # Create the Ollama LLM instance
    llm = OllamaLLM(
        model=MODEL_NAME, 
        base_url="http://localhost:11434",
        temperature=0.3,  # Lower temperature for more focused outputs
        max_tokens=250    # Limit output length
    )
    
    # Define a much more specific prompt template
    prompt = PromptTemplate.from_template(
        """
        You are a sports news summarizer that creates brief, engaging summaries for social media.

        Title of article: {title}
        Description: {subtitle}

        TASK:
        Write ONE short summary of this hockey news article for social media.
        - MUST be EXACTLY 150-250 characters long
        - Focus only on the main news from the title and description
        - Use clear, straightforward language
        - CRITICAL: Be COMPLETELY accurate with player names, team names, and statistics
        - ONLY use player names explicitly mentioned in the title or description
        - DO NOT substitute or invent players, teams, or facts
        - DO NOT include puzzles, rules, questions, or unrelated content
        - DO NOT include any instructions or placeholders
        - DO NOT make up information not present in the title or description
        - DO NOT write anything about database models, SQL queries, or programming
        - ONLY output the final summary text with no prefix or explanation

        Your summary:
        """
    )
    
    try:
        # Use the modern pipe syntax
        chain = prompt | llm
        
        # Run the chain with the input values
        result = chain.invoke({"title": title, "subtitle": subtitle})
        
        # Post-process to remove any potential unwanted content
        clean_result = result.strip()
        
        # If result is too long, truncate to 200 characters
        if len(clean_result) > 200:
            clean_result = clean_result[:197] + "..."
            
        return clean_result
    except Exception as e:
        print(f"An Error occurred in the API call: {e}")
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