
from pathlib import Path
import re

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

ALLOWED_CATEGORIES = ["5K", "10K", "21K", "Kids Run"]

st.set_page_config(
    page_title="PACEUP | Registration Cleaner",
    page_icon="🏃",
    layout="wide"
)


def make_field(value):
    """Keep the extracted value and its original evidence."""
    if value is None:
        return {"value": None, "evidence": None}

    value = value.strip()
    return {
        "value": value if value else None,
        "evidence": value if value else None
    }


def extract_value(pattern, text):
    """Extract the first value matching a labelled field."""
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip().rstrip(".") if match else None


def extract_name(text):
    patterns = [
        r"(?:Participant\s+name|Name)\s*:\s*([^,;\n]+)",
        r"(?:Team\s+leader|Leader|Member(?:\s+\d+)?|Participant(?:\s+\d+)?)\s*:\s*([^,;\n]+)",
        r"Registering myself\s*:\s*([^,;\n]+)",
        r"My name is\s+([^,;\n.]+)",
        r"I am\s+([^,;\n.]+)",
        r"this is\s+([^,;\n.]+)",
        r"register\s+([A-Z][A-Za-z. ]+?)\s+for\b",
    ]

    for pattern in patterns:
        value = extract_value(pattern, text)
        if value:
            value = re.sub(r"\s+from\s+.*$", "", value, flags=re.IGNORECASE)
            if value.casefold() not in ["not given", "missing"]:
                return value.strip()

    return None


def extract_age(text):
    age = extract_value(
        r"\bAge\s*:\s*(\d+|twenty one)\b",
        text
    )

    if age:
        return age

    match = re.search(r"\b(\d{1,2})\s+years?\b", text, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def extract_phone(text):
    match = re.search(
        r"(?<!\d)(\+91[\s-]?)?[6-9]\d(?:[\s-]?\d){8}(?!\d)",
        text
    )
    return match.group(0).strip() if match else None


def extract_email(text):
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )
    return match.group(0) if match else None


def extract_category(text):
    patterns = [
        r"(?:Race category|Category selected|Category|Race|run)\s*:\s*([^,;\n]+)",
        r"for\s+(Kids Run|Half Marathon(?:\s*\(21K\))?|21K|10K|5K)\b",
        r"for\s+the\s+(Kids Run|Half Marathon|21K|10K|5K)\b",
    ]

    for pattern in patterns:
        value = extract_value(pattern, text)
        if value:
            value = value.strip()
            if "half marathon" in value.casefold():
                return "21K"
            return value

    if re.search(r"Half Marathon", text, re.IGNORECASE):
        return "21K"

    return None


def split_participants(entry):
    """Separate clearly labelled team and family participants."""
    pattern = (
        r"(?=(?:Participant\s+\d+|Team\s+leader|Leader|"
        r"Member(?:\s+\d+)?)\s*:)"
    )

    parts = re.split(pattern, entry, flags=re.IGNORECASE)
    parts = [part.strip(" ,.;") for part in parts if part.strip(" ,.;")]

    return parts if parts else [entry]


def extract_registration(registration_id, entry):
    """Extract participant details using local Python rules only."""
    segments = split_participants(entry)
    participants = []

    for segment in segments:
        name = extract_name(segment)
        age = extract_age(segment)
        phone = extract_phone(segment)
        email = extract_email(segment)
        category = extract_category(segment)

        # Do not create a participant from a segment with no participant name.
        if not name:
            continue

        participants.append({
            "name": make_field(name),
            "phone": make_field(phone),
            "email": make_field(email),
            "age": make_field(age),
            "race_category": make_field(category),
        })

    return {"participants": participants}

def read_entry(row):
    """Return the registration ID and original message from a CSV row."""
    return str(row["id"]).strip(), str(row["entry"]).strip()



def get_field_value(participant, field):
    field_data = participant.get(field)
    if isinstance(field_data, dict):
        return field_data.get("value")
    return field_data


def get_field_evidence(participant, field):
    field_data = participant.get(field)
    return field_data.get("evidence") if isinstance(field_data, dict) else None


def check_facts(participant, original_entry):
    """Check that extracted values are supported by the original message."""
    problems = []
    original = str(original_entry).casefold()

    for field in ["name", "phone", "email", "age", "race_category"]:
        value = get_field_value(participant, field)
        evidence = get_field_evidence(participant, field)

        if value is None:
            continue

        if not evidence or str(evidence).casefold() not in original:
            problems.append(f"Evidence for {field} not found in original message")
            continue

        if str(value).casefold() not in str(evidence).casefold():
            problems.append(f"Extracted {field} does not match its evidence")

    return problems

def clean_name(name):
    if name is None:
        return None
    cleaned = " ".join(str(name).split())
    return cleaned.title() if cleaned else None



def clean_phone(phone):
    if phone is None:
        return None

    original = str(phone).strip()

    if original.startswith("+91"):
        original = original[3:].strip()

    digits = re.sub(r"[\s-]", "", original)

    if re.fullmatch(r"[6-9][0-9]{9}", digits):
        return digits

    return None


def clean_email(email):
    if email is None:
        return None

    value = str(email).strip().lower()
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return value if re.fullmatch(pattern, value) else None


def clean_age(age):
    if age is None:
        return None

    age_text = str(age).strip().casefold()

    if age_text == "twenty one":
        return 21

    try:
        value = int(age_text)
        return value if value > 0 else None
    except (ValueError, TypeError):
        return None


def clean_category(category):
    if category is None:
        return None
    value = str(category).strip()
    for allowed in ALLOWED_CATEGORIES:
        if value.casefold() == allowed.casefold():
            return allowed
    return None


def is_valid(participant):
    problems = []
    if not participant.get("name"):
        problems.append("Name missing or invalid")
    if not participant.get("phone"):
        problems.append("Phone missing or invalid")
    if not participant.get("email"):
        problems.append("Email missing or invalid")
    if participant.get("age") is None:
        problems.append("Age missing or invalid")
    if not participant.get("race_category"):
        problems.append("Race category missing or invalid")
    return problems


def find_duplicate(participant, previous_participants):
    phone = participant.get("phone")
    email = participant.get("email")
    for previous in previous_participants:
        same_phone = phone is not None and phone == previous.get("phone")
        same_email = email is not None and email == previous.get("email")
        if same_phone or same_email:
            same_name = (participant.get("name") or "").casefold() == (
                previous.get("name") or ""
            ).casefold()
            if same_name:
                return f"Possible duplicate of {previous.get('participant_id')}", "duplicate"
            return "Shared contact details detected; human review required", "needs_fix"
    return None, None


def clean(participant, registration_id, participant_id, original_entry):
    """Fact-check, clean and validate one extracted participant."""
    issues = check_facts(participant, original_entry)
    name = clean_name(get_field_value(participant, "name"))
    phone = clean_phone(get_field_value(participant, "phone"))
    email = clean_email(get_field_value(participant, "email"))
    age_value = get_field_value(participant, "age")
    age = clean_age(age_value)
    category_value = get_field_value(participant, "race_category")
    category = clean_category(category_value)

    if get_field_value(participant, "name") is not None and name is None:
        issues.append("Invalid name")
    if get_field_value(participant, "phone") is not None and phone is None:
        issues.append("Invalid phone number")
    if get_field_value(participant, "email") is not None and email is None:
        issues.append("Invalid email address")
    if age_value is not None and age is None:
        issues.append("Invalid age")
    if category_value is not None and category is None:
        issues.append("Unrecognised race category")

    record = {
        "registration_id": registration_id,
        "participant_id": participant_id,
        "name": name,
        "phone": phone,
        "email": email,
        "age": age,
        "race_category": category,
        "original_entry": original_entry,
    }
    issues.extend(is_valid(record))
    return record, issues

def read_entry(row):
    """Read registration ID and original message from CSV."""
    return str(row["id"]).strip(), str(row["entry"]).strip()

def process(df):
    clean_records = []
    problem_records = []
    previous_participants = []

    progress = st.progress(0)
    status_text = st.empty()
    total = len(df)

    for index, row in df.iterrows():
        registration_id, original_entry = read_entry(row)

        status_text.write(f"Processing registration {registration_id}...")

        extracted = extract_registration(registration_id, original_entry)
        participants = extracted.get("participants", [])

        if not participants:
            problem_records.append({
                "registration_id": registration_id,
                "participant_id": "",
                "name": "",
                "original_entry": original_entry,
                "status": "needs_fix",
                "problems": "Participant details could not be extracted automatically. Human review required."
            })

        for number, participant in enumerate(participants, start=1):
            participant_id = f"{registration_id}-{number}"

            record, issues = clean(
                participant,
                registration_id,
                participant_id,
                original_entry
            )

            duplicate_message, duplicate_status = find_duplicate(
                record,
                previous_participants
            )

            if duplicate_message:
                issues.append(duplicate_message)

            status = (
                "duplicate" if duplicate_status == "duplicate"
                else "needs_fix" if issues or duplicate_status == "needs_fix"
                else "valid"
            )

            record["status"] = status
            record["problems"] = "; ".join(issues)

            previous_participants.append(record)

            if status == "valid":
                clean_records.append(record)
            else:
                problem_records.append(record)

        progress.progress((index + 1) / total if total else 1.0)

    status_text.success("Registration processing completed!")

    return clean_records, problem_records

def process_registrations(df):
    """Compatibility wrapper for the registration-processing function."""
    return process(df)



def write_reports(clean_records, problem_records):
    """Generate the three PACEUP output reports."""

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    clean_path = OUTPUTS_DIR / "clean_list.csv"
    problems_path = OUTPUTS_DIR / "problems.csv"
    summary_path = OUTPUTS_DIR / "summary.txt"

    pd.DataFrame(clean_records).to_csv(clean_path, index=False)
    pd.DataFrame(problem_records).to_csv(problems_path, index=False)

    duplicate_count = sum(
        r.get("status") == "duplicate" for r in problem_records
    )

    needs_fix_count = sum(
        r.get("status") == "needs_fix" for r in problem_records
    )

    categories = {}

    for record in clean_records:
        category = record.get("race_category") or "Not specified"
        categories[category] = categories.get(category, 0) + 1

    lines = [
        "PACEUP - MARATHON REGISTRATION CLEANER",
        "=" * 42,
        "",
        f"Valid participants: {len(clean_records)}",
        f"Participants needing review: {needs_fix_count}",
        f"Possible duplicates: {duplicate_count}",
        f"Total participant records: {len(clean_records) + len(problem_records)}",
        "",
        "VALID PARTICIPANTS BY RACE CATEGORY",
    ]

    lines.extend(
        f"{category}: {count}"
        for category, count in sorted(categories.items())
    )

    lines.extend([
        "",
        "Eligibility was not assessed because official organiser age rules were not supplied."
    ])

    summary_path.write_text("\n".join(lines), encoding="utf-8")

    return clean_path, problems_path, summary_path


def main():
    st.title("🏃 PACEUP – Marathon Registration Cleaner")
    st.caption("Clean Registrations, Smoother Marathons")

    st.markdown(
        "PACEUP reads registration messages using Python, "
        "extracts participant details, checks information and "
        "generates reports for human review."
    )

    input_file = DATA_DIR / "registrations.csv"

    if not input_file.exists():
        st.error("registrations.csv not found inside the data folder.")
        return

    try:
        df = pd.read_csv(input_file)

        if not {"id", "entry"}.issubset(df.columns):
            st.error("CSV must contain columns named id and entry.")
            return

        st.success(f"{len(df)} registrations loaded.")
        st.dataframe(df.head(10), use_container_width=True)

        if st.button("Process Registrations", type="primary"):

            clean_records, problem_records = process(df)

            clean_path, problems_path, summary_path = write_reports(
                clean_records, problem_records
            )

            st.success("PACEUP processing completed!")

            col1, col2, col3 = st.columns(3)

            col1.metric("Valid participants", len(clean_records))

            col2.metric(
                "Needs review",
                sum(r.get("status") == "needs_fix" for r in problem_records)
            )

            col3.metric(
                "Possible duplicates",
                sum(r.get("status") == "duplicate" for r in problem_records)
            )

            st.subheader("Clean registrations")
            st.dataframe(
                pd.DataFrame(clean_records),
                use_container_width=True
            )

            st.subheader("Registrations needing attention")
            st.dataframe(
                pd.DataFrame(problem_records),
                use_container_width=True
            )

            st.subheader("Download reports")

            for path, label in [
                (clean_path, "Download clean_list.csv"),
                (problems_path, "Download problems.csv"),
                (summary_path, "Download summary.txt"),
            ]:
                st.download_button(
                    label=label,
                    data=path.read_bytes(),
                    file_name=path.name,
                )

    except Exception as error:
        st.error(f"Error processing file: {error}")


if __name__ == "__main__":
    main()
