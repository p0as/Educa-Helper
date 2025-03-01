# Educa Helper (Unofficial)

**Python** code that uses **pygame**, this code will help study sat Math materials in an organized fashion by taking your excesise images and answers, then testing you on that knowledge!

________________________________________________________________________________________________________________

# DISCLAIMER
This is a personal project designed to help users complete exercises from Educa College Prep. 
This project is **not affiliated with, endorsed by, or officially supported by Educa College Prep**.

## Important:
- This repository **only contains the code** to assist in **studying and revising** the exercises.
- **No Educa materials (images, meshes, exercises) are included.** You must have your own access.
- This software is for **personal, educational use only**. **Commercial use is strictly prohibited.**
- All rights to **Educa’s materials (exercises, images, meshes, etc.) remain with their respective owners.**

________________________________________________________________________________________________________________

# How to use

## Prerequisites
- Python 3.x
- Pygame (`pip install pygame`)

## Setup
1. **Clone the Repository**:
   ```bash
   git clone <https://github.com/p0as/Educa-Helper>
   cd <Educa-Helper>

2. **use this json structure to customize questions:**
   {
    "sections": {
        "sectionA": {
            "section_name": "Triangles",
            "questions": [
                {
                    "id": "q1",
                    "image": "path to question image",
                    "answer": "30",
                    "answer_sheet": "path to answersheet of the question",
                    "tags": ["geometry", "triangles"]
                },
                {
                    "id": "q2",
                    "image": "images/geometry1/question2.png",
                    "answer": "31",
                    "answer_sheet": "images/geometry1/answersheet2.png",
                    "tags": ["geometry", "triangles"]
                }
            ]
        },
        "sectionB": {
            "section_name": "Circles",
            "questions": []
        }
    }
}
3. **run the program**
   python sat_study_helper.py

# notes
Missing assets (icons, sounds) will fallback to placeholders with warnings.
Progress is saved in sat_data/*.json files. Ensure write permissions.
