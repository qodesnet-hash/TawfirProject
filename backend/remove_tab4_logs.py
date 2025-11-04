import re

# Read the TypeScript file
file_path = r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app\tab4-merchant\tab4-merchant.page.ts'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Count before
count_before = len(re.findall(r'console\.log', content))
print(f"Found {count_before} console.log statements in tab4-merchant")

# Remove ALL console.log statements
content = re.sub(r'\s*console\.log\([^)]*\);\s*', '', content)

# Count after
count_after = len(re.findall(r'console\.log', content))
print(f"Remaining {count_after} console.log statements")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ تم حذف {count_before - count_after} console.log من tab4-merchant")
