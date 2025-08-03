import json
from .config import model
from .prompt import build_prompt

def analyze_brief(row):
   # print(f"Row data: {row}")
    prompt = build_prompt(row)
   # print(f"Prompt built: {prompt}")
    if not prompt:
        return "Missing mandatory Title field"
    try:
        #print(f"Response received: here")
        response = model.generate_content(prompt)
       # print(f"Response received: {response.text}")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
    



def smart_merge_rows(old_row, new_row):
    # Normalize: convert Series to dict if needed
    if hasattr(old_row, "to_dict"):
        old_row = old_row.to_dict()
    if hasattr(new_row, "to_dict"):
        new_row = new_row.to_dict()

    prompt = f"""
You are a data cleaner. Given old data and new data of a challenge, merge them into a clean single entry.
If old data is None, just return the new data.
Use the most complete and accurate information.

Old:
{json.dumps(old_row, indent=2) if old_row else "None"}

New:
{json.dumps(new_row, indent=2)}

Return the merged result as a valid JSON object.
"""
    try:
        response = model.generate_content(prompt)

        # Try to find the start of the JSON block
        json_start = response.text.find("{")
        json_str = response.text[json_start:]
        return json.loads(json_str)
    except Exception as e:
        print("⚠️ Failed to parse merged response:", e)
        return new_row  # fallback
