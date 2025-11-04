import re

# Read the TypeScript file
with open(r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app\tab1\tab1.page.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Count before
count_before = len(re.findall(r'console\.log', content))
print(f"Found {count_before} console.log statements")

# Remove ALL console.log statements (more aggressive)
content = re.sub(r'\s*console\.log\([^)]*\);\s*', '', content)

# Count after
count_after = len(re.findall(r'console\.log', content))
print(f"Remaining {count_after} console.log statements")

# Write back
with open(r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app\tab1\tab1.page.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ تم حذف {count_before - count_after} console.log")
