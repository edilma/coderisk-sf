import pandas as pd
from pathlib import Path

# Load the data
df = pd.read_csv('results_folder/bocaraton/tables/boca_JustFOIA_Request_2024-9180-30p.csv')
df['city'] = 'bocaraton'

# Find descriptions
desc_mask = df['Main Address'].astype(str).str.contains('Description:', case=False, na=False)
descriptions = df[desc_mask].copy()

print(f'Found {len(descriptions)} descriptions')

# Create output directory
output_dir = Path('results_folder/boca_descriptions_extracted')
output_dir.mkdir(exist_ok=True)

# Save to CSV
descriptions.to_csv(output_dir / 'boca_descriptions.csv', index=False)

# Save readable text file
with open(output_dir / 'boca_descriptions_readable.txt', 'w', encoding='utf-8') as f:
    for i, row in descriptions.iterrows():
        main_addr = row['Main Address']
        source = row['source_file']
        f.write(f'Row {i}: {main_addr}\n')
        f.write(f'Source: {source}\n')
        f.write('-' * 80 + '\n\n')

print(f'Files saved to: {output_dir}')
print('Created:')
print('  - boca_descriptions.csv')
print('  - boca_descriptions_readable.txt')