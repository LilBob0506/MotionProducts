import pandas as pd

def get_single_entry(file_path):
    try:
        df = pd.read_excel(file_path, nrows=1)  # Read only the first row
        if "MFR_NAME" in df.columns and "Part Number" in df.columns:   # Check for MFR_NAME and Part Number
            entry = df.iloc[0][["MFR_NAME", "Part Number"]].values.tolist()
            return entry
        else:
            print("Required columns not found in the Excel file.")  # Error Handling
            return None
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

if __name__ == "__main__":
    excel_file = input("Enter the Excel file path: ")  #Input file path as ~/Directory/fileName.xlsx
    entry = get_single_entry(excel_file)
    if entry:
        print(f"First entry: {entry}")
    else:
        print("No valid entries found.")