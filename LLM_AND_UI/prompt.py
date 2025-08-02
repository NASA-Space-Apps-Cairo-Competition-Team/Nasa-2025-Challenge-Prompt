def build_prompt(row):
    if "Title" not in row or not str(row["Title"]).strip():
        return None

    content_parts = []
    fields = ["Title", "Brief", "Objectives", "Subjects", "Potential Considerations", "Background", "Difficulty"]
    for key in fields:
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            content_parts.append(f"{key}:\n{val.strip()}")

    joined_content = "\n\n".join(content_parts)

    return f"""
You will be given a NASA Space Apps hackathon challenge description with some or all of the following sections.

Extract and fill the following structured fields based on the information:

1. Challenge Title: The full challenge title as it appears
2. Challenge Summary: 2-3 lines summarizing the challenge with the core problem and context
3. Relevant Fields: Choose from:
   - GIS / Remote Sensing
   - AI / Machine Learning
   - 3D Modeling / Animation
   - Software Engineering
   - Augmented & Virtual Reality (AR/VR)
   - Storytelling / Video Editing
   - Data Science / Data Analysis
   - Mobile App Development
   - Web Development
   - Artificial Intelligence (AI)
   - Game Development
   - UI & UX Design
4. Required Technical Skills (e.g., Python, Unity, TensorFlow, Blender)
5. Potential Workshop/Session Topics (relevant training or crash courses)
6. Recommended Mentor Specializations
7. Overall Category (e.g., Earth, Space, Health, Humans, Climate, Oceans, etc.)

{joined_content}

Respond ONLY in the following format:

Title: ...
Summary: ...
Fields: ...
Skills: ...
Workshops: ...
Mentors: ...
Category: ...
""".strip()
