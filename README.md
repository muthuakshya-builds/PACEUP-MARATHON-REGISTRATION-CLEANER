# PACEUP – Marathon Registration Cleaner

**Clean Registrations, Smoother Marathons.**

## 1. Project Overview

PACEUP is an AI-powered marathon registration cleaning system designed to process registration messages collected through online forms and WhatsApp.

It uses Google Gemini to extract participant information and Python to validate, clean and identify registration issues.

## 2. Objectives

- Extract participant details from messy registration messages.
- Preserve original information and supporting evidence.
- Identify missing and invalid information.
- Detect duplicate registrations and shared contact details.
- Generate organised registration reports.

## 3. Technologies Used

- Python
- Google Gemini API
- Streamlit
- Pandas
- Google GenAI SDK

## 4. Information Extracted

- Participant name
- Phone number
- Email address
- Age
- Race category

## 5. Project Structure
PACEUP/
│
├── data/
│   └── registrations.csv
│
├── docs/
│   ├── PACEUP_Specification.md
│   └── Red_Team_Results.md
│
├── outputs/
│   ├── clean_list.csv
│   ├── problems.csv
│   └── summary.txt
│
├── .venv/   
├── __pycache__/
│---- main.py     
├── eval.py      
├── red_team.py  
├── test_gemini.py     
├── system_prompt.txt 
├── requirements.txt   
├── README.md        
└── .gitignore     
## 6. Installation

Install the required dependencies:

```bash
uv pip install -r requirements.txt
```

Configure the Gemini API key in a local `.env` file:

```text
GEMINI_API_KEY=your_api_key
```

Do not upload the API key or `.env` file to GitHub.

## 7. Running the Application

Run the following command in the project terminal:

```bash
uv run streamlit run main.py
```

Upload the registration CSV file through the application and start processing.

## 8. Output Files

The application is designed to generate:

- `clean_list.csv` – validated participant registrations.
- `problems.csv` – registrations requiring attention.
- `summary.txt` – processing summary and category-wise counts.

These reports are generated after successful processing.

## 9. Evaluation and Red-Team Testing

The project includes an evaluation harness and red-team testing scripts to examine extraction accuracy, handling of missing information, duplicate registrations and resistance to instructions embedded in registration messages.

## 10. Important Data Safety Rules

- Never invent missing participant information.
- Never silently correct phone numbers or email addresses.
- Preserve original registration messages.
- Do not treat guardian or emergency-contact details as participant details without explicit evidence.
- Flag uncertain information for human review.