import csv
import re

def parse_gen_file(input_filepath, output_filepath):
    """
    Parses a .gen file, extracts data, and writes it to a CSV file.
    """
    records = []
    all_fieldnames = {'strand', 'gene'}
    limits = ""

    with open(input_filepath, 'r') as f:
        lines = f.readlines()

    at_start_of_file = True
    current_strand = None
    current_record = None
    in_gene_block = False

    for line in lines:
        # 1. Ignore all text behind the "//" qualifier
        line = line.split('//')[0].strip()

        if not line:
            continue

        # 2. Append all text at the start of the file which begins with the # character to a field called limits.
        if at_start_of_file and line.startswith('#'):
            limits += line[1:].strip() + '\n'
            continue

        # Any other line means we are no longer at the start
        if line and not line.startswith('#'):
            at_start_of_file = False

        # 3. Find strand
        if line.startswith("strand"):
            parts = line.split()
            if len(parts) > 1:
                current_strand = parts[1]
            continue

        # 4. Find gene
        if line.startswith("gene"):
            # A new gene marks a new record
            parts = line.split()
            gene_data = "".join(parts[1:3])
            current_record = {
                "strand": current_strand,
                "gene": gene_data,
            }
            records.append(current_record)
            in_gene_block = False # Reset and wait for '{'
            continue

        # 5. Ignore "{" and start parsing key-value pairs
        if line == "{":
            if current_record is not None:
                in_gene_block = True
            continue

        # 6. Ignore "}" and stop parsing key-value pairs
        if line == "}":
            in_gene_block = False
            current_record = None # This gene block is done
            continue

        # 7. Parse key-value pairs
        if in_gene_block and current_record is not None and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            current_record[key] = value
            all_fieldnames.add(key)
            continue

    # Write to CSV
    # We need to get all fieldnames in a consistent order
    # Putting strand and gene first for readability
    other_fields = sorted(list(all_fieldnames - {'strand', 'gene'}))
    sorted_fieldnames = ['strand', 'gene'] + other_fields

    with open(output_filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted_fieldnames, extrasaction='ignore')

        writer.writeheader()
        writer.writerows(records)

    # Handle the limits data.
    # Creating a separate file for it as it doesn't fit well in a CSV row.
    if limits:
        with open('limits.txt', 'w') as f:
            f.write(limits)


if __name__ == "__main__":
    parse_gen_file("input.txt", "output.csv")
    print("Parsing complete. Output written to output.csv")
    import os
    if os.path.exists('limits.txt'):
        print("Limits data written to limits.txt")
