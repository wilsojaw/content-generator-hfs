import os
import gradio as gr
from dotenv import load_dotenv
from manual_vertical_service import (
    generate_caption_ideas,
    generate_content_ideas,
    generate_caption_ideas_claude,
    generate_content_ideas_claude,
)

# Load environment variables
load_dotenv()

# Verify API keys are available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

# Define the industry options
industries = [
    'Lifestyle',
    'Fitness',
    'Music',
    'Fashion',
    'Food',
    'Tech',
    'Travel',
    'Gaming',
    'Parenting',
    'Education',
    'Entertainment',
    'Beauty',
    'Sports',
    'Comedy'
]

def generate_captions(text_brief: str, industry: str, model_choice: str) -> tuple[str, str, str]:
    try:
        if not text_brief or not text_brief.strip():
            return "Please enter a campaign brief", "Please enter a campaign brief", "Please enter a campaign brief"
        if not industry:
            return "Please select an industry", "Please select an industry", "Please select an industry"
        if model_choice == "gpt-4":
            captions = generate_caption_ideas(text_brief, industry)
        else:
            captions = generate_caption_ideas_claude(text_brief, industry)
        return captions[0], captions[1], captions[2]
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        return error_msg, error_msg, error_msg

def generate_content(text_brief: str, industry: str, model_choice: str) -> tuple[str, str, str]:
    try:
        if not text_brief or not text_brief.strip():
            return "Please enter a campaign brief", "Please enter a campaign brief", "Please enter a campaign brief"
        if not industry:
            return "Please select an industry", "Please select an industry", "Please select an industry"
        if model_choice == "gpt-4":
            contents = generate_content_ideas(text_brief, industry)
        else:
            contents = generate_content_ideas_claude(text_brief, industry)
        return contents[0], contents[1], contents[2]
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        return error_msg, error_msg, error_msg

# Create the Gradio interface
demo = gr.Blocks()

with demo:
    gr.Markdown("# Manual Vertical Mode Content Generator")
    
    with gr.Row():
        with gr.Column():
            text_brief = gr.Textbox(
                label="Campaign Brief",
                placeholder="Enter your campaign brief here...",
                lines=10,
                value=""
            )
            industry = gr.Dropdown(
                choices=industries,
                label="Select Industry",
                value=industries[0]
            )
            model_choice = gr.Dropdown(
                choices=["gpt-4", "claude"],
                label="Select Model",
                value="gpt-4"
            )
            
            with gr.Row():
                caption_button = gr.Button("Generate Captions")
                content_button = gr.Button("Generate Content Ideas")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Caption Ideas")
            caption1 = gr.Textbox(label="Caption 1", lines=2, value="")
            caption2 = gr.Textbox(label="Caption 2", lines=2, value="")
            caption3 = gr.Textbox(label="Caption 3", lines=2, value="")
        
        with gr.Column():
            gr.Markdown("### Content Ideas")
            content1 = gr.Textbox(label="Content 1", lines=2, value="")
            content2 = gr.Textbox(label="Content 2", lines=2, value="")
            content3 = gr.Textbox(label="Content 3", lines=2, value="")
    
    caption_button.click(
        fn=generate_captions,
        inputs=[text_brief, industry, model_choice],
        outputs=[caption1, caption2, caption3],
        api_name="generate_captions"
    )
    
    content_button.click(
        fn=generate_content,
        inputs=[text_brief, industry, model_choice],
        outputs=[content1, content2, content3],
        api_name="generate_content"
    )

# Launch the app
demo.launch() 