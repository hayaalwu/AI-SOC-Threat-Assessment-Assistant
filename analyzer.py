import json
import re
import ollama
from prompts import SOC_ANALYSIS_PROMPT, SOC_DECISION_PROMPT

# Model configuration
MODEL_NAME = "gemma3:4b"

# Clean the model response before parsing JSON
def clean_json_text(text):
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.replace("\\_", "_")
    text = text.strip()

    match = re.search(r"\{.*\}", text, re.DOTALL) # extract JSON across multiple lines

    if not match:
        return None

    return match.group() # return the extracted JSON text

# Convert the cleaned JSON text into a Python dictionary
def parse_json_response(text):
    json_text = clean_json_text(text)

    if json_text is None:
        return None

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None

# Generate structured threat assessment from the uploaded image
def analyze_soc_image(image_path):
    response = ollama.chat(                     # send the request to the vision model
        model=MODEL_NAME,                       # model to use
        messages=[{
                "role": "user",                 # user request
                "content": SOC_ANALYSIS_PROMPT, # analysis prompt
                "images": [image_path],         # input image
            }],
    )

    result = parse_json_response(response["message"]["content"]) # parse the model response

    if result is None: # handle invalid model output
        return {
            "image_type": "Unknown",
            "platform": "Unknown",
            "main_finding": "The model did not return valid JSON.",
            "security_observations": [],
            "confidence_level": "Low",
            "recommended_next_step": "Manual review is required.",
        }

    return result

# Generate the SOC decision using the structured output
def generate_soc_decision(structured_output):
    decision_input = json.dumps(structured_output, indent=2) # convert the structured output to JSON text

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{
                "role": "user",
                "content": SOC_DECISION_PROMPT + "\n\nStructured output:\n" + decision_input, # send the structured output to the decision model
            }],
    )

    result = parse_json_response(response["message"]["content"]) # parse the decision response

    if result is None: # handle invalid model output
        return {
            "overall_soc_status": "Manual Review",
            "decision_reason": "The model did not return a valid decision JSON.",
            "recommended_action": "Assign to SOC analyst for manual review.",
            "next_step": "Review the screenshot and extracted observations manually.",
        }

    return result