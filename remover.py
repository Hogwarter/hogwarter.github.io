def filter_lines_by_label(input_file, output_file, label):
    """
    Filters lines from a file based on the specified label.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output text file.
        label (str): The label to retain.
    """
    try:
        with open(input_file, 'r') as infile:
            lines = infile.readlines()

        with open(output_file, 'w') as outfile:
            for line in lines:
                # Check if the line ends with the desired label
                if line.split()[2] == label:
                    outfile.write(line)
        
        print(f"Lines labeled with '{label}' have been retained in '{output_file}'.")
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example Usage
input_file_path = "wordfreq_copy.txt"
output_file_path = "wordfreq_nouns.txt"
label_to_retain = "n"  # Replace with the label you want to keep.

filter_lines_by_label(input_file_path, output_file_path, label_to_retain)


if __name__ == "main":
    filter_lines_by_label(input_file_path, output_file_path, label_to_retain)
    