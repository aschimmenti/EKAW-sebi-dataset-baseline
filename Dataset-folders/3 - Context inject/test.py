def normalize(text):
    return text.replace('.', '').lower()

def is_abbreviation_or_part_of(abbreviation, full_name):
    abbr_normalized = normalize(abbreviation)
    full_name_normalized = normalize(full_name)
    abbr_parts = abbr_normalized.split()
    full_name_parts = full_name_normalized.split()

    # Check if each part of the abbreviation matches the corresponding part of the full name
    if len(abbr_parts) > 1:
        if len(abbr_parts) > len(full_name_parts):
            return False
        return all(
            abbr_parts[i] == full_name_parts[i][0] or abbr_parts[i] == full_name_parts[i]
            for i in range(len(abbr_parts))
        )
    
    # For single part abbreviations
    if len(abbr_parts) == 1:
        return any(
            abbr_parts[0] == full_name_part[0] or abbr_parts[0] == full_name_part
            for full_name_part in full_name_parts
        )

    return False

# Test cases
test_cases = [
    ("Ali", "Caliphs", False),
    ("J. Grimm", "Jacob Grimm", True),
    ("Alighieri", "Dante Alighieri", True)
]

for abbreviation, full_name, expected in test_cases:
    result = is_abbreviation_or_part_of(abbreviation, full_name)
    print(f"Abbreviation: '{abbreviation}', Full Name: '{full_name}', Result: {result}, Expected: {expected}")
