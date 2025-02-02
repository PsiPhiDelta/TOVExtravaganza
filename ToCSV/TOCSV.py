import os
import csv

def convert_txt_to_csv(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all .txt files in the input folder
    txt_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    
    for txt_file in txt_files:
        input_path = os.path.join(input_folder, txt_file)
        output_path = os.path.join(output_folder, txt_file.replace(".txt", ".csv"))
        
        with open(input_path, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
        
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            
            for line in lines:
                # Assuming space or tab separation; adjust as needed
                writer.writerow(line.strip().split())
        
        print(f"Converted {txt_file} to CSV.")

if __name__ == "__main__":
    input_folder = "inputCSC"
    output_folder = "outputCSC"
    convert_txt_to_csv(input_folder, output_folder)