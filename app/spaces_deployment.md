# Deploying to Hugging Face Spaces

## 1. Required Files

Create these files in your project root:

### requirements.txt
```
gradio>=4.0.0
openai>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```

### app.py
```python
import os
import gradio as gr
from manual_vertical_service import (
    generate_caption_ideas,
    generate_content_ideas,
    generate_caption_ideas_claude,
    generate_content_ideas_claude,
)

# Your existing main.py code here, but with these modifications:
# 1. Remove the if __name__ == "__main__" block
# 2. Change demo.launch() to:
demo = gr.Blocks()
# ... your existing Gradio interface code ...
demo.launch()
```

### README.md
```markdown
---
title: Manual Vertical Mode Content Generator
emoji: 🎯
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# Manual Vertical Mode Content Generator

[Your existing README content]
```

## 2. Environment Variables

1. Go to your Space's settings
2. Add these secrets:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`

## 3. Project Structure
```
your-space/
├── app.py
├── manual_vertical_service.py
├── requirements.txt
└── README.md
```

## 4. Deployment Steps

1. **Create a New Space**
   - Go to huggingface.co/spaces
   - Click "Create new Space"
   - Choose "Gradio" as the SDK
   - Name your space

2. **Push Your Code**
   ```bash
   # Initialize git if not already done
   git init
   
   # Add Hugging Face as remote
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   
   # Add your files
   git add .
   
   # Commit
   git commit -m "Initial commit"
   
   # Push to Hugging Face
   git push space main
   ```

3. **Monitor Deployment**
   - Go to your Space's page
   - Check the "Build logs" tab
   - Wait for the build to complete

## 5. Common Issues and Solutions

### API Key Issues
```python
# In your app.py, add this at the top:
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API keys are available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
```

### Memory Issues
If you encounter memory issues, add this to your app.py:
```python
import gc

# After each generation
gc.collect()
```

### Rate Limiting
Add rate limiting to your API calls:
```python
from ratelimit import limits, sleep_and_retry

ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 30

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def rate_limited_api_call():
    # Your API call here
    pass
```

## 6. Performance Optimization

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generation(text: str, industry: str):
    # Your generation code here
    pass
```

### Batch Processing
```python
def batch_process(items: list):
    # Process multiple items at once
    pass
```

## 7. Monitoring and Maintenance

### Add Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In your functions
logger.info("Starting content generation")
logger.error("API call failed", exc_info=True)
```

### Health Check
```python
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Add to your Gradio interface
with gr.Blocks() as demo:
    # ... your existing interface ...
    gr.Markdown(f"Status: {health_check()['status']}")
```

## 8. Security Considerations

1. **API Key Protection**
   - Never expose API keys in code
   - Use environment variables
   - Rotate keys regularly

2. **Input Validation**
   ```python
   def validate_input(text: str, industry: str):
       if len(text) > 1000:  # Adjust limit as needed
           raise ValueError("Text too long")
       if industry not in valid_industries:
           raise ValueError("Invalid industry")
   ```

3. **Rate Limiting**
   - Implement per-user rate limiting
   - Add cooldown periods
   - Monitor usage patterns

## 9. Updating Your Space

1. **Make Changes Locally**
2. **Test Thoroughly**
3. **Commit and Push**
   ```bash
   git add .
   git commit -m "Update: [description]"
   git push space main
   ```

## 10. Best Practices

1. **Error Handling**
   - Always catch and handle exceptions
   - Provide user-friendly error messages
   - Log errors for debugging

2. **User Experience**
   - Add loading indicators
   - Provide clear instructions
   - Handle edge cases gracefully

3. **Code Organization**
   - Keep functions modular
   - Add type hints
   - Document your code

4. **Testing**
   - Test locally before deploying
   - Add unit tests
   - Test edge cases

## 11. Troubleshooting

### Common Issues

1. **Build Failures**
   - Check requirements.txt
   - Verify file structure
   - Check build logs

2. **Runtime Errors**
   - Check environment variables
   - Verify API keys
   - Check error logs

3. **Performance Issues**
   - Implement caching
   - Optimize API calls
   - Monitor memory usage

### Debugging Tips

1. **Local Testing**
   ```bash
   # Run locally with same environment
   python app.py
   ```

2. **Logging**
   ```python
   # Add detailed logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

3. **Error Tracking**
   ```python
   try:
       # Your code
   except Exception as e:
       logger.error(f"Error: {str(e)}", exc_info=True)
       # Handle error
   ``` 