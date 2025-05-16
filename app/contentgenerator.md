# Content Generator Technical Documentation

## System Architecture

### Core Components
1. **User Interface (Gradio)**
   - Input handling
   - Model selection
   - Industry selection
   - Content display

2. **Content Generation Service**
   - GPT-4 integration
   - Claude 3.5 integration
   - Industry validation system

3. **Validation System**
   - Industry relevance checking
   - Content regeneration logic
   - Relevance tagging

## Functional Flow

### 1. User Input Processing
```python
def generate_captions(text_brief: str, industry: str, model_choice: str):
    # Input validation
    if not text_brief or not text_brief.strip():
        return "Please enter a campaign brief"
    if not industry:
        return "Please select an industry"
    
    # Model selection
    if model_choice == "gpt-4":
        captions = generate_caption_ideas(text_brief, industry)
    else:
        captions = generate_caption_ideas_claude(text_brief, industry)
```

### 2. Content Generation
```python
def generate_caption_ideas(text: str, industry: str) -> List[str]:
    # Initial generation
    response = call_openai_api([
        {"role": "system", "content": f"You are a creative strategist for {industry}..."},
        {"role": "user", "content": text}
    ])
    
    # Parse response
    captions = _robust_json_parse(arguments_str, ["captions", "caption_ideas"], 3)
```

### 3. Industry Validation System

#### 3.1 Validation Function
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
```

#### 3.2 Validation Process Flow
1. **Initial Content Generation**
   ```python
   # Generate initial content
   captions = _robust_json_parse(arguments_str, ["captions", "caption_ideas"], 3)
   ```

2. **Individual Content Validation**
   ```python
   final_captions = []
   for i, caption in enumerate(captions):
       if validate_industry_relevance(caption, industry):
           final_captions.append(caption)
       else:
           # Regeneration logic
   ```

3. **Regeneration for Failed Content**
   ```python
   # Regenerate just the failed content
   try:
       response = call_openai_api([
           {"role": "system", "content": f"Generate ONE caption for {industry}..."},
           {"role": "user", "content": text}
       ])
       
       new_caption = _robust_json_parse(response.choices[0].message.content, ["caption"], 1)[0]
       if validate_industry_relevance(new_caption, industry):
           final_captions.append(new_caption)
       else:
           final_captions.append(f"{new_caption} (low relevance)")
   ```

### 4. Error Handling and Recovery

#### 4.1 JSON Parsing
```python
def _robust_json_parse(raw_str, keys, expected_count=3):
    """
    Robust JSON parsing with multiple fallback methods.
    
    Args:
        raw_str (str): Raw string to parse
        keys (list): List of possible JSON keys
        expected_count (int): Expected number of items
    
    Returns:
        list: Parsed items
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

#### 4.2 API Error Handling
```python
try:
    response = call_openai_api([...])
except Exception as e:
    print(f"API call failed: {str(e)}")
    # Fallback to original content with low relevance tag
    final_captions.append(f"{caption} (low relevance)")
```

## Integration Guide

### 1. Setting Up Industry Validation
```python
# 1. Import required functions
from manual_vertical_service import validate_industry_relevance

# 2. Implement validation in your content generation
def your_content_generator(text: str, industry: str):
    # Generate content
    content = generate_initial_content(text)
    
    # Validate
    if validate_industry_relevance(content, industry):
        return content
    else:
        # Regenerate or tag as low relevance
        return f"{content} (low relevance)"
```

### 2. Customizing Validation Criteria
```python
def custom_industry_validation(text: str, industry: str, criteria: dict) -> bool:
    """
    Custom validation with specific criteria.
    
    Args:
        text (str): Content to validate
        industry (str): Target industry
        criteria (dict): Custom validation criteria
    
    Returns:
        bool: Validation result
    """
    # Add your custom validation logic here
    pass
```

## Best Practices

1. **Industry Validation**
   - Always validate content against specific industry context
   - Use clear industry-specific terminology in prompts
   - Consider industry-specific metrics and KPIs

2. **Error Handling**
   - Implement multiple fallback methods
   - Preserve original content when possible
   - Use clear error messaging

3. **Content Generation**
   - Use industry-specific prompts
   - Include context about target audience
   - Consider industry trends and best practices

4. **Performance Optimization**
   - Cache validation results when possible
   - Batch process similar content
   - Use appropriate model sizes for validation

## Extending the System

### 1. Adding New Industries
```python
# Add to industries list
industries = [
    'Lifestyle',
    'Fitness',
    # Add your new industry
    'YourNewIndustry'
]

# Update validation criteria if needed
industry_criteria = {
    'YourNewIndustry': {
        'required_terms': [...],
        'forbidden_terms': [...],
        'context_rules': [...]
    }
}
```

### 2. Custom Validation Rules
```python
def custom_validation_rules(industry: str) -> dict:
    """
    Define custom validation rules for specific industries.
    """
    rules = {
        'Tech': {
            'min_technical_terms': 2,
            'required_context': ['innovation', 'digital'],
            'forbidden_terms': ['outdated', 'obsolete']
        }
        # Add more industries
    }
    return rules.get(industry, {})
```

## Troubleshooting

### Common Issues

1. **Validation False Positives**
   - Review industry-specific terminology
   - Adjust validation criteria
   - Consider adding industry-specific examples

2. **API Rate Limits**
   - Implement rate limiting
   - Cache validation results
   - Use appropriate API tiers

3. **Content Quality**
   - Refine prompts
   - Add more context
   - Adjust validation thresholds

## Future Improvements

1. **Enhanced Validation**
   - Machine learning-based relevance scoring
   - Industry-specific sentiment analysis
   - Trend-based validation

2. **Performance**
   - Parallel processing
   - Caching system
   - Batch validation

3. **Customization**
   - User-defined validation rules
   - Industry-specific templates
   - Custom scoring systems 