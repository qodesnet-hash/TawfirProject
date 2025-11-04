import re

# Read the TypeScript file
with open(r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app\tab1\tab1.page.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove only scroll-related console.log
output = []
skip_line = False

for i, line in enumerate(lines):
    # Check if this line contains scroll-related console.log
    if 'console.log' in line:
        lower_line = line.lower()
        # Only remove if it contains scroll-related keywords
        if any(keyword in lower_line for keyword in [
            'scroll', 'toolbar', 'delta', 'threshold', 'direction', 
            'position', 'state', 'hidden', 'visible', 'tab1', 'advanced',
            'sentinel', 'polling', 'native', 'event start', 'event end'
        ]):
            continue  # Skip this line
    
    output.append(line)

# Write back
with open(r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app\tab1\tab1.page.ts', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("✅ تم حذف console.log المتعلقة بالـ scroll فقط!")
