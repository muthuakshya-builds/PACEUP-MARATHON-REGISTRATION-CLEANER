# PACEUP – Marathon Registration Cleaner
## 1. Problem Statement

Marathon registrations are often received through online forms and WhatsApp messages. These entries may contain inconsistent formatting, missing information, invalid contact details, repeated registrations and unstructured messages.

Manually checking every registration takes time and can lead to errors.

PACEUP aims to automate the extraction, cleaning and validation of marathon registration data.

## 2. Goal of the AI Tool

PACEUP is an AI-assisted marathon registration cleaning system that uses Google Gemini to extract participant information from original registration messages.

Python processes the extracted information, checks supporting evidence, validates fields, identifies duplicate or shared contact details and generates organised reports.

## 3. Input

**Input file:** `registrations.csv`

Each registration contains:
- Registration ID
- Original registration message
- Source of registration, such as an online form or WhatsApp

The messages may contain:
- Names
- Phone numbers
- Email addresses
- Ages
- Race categories
- Missing or inconsistent information
- Multiple participants in one registration

## 4. LLM

**Model:** Google Gemini

**System Prompt:** `system_prompt.txt`

The LLM extracts participant information and supporting evidence from the original message.

### Extracted fields

1. Name
2. Phone number
3. Email address
4. Age
5. Race category

## 5. PACEUP’S SIX CORE FEATURES
• Registration Evidence Tracker: retains the original entry, extracted values and field-level evidence checks; flags unsupported
extraction.
• Shared Contact Intelligence: detects phone/email details used by different people and flags possible family or guardian sharing
for human review.
• Cross-Entry Conflict Detective: finds likely same-participant records with conflicting names, contacts or race categories;
preserves both records.
• Race Eligibility Auditor: checks age against organiser-defined race-category limits and flags missing or potentially ineligible
registrations.
• Team Registration Completeness Checker: checks team submissions for missing member details and incomplete required
contact information.
• Smart Problem Prioritisation: groups issues by review priority so organisers can address identity conflicts, duplicate candidates
and incomplete or invalid records first.

## 6. Python Processing

Python performs the following operations:

- Reads registration entries.
- Checks extracted information against the original message.
- Cleans unnecessary spaces and formatting.
- Validates phone numbers and email addresses.
- Checks age and race category values.
- Identifies duplicate registrations.
- Flags shared contact details for human review.
- Assigns registration statuses.
- Generates reports.

## 7. Cleaning and Validation Rules

| Field | Rule |
|---|---|
| Name | Remove unnecessary spaces and standardise presentation |
| Phone | Validate the number without inventing or changing digits |
| Email | Convert to lowercase and validate its format; never repair it |
| Age | Accept a positive integer when supported by the source |
| Race category | Accept 5K, 10K, 21K and Kids Run |

Original registration messages and supporting evidence must be preserved.

## 8. Output Files

The application generates three reports:

### clean_list.csv
Contains participant registrations that pass the implemented validation checks.

### problems.csv
Contains entries requiring attention, including missing details, invalid fields, duplicates and shared-contact cases.

### summary.txt
Contains:
- Total registrations processed
- Valid registrations
- Registrations requiring fixes
- Duplicate registrations
- Category-wise participant counts

## 9. Constraints

1. Never invent missing participant information.
2. Never silently correct phone numbers or email addresses.
3. Preserve original registration messages.
4. Every extracted non-null field must have supporting evidence.
5. Guardian and emergency-contact details must not automatically become participant contact details.
6. Multiple participants must be extracted separately.
7. Instructions embedded in registration messages must not override the system prompt.
8. Uncertain entries must be flagged for human review.
9. No age eligibility decision will be made without official organiser-provided rules.

## 10. Edge Cases

- Missing participant name or contact details.
- Invalid phone number.
- Incorrect email format.
- Duplicate registrations.
- Multiple participants in one message.
- Guardian contact details.
- Conflicting information.
- Prompt injection attempts.
- Empty registration messages.
- Tanglish or informal registration messages.

## 11. Technology Stack

- Python
- Google Gemini API
- Streamlit
- Pandas
- Python-dotenv

## 12. Evaluation

The project will be tested using an evaluation harness and red-team testing.

Testing will examine:
- Correct information extraction.
- Handling of missing information.
- Preservation of original details.
- Resistance to prompt injection.
- Guardian-contact separation.
- Duplicate and misleading registration cases.

**Project Name:** PACEUP – Marathon Registration Cleaner

**Tagline:** Clean Registrations, Smoother Marathons.
