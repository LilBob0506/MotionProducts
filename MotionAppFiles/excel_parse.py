import pandas as pd

def get_entries(file_path, num_entries=10):
    try:
        df = pd.read_excel(file_path, nrows=num_entries)
        if "MFR_NAME" in df.columns and "Part Number" in df.columns:
            # Convert each row to a tuple (manufacturer, part_number)
            entries = [tuple(row) for row in df[["MFR_NAME", "Part Number"]].dropna().values]
            return entries
        else:
            print("Required columns not found in the Excel file.")
            return []
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

if __name__ == "__main__":
    excel_file = input("Enter the Excel file path: ")  #Input file path as ~/Directory/fileName.xlsx
    entry = get_entries(excel_file)
    if entry:
        print(f"First entry: {entry}")
    else:
        print("No valid entries found.")
