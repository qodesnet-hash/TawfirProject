#!/usr/bin/env python
"""
Script to generate a new Django SECRET_KEY
Run this script and copy the output to your .env file
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    new_key = get_random_secret_key()
    print("\n" + "="*50)
    print("🔐 Your new SECRET_KEY:")
    print("="*50)
    print(new_key)
    print("="*50)
    print("\n✅ Copy this key and update it in your .env file")
    print("⚠️  NEVER commit this key to version control!")
    print("="*50 + "\n")
