def extract_confused_blocks(filename):
    """Extract blocks between ###CONFUSED### and ###ENDCONFUSED### from a file."""
    blocks = []
    inside_block = False
    current_block = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if '###CONFUSED###' in line:
                    inside_block = True
                    current_block = []
                    # If there's content after the marker on the same line, capture it
                    if line.strip() != '###CONFUSED###':
                        content = line.split('###CONFUSED###')[1]
                        if content.strip():
                            current_block.append(content)
                elif '###ENDCONFUSED###' in line:
                    inside_block = False
                    # If there's content before the marker on the same line, capture it
                    if line.strip() != '###ENDCONFUSED###':
                        content = line.split('###ENDCONFUSED###')[0]
                        if content.strip():
                            current_block.append(content)
                    # Add the completed block to our list of blocks
                    blocks.append(''.join(current_block))
                elif inside_block:
                    current_block.append(line)
    except FileNotFoundError:
        print(f"Warning: File {filename} not found.")
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
    
    return blocks

def main():
    # Input files
    input_files = ['2490-out', '2497-out', '2499-out']
    # Output file
    output_file = 'combined_confused_blocks.txt'
    
    all_blocks = []
    
    # Process each input file
    for filename in input_files:
        blocks = extract_confused_blocks(filename)
        if blocks:
            all_blocks.extend(blocks)
            print(f"Extracted {len(blocks)} block(s) from {filename}")
        else:
            print(f"No blocks found in {filename}")
    
    # Write all blocks to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i, block in enumerate(all_blocks):
                outfile.write(f"Block {i+1} from input files:\n")
                outfile.write("###CONFUSED###\n")
                outfile.write(block)
                outfile.write("###ENDCONFUSED###\n\n")
        
        print(f"Successfully wrote {len(all_blocks)} block(s) to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()