import pandas as pd
from itertools import combinations
import os
from zipfile import ZipFile

def generate_combinations(input_file):
    # Load the dataset
    df = pd.read_excel(input_file)

    # Filter relevant columns
    relevant_columns = df[['texts.id', 'texts.event_id', 'texts.lang', 'texts.source_target', 'texts.spoken_written']]

    # Prepare a list to hold all valid combinations
    valid_combinations = []

    # Generate combinations of texts.id within each event_id having different groupings
    for _, event_group in relevant_columns.groupby('texts.event_id'):
        for combo in combinations(event_group.iterrows(), 2):
            _, item_1_details = combo[0]
            _, item_2_details = combo[1]

            # Creating tuples for sorting
            item_1_tuple = (item_1_details['texts.lang'], item_1_details['texts.source_target'], item_1_details['texts.spoken_written'], item_1_details['texts.id'])
            item_2_tuple = (item_2_details['texts.lang'], item_2_details['texts.source_target'], item_2_details['texts.spoken_written'], item_2_details['texts.id'])

            # Sort based on language, source_target, and spoken_written to determine correct file name and order of ids
            sorted_items = sorted([item_1_tuple, item_2_tuple])

            # Extracting ids after sorting ensures they are in the correct order
            first_id = sorted_items[0][3]
            second_id = sorted_items[1][3]

            grouping = f"{sorted_items[0][0]}_{sorted_items[0][1]}_{sorted_items[0][2]}__{sorted_items[1][0]}_{sorted_items[1][1]}_{sorted_items[1][2]}"

            valid_combinations.append({
                'first_id': first_id,
                'second_id': second_id,
                'grouping': grouping
            })

    # Convert to DataFrame
    combinations_df = pd.DataFrame(valid_combinations)

    # Output directory for Excel files
    output_dir = "text_combinations"
    os.makedirs(output_dir, exist_ok=True)

    # Export combinations to Excel based on their unique, sorted grouping
    for grouping, group_df in combinations_df.groupby('grouping'):
        filename = f"{grouping}.xlsx"
        filepath = os.path.join(output_dir, filename)
        group_df[['first_id', 'second_id']].to_excel(filepath, index=False)

    # Zip all the Excel files
    zip_filename = "text_combinations.zip"
    with ZipFile(zip_filename, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(output_dir):
            for filename in filenames:
                zipf.write(os.path.join(foldername, filename),
                           os.path.relpath(os.path.join(foldername, filename), output_dir))

    print(f"Process completed. Files are zipped in: {zip_filename}")

# Replace 'your_input_file.xlsx' with the path to your actual input Excel file
generate_combinations(r'E:\Code\eptic\data\final\texts.xlsx')
