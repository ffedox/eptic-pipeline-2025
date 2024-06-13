import pandas as pd
import re
import glob
import os
from xml.etree import ElementTree as ET
from lxml import etree

# Directory paths
input_folder_path = '/home/afedotova/bertalign/temp'
output_folder_path = '/home/afedotova/bertalign/pretgd3'

# Load the provided Excel files (adjust these paths as needed)
texts_file_path = '/home/afedotova/bertalign/database/texts.xlsx'
events_file_path = '/home/afedotova/bertalign/database/events.xlsx'
speakers_file_path = '/home/afedotova/bertalign/database/speakers.xlsx'
interpreters_file_path = '/home/afedotova/bertalign/database/interpreters.xlsx'

# Load supporting data
texts_df = pd.read_excel(texts_file_path)
events_df = pd.read_excel(events_file_path)
speakers_df = pd.read_excel(speakers_file_path)
interpreters_df = pd.read_excel(interpreters_file_path)

# Ensure the renaming logic is correctly applied
# Adjust DataFrame columns to match expected keys
for df in [texts_df, events_df, speakers_df, interpreters_df]:
    df.columns = [col.replace(".", "_").lower().replace(" ", "_") for col in df.columns]

# Define full names for languages
language_full_names = {
    "DE": "German", "EN": "English", "FR": "French",
    "IT": "Italian", "PL": "Polish", "FI": "Finnish", "SL": "Slovenian"
}

# Define possible combinations
combinations = {
    "TT SP": "interpretations", "TT WR": "translations",
    "ST SP": "spoken sources", "ST WR": "written sources"
}

# Generate exhaustive type mapping
type_mapping = {}
for lang_code, lang_full in language_full_names.items():
    for combo, combo_full in combinations.items():
        key = f"{lang_code} {combo}"
        value = f"{lang_full} {combo_full}"
        type_mapping[key] = value

def map_type_value(type_key):
    # Attempt to map the type_key directly
    mapped_value = type_mapping.get(type_key)
    if not mapped_value:
        print(f"Mapping not found for: {type_key}")  # Debug message
    return mapped_value or type_key

def na_if_nan(value):
    """Returns 'NA' if value is NaN or None, otherwise returns the value itself."""
    if pd.isna(value):
        return "NA"
    return value

def preprocess_xml(xml_str):
    """
    Preprocesses the XML string by removing the Byte Order Mark (BOM) if present and trimming leading whitespace.
    """
    # Remove UTF-8 BOM if present
    xml_str = xml_str.lstrip('\ufeff')
    # Strip leading whitespace characters
    xml_str = xml_str.lstrip()
    return xml_str

def parse_xml_s_tags(xml_str, video_url=None):
    xml_str_cleaned = preprocess_xml(xml_str)
    
    try:
        # Parse the cleaned XML string directly using lxml
        root = etree.fromstring(xml_str_cleaned.encode('utf-8'))
        s_elements = root.findall(".//s")
        return [{"id": s.get("id"), "text": s.text} for s in s_elements]
    except etree.XMLSyntaxError as e:
        # Print the problematic XML string for inspection along with the error
        print(f"XML parsing error using lxml: {e}\nProblematic XML content:\n{xml_str}")
        return []

def match_subtitles_with_timestamps(subtitled_text, s_tags, video_url, text_id):
    # Parse subtitled text to get timestamps
    subtitle_parts = subtitled_text.strip().split("\n\n")
    timestamps = []
    for part in subtitle_parts:
        lines = part.split("\n")
        if len(lines) >= 3:
            timestamp_line = lines[1]
            start, end = re.findall(r"(\d{2}:\d{2}:\d{2}),\d+", timestamp_line)
            timestamps.append({"start": start, "end": end})
    
    # Ensure we have the same number of s_tags and timestamps
    if len(s_tags) != len(timestamps):
        raise ValueError(f"Mismatch in {text_id}: s_tags ({len(s_tags)}) and subtitle timestamps ({len(timestamps)}).")
    
    # Match s_tags with timestamps based on order
    matched_s_tags = []
    for s_tag, timestamp in zip(s_tags, timestamps):
        matched_s_tags.append({
            "id": s_tag["id"],
            "text": s_tag["text"],
            "start": timestamp["start"].replace(":", "."),
            "end": timestamp["end"].replace(":", "."),
            "video_url": video_url
        })

    return matched_s_tags

def create_vert_structure(text_id, texts_df, events_df, speakers_df, interpreters_df):
    text_row = texts_df[texts_df["texts_id"] == text_id].iloc[0]
    # Check for NaN values in critical fields
    if pd.isna(text_row["texts_duration"]) or pd.isna(text_row["texts_word_count"]):
        return None  # Skip this record
    
    # Proceed with processing if no critical NaN values are found
    event_row = events_df[events_df["events_id"] == text_row["texts_event_id"]].iloc[0]
    if event_row.empty:
        return None  # Skip if the event row is missing
    
    speaker_row = speakers_df[speakers_df["speakers_id"] == event_row["events_speaker_id"]].iloc[0]
    if speaker_row.empty:
        return None  # Skip if the speaker row is missing
    
    interpreter_id = text_row["texts_interpreter_id"]
    interpreter_row = interpreters_df[interpreters_df["interpreters_id"] == interpreter_id] if pd.notnull(interpreter_id) else pd.DataFrame()
    
    # Finding the related WR and ST row for the event
    related_text_row = texts_df[(texts_df["texts_event_id"] == text_row["texts_event_id"]) & 
                                (texts_df["texts_spoken_written"] == "WR") & 
                                (texts_df["texts_source_target"] == "ST")].iloc[0] if not texts_df[(texts_df["texts_event_id"] == text_row["texts_event_id"]) & 
                                (texts_df["texts_spoken_written"] == "WR") & 
                                (texts_df["texts_source_target"] == "ST")].empty else None

    if related_text_row is not None:
        st_language = related_text_row["texts_lang"]
        st_lengthw = related_text_row["texts_word_count"]
        st_length = "short" if 100 <= st_lengthw <= 400 else "medium" if 401 <= st_lengthw <= 1000 else "long"
        st_durations = related_text_row["texts_duration"]
        st_duration = "short" if st_durations < 120 else "medium" if 120 <= st_durations <= 360 else "long"
        st_speedwm = round(st_lengthw / (st_durations / 60), 1) if st_durations > 0 else 0
        st_speed = "slow" if st_speedwm < 130 else "medium" if 130 <= st_speedwm <= 160 else "high"
        st_delivery = event_row["events_delivery"]
    else:
        st_language = "NA"
        st_lengthw = "NA"
        st_length = "NA"
        st_durations = "NA"
        st_duration = "NA"
        st_speedwm = "NA"
        st_speed = "NA"
        st_delivery = "NA"

    s_tags = parse_xml_s_tags(text_row["texts_sentence_split_text"])
    
    type_key = f"{text_row['texts_lang'].upper()} {text_row['texts_source_target']} {text_row['texts_spoken_written']}"
    type_value = map_type_value(type_key)
    
    word_count = text_row["texts_word_count"]
    durations = round(float(text_row["texts_duration"]), 0)
    length_category = "short" if 100 <= word_count <= 400 else "medium" if 401 <= word_count <= 1000 else "long"
    duration_category = "short" if durations < 120 else "medium" if 120 <= durations <= 360 else "long"
    words_per_minute = round(word_count / (durations / 60), 1)
    speed_category = "slow" if words_per_minute < 130 else "medium" if 130 <= words_per_minute <= 160 else "high"
    
    event_date_str = "NA" if pd.isna(event_row["events_date"]) else event_row["events_date"].strftime("%Y-%m-%d")
    vert_string = f'<text id="{text_id}" date="{event_date_str}" length="{na_if_nan(length_category)}" lengthw="{na_if_nan(text_row["texts_word_count"])}" duration="{na_if_nan(duration_category)}" durations="{na_if_nan(round(float(text_row["texts_duration"]), 0))}" speed="{na_if_nan(speed_category)}" speedwm="{na_if_nan(words_per_minute)}" delivery="{na_if_nan(event_row["events_delivery"])}" topic="{na_if_nan(event_row["events_topic"])}" topicspec="{na_if_nan(event_row["events_topic_specific"])}" type="{na_if_nan(type_value)}" comments="NA">\n'
    vert_string += f'<speaker name="{na_if_nan(speaker_row["speakers_full_name"])}" gender="{na_if_nan(speaker_row["speakers_gender"])}" country="{na_if_nan(speaker_row["speakers_country"])}" politfunc="{na_if_nan(speaker_row["speakers_political_function"])}" politgroup="{na_if_nan(speaker_row["speakers_political_group"])}">\n'
    vert_string += f'<st language="{na_if_nan(st_language)}" length="{na_if_nan(st_length)}" lengthw="{na_if_nan(st_lengthw)}" duration="{na_if_nan(st_duration)}" durations="{na_if_nan(st_durations)}" speed="{na_if_nan(st_speed)}" speedwm="{na_if_nan(st_speedwm)}" delivery="{na_if_nan(st_delivery)}">\n'
    
    # Check if an interpreter ID is present and fetch the corresponding row
    if pd.notnull(text_row["texts_interpreter_id"]):
        interpreter_row = interpreters_df[interpreters_df["interpreters_id"] == text_row["texts_interpreter_id"]]
        interpreter_present = not interpreter_row.empty
    else:
        interpreter_present = False

    if interpreter_present:
        # If interpreter_row is not empty, meaning there's an interpreter
        interpreter_tag = f'<interpreter id="{na_if_nan(interpreter_row.iloc[0]["interpreters_nickname"])}" gender="{na_if_nan(interpreter_row.iloc[0]["interpreters_gender"])}" native="{na_if_nan(interpreter_row.iloc[0].get("interpreters_native", "NA"))}">\n'
    else:
        # If there's no interpreter assigned, include a placeholder or simplified tag
        interpreter_tag = '<interpreter id="NA" gender="NA" native="NA">\n'

    # Include the interpreter_tag when constructing the vert_string
    vert_string += interpreter_tag

    s_tags = parse_xml_s_tags(text_row["texts_sentence_split_text"])
    if text_row["texts_spoken_written"] == "SP" and pd.notnull(text_row["texts_subtitled_text"]) and pd.notnull(text_row["texts_video_url"]):
        try:
            # Assuming your code here calls match_subtitles_with_timestamps at some point
            s_tags = match_subtitles_with_timestamps(text_row["texts_subtitled_text"], s_tags, text_row["texts_video_url"], text_id)
        except ValueError as e:
            print(e)
            video_url = "ERR" 

    for s_tag in s_tags:
        video_attr = f' video="{s_tag["video_url"]}&start={s_tag["start"]}&end={s_tag["end"]}"' if "video_url" in s_tag else ""
        vert_string += f'<s id="{s_tag["id"]}"{video_attr}>\n{s_tag["text"]}\n</s>\n'

    # Ensure to append '</st>\n</speaker>\n</text>\n' after adding the interpreter tag
    vert_string += '</interpreter>\n</st>\n</speaker>\n</text>'
    return vert_string

def process_excel_files_in_directory(input_folder_path, output_folder_path):
    ensure_directory_exists(output_folder_path)  # Ensure the output directory exists
    for excel_file_name in os.listdir(input_folder_path):
        if excel_file_name.endswith('.xlsx'):
            excel_file_path = os.path.join(input_folder_path, excel_file_name)
            ids_df = pd.read_excel(excel_file_path)
            # Adjust 'id' to match the actual column name in your Excel files
            text_ids = ids_df['texts.id'].dropna().astype(int).tolist()
            aggregated_content = []

            for text_id in text_ids:
                vert_content = create_vert_structure(text_id, texts_df, events_df, speakers_df, interpreters_df)
                if vert_content:  # Add content to the aggregated list if generated
                    aggregated_content.append(vert_content)
            
            if aggregated_content:  # Check if there's any content to write
                output_file_path = os.path.join(output_folder_path, f"{excel_file_name.replace('.xlsx', '.pretgd')}")
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    file.write("\n".join(aggregated_content))
                    print(f"Generated .pretgd file from {excel_file_name} with aggregated content")

def ensure_directory_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

process_excel_files_in_directory(input_folder_path, output_folder_path)