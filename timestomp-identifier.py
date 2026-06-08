import argparse
import subprocess
import os
import pandas as pd

def extract_mft(raw_mft_path, temp_csv):
    print(f"Phase 1: Parsing {raw_mft_path}")
    try:
        result = subprocess.run(
            ['analyzeMFT', '-f', raw_mft_path, '-o', temp_csv], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            shell=True 
        )
        
        if os.path.exists(temp_csv) and os.path.getsize(temp_csv) > 0:
            if "ERROR" in result.stderr or result.returncode != 0:
                print("Warning: analyzeMFT encountered corrupted/oversized MFT records.")
                print("The parser skipped the malformed sectors and salvaged the remaining timeline.")
            return True
        else:
            print(f"Fatal Error: analyzeMFT failed completely and produced no output.\nDetails: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Fatal Error during MFT parsing execution: {e}")
        return False

def detect_anomalies(temp_csv):
    print("Phase 2: Checking Timestamps and Detecting Anomalies...")
    
    try:
        df = pd.read_csv(temp_csv, low_memory=False, on_bad_lines='skip')
    except Exception as e:
        print(f"Fatal Error: Pandas could not read the CSV. Details: {e}")
        exit(1)
        
    actual_cols = df.columns.tolist()
    
    filename_col = 'Filename' if 'Filename' in actual_cols else 'Filename #1'
    si_col = next((col for col in actual_cols if 'SI Creation' in col or 'Std Info Creation' in col), None)
    fn_col = next((col for col in actual_cols if 'FN Creation' in col or 'FN Info Creation' in col), None)
    
    if not (filename_col in actual_cols and si_col and fn_col):
        print("\nError: Could not locate the exact SI/FN timestamp columns.")
        exit(1)
        
    # Isolate columns and create a safe copy
    df = df[[filename_col, si_col, fn_col]].copy()
    
    # Clean the raw strings
    purge_strings = ['No Data', 'nan', 'None', 'Not defined']
    df[si_col] = df[si_col].astype(str).replace(purge_strings, '', regex=True)
    df[fn_col] = df[fn_col].astype(str).replace(purge_strings, '', regex=True)
    
    df['SI'] = pd.to_datetime(df[si_col], format='mixed', errors='coerce')
    df['FN'] = pd.to_datetime(df[fn_col], format='mixed', errors='coerce')
    
    # Drop rows that are genuinely empty or corrupted
    df = df.dropna(subset=['SI', 'FN'])
    
    # Potential evidence of manipulation
    df['Is_Timestomped'] = df['SI'] < df['FN']
    
    print(f"Logical records analyzed: {len(df)}")
    print(f"Anomalies Flagged: {df['Is_Timestomped'].sum()}")
    
    # Standardize the output dataframe column name
    df = df.rename(columns={filename_col: 'Filename #1'})
    
    return df

def main():
    parser = argparse.ArgumentParser(description="Timestomp Identifier")
    parser.add_argument("-f", "--file", required=True, help="Path to the raw $MFT binary")
    parser.add_argument("--keep-csv", action="store_true", help="Do not delete the intermediate CSV file")
    args = parser.parse_args()

    temp_csv = "parsed_temp.csv"

    # Execute Pipeline
    if not extract_mft(args.file, temp_csv):
        exit(1)
        
    df = detect_anomalies(temp_csv)
    
    # Isolate and display only the manipulated artifacts
    anomalies = df[df['Is_Timestomped'] == True]
    
    print("\n==========================================")
    if anomalies.empty:
        print("NO TIMESTOMPING DETECTED.")
    else:
        print("POTENTIAL TIMESTOMPING DETECTED")
        print("==========================================")
        
        # Limit output to first 10
        for index, row in anomalies.head(10).iterrows():
            print(f"\nFile: {row['Filename #1']}")
            print(f"     SI Creation Date: {row['SI']}")
            print(f"     FN Creation Date:  {row['FN']}")
            
        if len(anomalies) > 10:
            print(f"\n...and {len(anomalies) - 10} more. Check the CSV for full details.")

    print("====================================================")

    # Cleanup
    if not args.keep_csv and os.path.exists(temp_csv):
        os.remove(temp_csv)
        print("\nTemporary files cleaned.")

if __name__ == "__main__":
    main()