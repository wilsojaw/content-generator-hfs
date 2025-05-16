import json
import re
from typing import List, Tuple, Dict, Optional
from json.decoder import JSONDecoder, JSONDecodeError
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

# Clear proxy settings to avoid unexpected client parameters
for _var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ.pop(_var, None)

# Helper: Call OpenAI API (simple version for Hugging Face)
def call_openai_api(messages, model="gpt-4"):
    print("\n=== OpenAI API Call ===")
    print(f"Model: {model}")
    print("Messages:")
    for msg in messages:
        print(f"- {msg['role']}: {msg['content'][:100]}...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    
    print(f"API Key found: {api_key[:5]}...")
    
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=512
        )
        print("API call successful!")
        return response
    except Exception as e:
        print(f"API call failed: {str(e)}")
        raise e

def _robust_json_parse(raw_str, keys, expected_count=3):
    import re, json
    # Tier 1: Try direct JSON parse
    try:
        data = json.loads(raw_str)
        for key in keys:
            ideas = data.get(key)
            if isinstance(ideas, list) and len(ideas) == expected_count:
                return ideas
    except Exception:
        pass
    # Tier 2: Sanitize and try again
    cleaned = re.sub(r"[\x00-\x1F\x7F]", " ", raw_str).strip()
    try:
        data = json.loads(cleaned)
        for key in keys:
            ideas = data.get(key)
            if isinstance(ideas, list) and len(ideas) == expected_count:
                return ideas
    except Exception:
        pass
    # Tier 3: Regex fallback for bullet/numbered lists
    bullets = re.findall(r"[-•*]\s*(.+)", raw_str)
    if len(bullets) == expected_count:
        return [b.strip() for b in bullets]
    numbers = re.split(r"\d+\.\s*", raw_str)
    numbered = [n.strip() for n in numbers if n.strip()]
    if len(numbered) == expected_count:
        return numbered
    # Fallback
    return [f"Default idea {i+1}" for i in range(expected_count)]

def validate_industry_relevance(text: str, industry: str) -> bool:
    """Validate if the generated content is relevant to the specified industry."""
    try:
        response = call_openai_api([
            {"role": "system", "content": f"You are an industry expert. Evaluate if the following content is relevant to the {industry} industry. Consider industry-specific terminology, themes, and context. Return ONLY a JSON object with a single boolean field 'is_relevant'."},
            {"role": "user", "content": text}
        ], model="gpt-4")
        
        result = json.loads(response.choices[0].message.content)
        return result.get('is_relevant', False)
    except Exception as e:
        print(f"Error in validate_industry_relevance: {str(e)}")
        return True  # Default to True if validation fails

def generate_caption_ideas(text: str, industry: str) -> List[str]:
    """Generate caption ideas based on the brief."""
    print(f"\n=== Generating Captions for {industry} ===")
    try:
        response = call_openai_api([
            {"role": "system", "content": f"You are a creative strategist for a digital agency specializing in {industry}. Based on the following campaign brief, generate exactly three short, engaging caption ideas for social media posts. Each caption MUST be specifically relevant to the {industry} industry. Return ONLY a valid JSON object with a single key: 'captions', whose value is an array of three strings. No commentary, no extra fields, no markdown, no code block."},
            {"role": "user", "content": text}
        ], model="gpt-4")
        
        arguments_str = response.choices[0].message.content
        print(f"Raw response: {arguments_str}")
        captions = _robust_json_parse(arguments_str, ["captions", "caption_ideas"], 3)
        
        # Validate each caption and regenerate failed ones
        final_captions = []
        for i, caption in enumerate(captions):
            if validate_industry_relevance(caption, industry):
                final_captions.append(caption)
            else:
                print(f"Caption not relevant to {industry}: {caption}")
                # Regenerate just this caption
                try:
                    response = call_openai_api([
                        {"role": "system", "content": f"You are a creative strategist for a digital agency specializing in {industry}. Generate ONE short, engaging caption idea for social media posts that is specifically relevant to the {industry} industry. Return ONLY the caption text, with no additional formatting or structure."},
                        {"role": "user", "content": text}
                    ], model="gpt-4")
                    
                    new_caption = response.choices[0].message.content.strip()
                    if validate_industry_relevance(new_caption, industry):
                        final_captions.append(new_caption)
                    else:
                        print(f"Regenerated caption still not relevant to {industry}: {new_caption}")
                        final_captions.append(f"{new_caption} (low relevance)")
                except Exception as e:
                    print(f"Error regenerating caption: {str(e)}")
                    final_captions.append(f"{caption} (low relevance)")
        
        print(f"Final captions: {final_captions}")
        return final_captions
    except Exception as e:
        print(f"Error in generate_caption_ideas: {str(e)}")
        raise e

def _parse_single_item(raw_str, keys):
    """Parse a single item from a JSON response."""
    try:
        data = json.loads(raw_str)
        for key in keys:
            if key in data:
                return str(data[key]).strip()
    except Exception:
        pass
    # If JSON parsing fails, try to extract the content directly
    try:
        # Remove any JSON wrapper if present
        content = re.sub(r'^{.*?"content_idea":\s*"|"}$', '', raw_str)
        return content.strip()
    except Exception:
        return raw_str.strip()

def generate_content_ideas(text: str, industry: str) -> List[str]:
    """Generate content ideas based on the brief."""
    print(f"\n=== Generating Content Ideas for {industry} ===")
    try:
        response = call_openai_api([
            {"role": "system", "content": f"You are a creative strategist for a digital agency specializing in {industry}. Based on the following campaign brief, generate exactly three detailed content ideas for social media posts. Each idea MUST be specifically relevant to the {industry} industry. Return ONLY a valid JSON object with a single key: 'content_ideas', whose value is an array of three strings. No commentary, no extra fields, no markdown, no code block."},
            {"role": "user", "content": text}
        ], model="gpt-4")
        
        arguments_str = response.choices[0].message.content
        print(f"Raw response: {arguments_str}")
        content_ideas = _robust_json_parse(arguments_str, ["content_ideas", "contents", "content"], 3)
        
        # Validate each content idea and regenerate failed ones
        final_ideas = []
        for i, idea in enumerate(content_ideas):
            if validate_industry_relevance(idea, industry):
                final_ideas.append(idea)
            else:
                print(f"Content idea not relevant to {industry}: {idea}")
                # Regenerate just this idea
                try:
                    response = call_openai_api([
                        {"role": "system", "content": f"You are a creative strategist for a digital agency specializing in {industry}. Generate ONE detailed content idea for social media posts that is specifically relevant to the {industry} industry. Return ONLY the content idea text, with no additional formatting or structure."},
                        {"role": "user", "content": text}
                    ], model="gpt-4")
                    
                    new_idea = response.choices[0].message.content.strip()
                    if validate_industry_relevance(new_idea, industry):
                        final_ideas.append(new_idea)
                    else:
                        print(f"Regenerated content idea still not relevant to {industry}: {new_idea}")
                        final_ideas.append(f"{new_idea} (low relevance)")
                except Exception as e:
                    print(f"Error regenerating content idea: {str(e)}")
                    final_ideas.append(f"{idea} (low relevance)")
        
        print(f"Final content ideas: {final_ideas}")
        return final_ideas
    except Exception as e:
        print(f"Error in generate_content_ideas: {str(e)}")
        raise e

def generate_brief_and_ideas(text_brief: str, industry: str, demographics: Optional[Dict[str, List[str]]] = None) -> Tuple[str, List[str], List[str]]:
    """Generate summary and ideas from a brief."""
    print("\n=== Starting Content Generation ===")
    print(f"Industry: {industry}")
    print(f"Brief: {text_brief[:100]}...")
    
    if not text_brief or not text_brief.strip():
        print("Error: No brief provided")
        return "No brief provided. Please enter a text brief.", [], []
    if not industry or not industry.strip():
        print("Error: No industry provided")
        return "No industry provided. Please select an industry.", [], []
    
    try:
        summarized = text_brief.strip()
        default_demographics = {
            "age_range": ["18–24", "25–34"],
            "gender": ["Male", "Female"]
        }
        demographics_context = f"""
Demographics (default values used):
- Age Range: {', '.join(default_demographics['age_range'])}
- Gender: {', '.join(default_demographics['gender'])}

Original Brief:
{summarized}
"""
        print("Generating captions...")
        captions = generate_caption_ideas(demographics_context, industry)
        print("Generating content ideas...")
        contents = generate_content_ideas(demographics_context, industry)
        print("=== Content Generation Complete ===")
        return summarized, captions, contents
    except Exception as e:
        print(f"Error in generate_brief_and_ideas: {str(e)}")
        raise e

def generate_caption_ideas_claude(text: str, industry: str) -> list:
    """Generate caption ideas using Claude API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    try:
        # First attempt to generate all captions
        prompt = f"You are a creative strategist for a digital agency specializing in {industry}. Based on the following campaign brief, generate exactly three short, engaging caption ideas for social media posts. Each caption MUST be specifically relevant to the {industry} industry. Return ONLY a valid JSON object with a single key: 'captions', whose value is an array of three strings. No commentary, no extra fields, no markdown, no code block.\n\n{text}"
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 512,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        content = response.json()["content"][0]["text"]
        print(f"Claude raw response: {content}")
        captions = _robust_json_parse(content, ["captions", "caption_ideas"], 3)
        
        # Validate each caption and regenerate failed ones
        final_captions = []
        for i, caption in enumerate(captions):
            if validate_industry_relevance(caption, industry):
                final_captions.append(caption)
            else:
                print(f"Claude caption not relevant to {industry}: {caption}")
                # Regenerate just this caption
                try:
                    prompt = f"You are a creative strategist for a digital agency specializing in {industry}. Generate ONE short, engaging caption idea for social media posts that is specifically relevant to the {industry} industry. Return ONLY the caption text, with no additional formatting or structure.\n\n{text}"
                    data = {
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 512,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                    
                    response = requests.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    new_content = response.json()["content"][0]["text"]
                    new_caption = new_content.strip()
                    
                    if validate_industry_relevance(new_caption, industry):
                        final_captions.append(new_caption)
                    else:
                        print(f"Regenerated Claude caption still not relevant to {industry}: {new_caption}")
                        final_captions.append(f"{new_caption} (low relevance)")
                except Exception as e:
                    print(f"Error regenerating Claude caption: {str(e)}")
                    final_captions.append(f"{caption} (low relevance)")
        
        print(f"Claude final captions: {final_captions}")
        return final_captions
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        return [f"Claude caption idea {i+1}" for i in range(3)]

def generate_content_ideas_claude(text: str, industry: str) -> list:
    """Generate content ideas using Claude API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    try:
        # First attempt to generate all content ideas
        prompt = f"You are a creative strategist for a digital agency specializing in {industry}. Based on the following campaign brief, generate exactly three detailed content ideas for social media posts. Each idea MUST be specifically relevant to the {industry} industry. Return ONLY a valid JSON object with a single key: 'content_ideas', whose value is an array of three strings. No commentary, no extra fields, no markdown, no code block.\n\n{text}"
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 512,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        content = response.json()["content"][0]["text"]
        print(f"Claude raw response: {content}")
        content_ideas = _robust_json_parse(content, ["content_ideas", "contents", "content"], 3)
        
        # Validate each content idea and regenerate failed ones
        final_ideas = []
        for i, idea in enumerate(content_ideas):
            if validate_industry_relevance(idea, industry):
                final_ideas.append(idea)
            else:
                print(f"Claude content idea not relevant to {industry}: {idea}")
                # Regenerate just this idea
                try:
                    prompt = f"You are a creative strategist for a digital agency specializing in {industry}. Generate ONE detailed content idea for social media posts that is specifically relevant to the {industry} industry. Return ONLY the content idea text, with no additional formatting or structure.\n\n{text}"
                    data = {
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 512,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                    
                    response = requests.post(url, headers=headers, json=data)
                    response.raise_for_status()
                    new_content = response.json()["content"][0]["text"]
                    new_idea = new_content.strip()
                    
                    if validate_industry_relevance(new_idea, industry):
                        final_ideas.append(new_idea)
                    else:
                        print(f"Regenerated Claude content idea still not relevant to {industry}: {new_idea}")
                        final_ideas.append(f"{new_idea} (low relevance)")
                except Exception as e:
                    print(f"Error regenerating Claude content idea: {str(e)}")
                    final_ideas.append(f"{idea} (low relevance)")
        
        print(f"Claude final content ideas: {final_ideas}")
        return final_ideas
    except Exception as e:
        print(f"Claude API error: {str(e)}")
        return [f"Claude content idea {i+1}" for i in range(3)]