import os

# --- CONFIGURATION ---
# The folder containing your AI-generated summary files
CAPTIONS_FOLDER = "esa_summaries" 
# Your unique trigger word or phrase to add
TRIGGER_WORD = ", sat-art style"

def add_trigger_word_to_captions(directory, trigger):
    """
    Appends a trigger word to all .txt files in a directory.
    """
    print(f"Starting to add trigger word to files in: '{directory}'")
    
    # Get a list of all text files in the directory
    try:
        text_files = [f for f in os.listdir(directory) if f.endswith(".txt")]
        total_files = len(text_files)
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' was not found. Please check the folder name.")
        return

    for i, filename in enumerate(text_files):
        filepath = os.path.join(directory, filename)
        
        try:
            # Read the existing content of the file
            with open(filepath, 'r+') as f:
                content = f.read().strip()
                
                # Check if the trigger word is already there to avoid duplicates
                if not content.endswith(trigger):
                    # Move the cursor to the end of the file to append
                    f.seek(0, os.SEEK_END)
                    # Add the trigger word (preceded by a comma and space if needed)
                    f.write(trigger)
                    print(f"({i+1}/{total_files}) Added trigger word to {filename}")
                else:
                    print(f"({i+1}/{total_files}) Trigger word already exists in {filename}. Skipping.")

        except Exception as e:
            print(f"Could not process {filename}: {e}")

    print("\nProcessing complete!")

# --- Run the script ---
if __name__ == "__main__":
    add_trigger_word_to_captions(CAPTIONS_FOLDER, TRIGGER_WORD)