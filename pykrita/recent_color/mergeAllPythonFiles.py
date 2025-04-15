import os
import glob

def combine_py_files():
    # Ottieni il nome dello script corrente
    current_script = os.path.basename(__file__)
    output_filename = "combined_files.py"
    
    # Trova tutti i file .py nella cartella corrente
    py_files = glob.glob("*.py")
    
    # Filtra escludendo lo script corrente e il file di output
    selected_files = [
        f for f in py_files
        if os.path.basename(f) not in [current_script, output_filename]
    ]
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for i, file_path in enumerate(selected_files):
            filename = os.path.basename(file_path)
            
            # Crea il separatore
            if i == 0:
                separator = f"### START OF FILE: {filename} ###\n\n"
            else:
                separator = f"\n\n### START OF FILE: {filename} ###\n\n"
            
            outfile.write(separator)
            
            # Copia il contenuto del file
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
        
        outfile.write("\n")  # Newline finale
    
    print(f"Uniti {len(selected_files)} file in {output_filename}")

if __name__ == "__main__":
    combine_py_files()