import pandas as pd
import re

def parse_output(output):
    def extract(field):
        pattern = rf"{field}:\s*(.*?)(?=\n[A-Z][a-z]+:|$)"
        match = re.search(pattern, output, re.DOTALL)
        return match.group(1).strip() if match else ""

    return pd.Series({
        "Title": extract("Title"),
        "Summary": extract("Summary"),
        "Fields": extract("Fields"),
        "Skills": extract("Skills"),
        "Workshops": extract("Workshops"),
        "Mentors": extract("Mentors"),
        "Category": extract("Category")
    })
