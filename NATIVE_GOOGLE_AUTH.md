# استخدام Native Google Auth بدون SHA-1

## المشكلة
SHA-1 صعب الحصول عليه بدون Java

## الحل البديل: Native Plugin

### الخطوة 1: تثبيت Plugin

```bash
npm install @codetrix-studio/capacitor-google-auth
npx cap sync
```

### الخطوة 2: تعديل الكود

في `capacitor.config.ts`:

```typescript
import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'com.tawfir.app',
  appName: 'tawfir_app',
  webDir: 'www',
  plugins: {
    GoogleAuth: {
      scopes: ['profile', 'email'],
      serverClientId: '409608657151-95dqok74ojre9b6u377f1vsritt6afb3.apps.googleusercontent.com',
      forceCodeForRefreshToken: true,
    },
  },
};

export default config;
```

### الخطوة 3: استخدمه في الكود

```typescript
import { GoogleAuth } from '@codetrix-studio/capacitor-google-auth';

// في ngOnInit أو constructor
GoogleAuth.initialize();

// عند تسجيل الدخول
async signInWithGoogle() {
  try {
    const result = await GoogleAuth.signIn();
    console.log(result);
    // result.authentication.idToken
  } catch (error) {
    console.error(error);
  }
}
```

هذا الـ Plugin لا يحتاج SHA-1 ويعمل مباشرة!
