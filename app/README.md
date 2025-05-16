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

A powerful content generation tool that creates industry-specific social media captions and content ideas using either GPT-4 or Claude AI models. The application includes built-in industry relevance validation to ensure generated content is appropriate for the selected industry.

## Features

- **Dual AI Model Support**
  - GPT-4 integration
  - Claude 3.5 Sonnet integration
  - Easy switching between models

- **Industry-Specific Content Generation**
  - 14 pre-defined industries
  - Industry relevance validation
  - Automatic content regeneration for low-relevance items

- **Content Types**
  - Social media captions
  - Detailed content ideas
  - Industry-optimized suggestions

## Supported Industries

- Lifestyle
- Fitness
- Music
- Fashion
- Food
- Tech
- Travel
- Gaming
- Parenting
- Education
- Entertainment
- Beauty
- Sports
- Comedy

## Setup

1. **Environment Variables**
   For local development, create a `.env` file in the root directory with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```
   
   For Hugging Face Spaces deployment, add these as secrets in your Space's settings.

2. **Dependencies**
   Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Running the Application**
   - Local development:
     ```bash
     python app.py
     ```
   - Hugging Face Spaces:
     The app will automatically deploy when pushed to the Space.

## Usage

1. **Input Campaign Brief**
   - Enter your campaign brief in the text area
   - Be specific about your goals and target audience

2. **Select Industry**
   - Choose from the dropdown menu of supported industries
   - This helps ensure content relevance

3. **Choose AI Model**
   - Select between GPT-4 and Claude
   - Each model may produce slightly different results

4. **Generate Content**
   - Click "Generate Captions" for social media captions
   - Click "Generate Content Ideas" for detailed content suggestions
   - Each generation produces three unique ideas

## Content Validation

The application includes a sophisticated validation system:

1. **Initial Generation**
   - Generates three content pieces
   - Validates each piece for industry relevance

2. **Regeneration Process**
   - If content fails relevance check, regenerates only that specific piece
   - Marks regenerated content with "(low relevance)" if it still doesn't meet criteria
   - Preserves all generated content for review

## Error Handling

- Input validation for empty briefs and industry selection
- Detailed error messages for API failures
- Graceful fallback for low-relevance content

## Development

The application is built with:
- Gradio for the user interface
- OpenAI and Anthropic APIs for content generation
- Python for backend processing

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Add your license information here]
