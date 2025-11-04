import re

# Read the file
file_path = r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app\tab1\tab1.page.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all console.log statements
content = re.sub(r'\s*console\.log\([^;]*\);?\s*', '', content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ تم حذف جميع console.log من tab1.page.ts")
