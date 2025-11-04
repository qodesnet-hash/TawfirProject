#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

file_path = r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app\tab1\tab1.page.ts'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Count console.log before
count_before = len(re.findall(r'console\.log', content))
print(f"Found {count_before} console.log statements")

# Remove all console.log lines (including multi-line)
content = re.sub(r'\s*console\.log\([^)]*\);\s*\n?', '', content)

# Count after
count_after = len(re.findall(r'console\.log', content))
print(f"Remaining: {count_after} console.log statements")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Removed {count_before - count_after} console.log statements from tab1.page.ts")
