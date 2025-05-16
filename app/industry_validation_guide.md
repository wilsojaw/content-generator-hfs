# Adding Industry Validation to Your Content Generator

This guide shows how to add the industry validation system to your existing content generation app.

## 1. Required Functions

Copy these two essential functions to your app:

```python
def validate_industry_relevance(text: str, industry: str) -> bool:
    """
    Validates if content is relevant to the specified industry.
    
    Args:
        text (str): The content to validate
        industry (str): The target industry
    
    Returns:
        bool: True if content is industry-relevant, False otherwise
    """
    try:
        response = call_openai_api([
            {"role": "system", "content": f"You are an industry expert. Evaluate if the following content is relevant to the {industry} industry. Consider industry-specific terminology, themes, and context. Return ONLY a JSON object with a single boolean field 'is_relevant'."},
            {"role": "user", "content": text}
        ])
        
        result = json.loads(response.choices[0].message.content)
        return result.get('is_relevant', False)
    except Exception as e:
        print(f"Error in validate_industry_relevance: {str(e)}")
        return True  # Default to True if validation fails

def _robust_json_parse(raw_str, keys, expected_count=3):
    """
    Robust JSON parsing with multiple fallback methods.
    Only needed for initial batch generation of multiple items.
    """
    # Tier 1: Direct JSON parse
    try:
        data = json.loads(raw_str)
        for key in keys:
            ideas = data.get(key)
            if isinstance(ideas, list) and len(ideas) == expected_count:
                return ideas
    except Exception:
        pass

    # Tier 2: Sanitized JSON parse
    cleaned = re.sub(r"[\x00-\x1F\x7F]", " ", raw_str).strip()
    try:
        data = json.loads(cleaned)
        for key in keys:
            ideas = data.get(key)
            if isinstance(ideas, list) and len(ideas) == expected_count:
                return ideas
    except Exception:
        pass

    # Tier 3: Regex fallback
    bullets = re.findall(r"[-•*]\s*(.+)", raw_str)
    if len(bullets) == expected_count:
        return [b.strip() for b in bullets]
    
    numbers = re.split(r"\d+\.\s*", raw_str)
    numbered = [n.strip() for n in numbers if n.strip()]
    if len(numbered) == expected_count:
        return numbered
```

## 2. Modify Your Existing Generation Function

Add validation to your existing content generation function:

```python
def your_existing_generation_function(text: str, industry: str) -> List[str]:
    # Your existing generation code here
    generated_content = your_current_generation_logic(text)
    
    # Add validation
    final_content = []
    for item in generated_content:
        if validate_industry_relevance(item, industry):
            final_content.append(item)
        else:
            # Regenerate just this item
            try:
                response = call_openai_api([
                    {"role": "system", "content": f"Generate ONE content piece for {industry}. Return ONLY the content text, with no additional formatting or structure."},
                    {"role": "user", "content": text}
                ])
                
                new_item = response.choices[0].message.content.strip()
                if validate_industry_relevance(new_item, industry):
                    final_content.append(new_item)
                else:
                    final_content.append(f"{new_item} (low relevance)")
            except Exception as e:
                print(f"Error regenerating content: {str(e)}")
                final_content.append(f"{item} (low relevance)")
    
    return final_content
```

## 3. Required Imports

Add these imports to your app:

```python
import json
import re
from typing import List
from openai import OpenAI
```

## 4. Example Integration

Here's how to integrate with different types of content generation:

### For Single Content Generation
```python
def generate_single_content(text: str, industry: str) -> str:
    # Generate content
    content = your_generation_function(text)
    
    # Validate
    if validate_industry_relevance(content, industry):
        return content
    else:
        # Regenerate
        try:
            response = call_openai_api([
                {"role": "system", "content": f"Generate ONE content piece for {industry}. Return ONLY the content text, with no additional formatting or structure."},
                {"role": "user", "content": text}
            ])
            new_content = response.choices[0].message.content.strip()
            if validate_industry_relevance(new_content, industry):
                return new_content
            else:
                return f"{new_content} (low relevance)"
        except Exception as e:
            return f"{content} (low relevance)"
```

### For Batch Content Generation
```python
def generate_batch_content(text: str, industry: str, batch_size: int) -> List[str]:
    # Generate batch
    batch = your_batch_generation_function(text, batch_size)
    
    # Validate each item
    final_batch = []
    for item in batch:
        if validate_industry_relevance(item, industry):
            final_batch.append(item)
        else:
            # Regenerate individual item
            try:
                response = call_openai_api([
                    {"role": "system", "content": f"Generate ONE content piece for {industry}. Return ONLY the content text, with no additional formatting or structure."},
                    {"role": "user", "content": text}
                ])
                new_item = response.choices[0].message.content.strip()
                if validate_industry_relevance(new_item, industry):
                    final_batch.append(new_item)
                else:
                    final_batch.append(f"{new_item} (low relevance)")
            except Exception as e:
                final_batch.append(f"{item} (low relevance)")
    
    return final_batch
```

## 5. Customization Options

### Adjust Validation Strictness
```python
def validate_industry_relevance(text: str, industry: str, strictness: float = 0.7) -> bool:
    """
    Add strictness parameter to control validation threshold
    """
    try:
        response = call_openai_api([
            {"role": "system", "content": f"You are an industry expert. Evaluate if the following content is relevant to the {industry} industry (strictness: {strictness}). Consider industry-specific terminology, themes, and context. Return ONLY a JSON object with a single boolean field 'is_relevant'."},
            {"role": "user", "content": text}
        ])
        
        result = json.loads(response.choices[0].message.content)
        return result.get('is_relevant', False)
    except Exception as e:
        print(f"Error in validate_industry_relevance: {str(e)}")
        return True
```

### Add Industry-Specific Rules
```python
def get_industry_rules(industry: str) -> dict:
    """
    Define specific rules for each industry
    """
    rules = {
        'Tech': {
            'required_terms': ['digital', 'innovation', 'technology'],
            'forbidden_terms': ['outdated', 'obsolete'],
            'min_technical_terms': 2
        },
        'Fashion': {
            'required_terms': ['style', 'trend', 'design'],
            'forbidden_terms': ['outdated', 'unfashionable'],
            'min_style_terms': 2
        }
        # Add more industries
    }
    return rules.get(industry, {})
```

## 6. Error Handling

Add these error handling patterns:

```python
def safe_validation(text: str, industry: str) -> bool:
    """
    Wrapper for validation with error handling
    """
    try:
        return validate_industry_relevance(text, industry)
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return True  # Default to True on error

def safe_regeneration(text: str, industry: str) -> str:
    """
    Wrapper for regeneration with error handling
    """
    try:
        response = call_openai_api([
            {"role": "system", "content": f"Generate ONE content piece for {industry}. Return ONLY the content text, with no additional formatting or structure."},
            {"role": "user", "content": text}
        ])
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Regeneration error: {str(e)}")
        return f"{text} (low relevance)"
```

## 7. Performance Tips

1. **Cache Validation Results**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_validation(text: str, industry: str) -> bool:
    return validate_industry_relevance(text, industry)
```

2. **Batch Processing**
```python
def batch_validate(content_list: List[str], industry: str) -> List[bool]:
    """
    Validate multiple items in one API call
    """
    combined_text = "\n".join(content_list)
    try:
        response = call_openai_api([
            {"role": "system", "content": f"Evaluate each content piece for {industry} relevance. Return JSON with boolean array 'is_relevant'."},
            {"role": "user", "content": combined_text}
        ])
        results = json.loads(response.choices[0].message.content)
        return results.get('is_relevant', [True] * len(content_list))
    except Exception as e:
        print(f"Batch validation error: {str(e)}")
        return [True] * len(content_list)
``` 