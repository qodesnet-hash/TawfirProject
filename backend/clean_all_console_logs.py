import os
import re

# Base path
base_path = r'C:\Users\mus_2\GitHub\TawfirProject\tawfir_app\src\app'

# Files to clean
files_to_clean = [
    'tab1/tab1.page.ts',
    'tab2/tab2.page.ts',
    'tab3/tab3.page.ts',
    'tab4-merchant/tab4-merchant.page.ts',
    'pages/merchant-detail/merchant-detail.page.ts',
    'pages/offer-detail/offer-detail.page.ts',
    'pages/add-review/add-review.page.ts',
]

total_removed = 0

for file_rel_path in files_to_clean:
    file_path = os.path.join(base_path, file_rel_path)
    
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_rel_path}")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        count_before = len(re.findall(r'console\.log', content))
        
        if count_before == 0:
            print(f"✓ {file_rel_path}: No console.log found")
            continue
        
        # Remove ALL console.log statements
        content = re.sub(r'\s*console\.log\([^)]*\);\s*', '', content)
        
        count_after = len(re.findall(r'console\.log', content))
        removed = count_before - count_after
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        total_removed += removed
        print(f"✅ {file_rel_path}: Removed {removed} console.log")
        
    except Exception as e:
        print(f"❌ Error processing {file_rel_path}: {e}")

print(f"\n🎉 Total removed: {total_removed} console.log statements")
