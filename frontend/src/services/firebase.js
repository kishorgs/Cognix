// Simple Firebase initialization.
// Replace the config values below or set the corresponding REACT_APP_* env vars.
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || 'REPLACE_WITH_API_KEY',
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || 'REPLACE_WITH_AUTH_DOMAIN',
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || 'REPLACE_WITH_PROJECT_ID',
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || 'REPLACE_WITH_STORAGE_BUCKET',
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || 'REPLACE_WITH_MESSAGING_SENDER_ID',
  appId: process.env.REACT_APP_FIREBASE_APP_ID || 'REPLACE_WITH_APP_ID',
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// Note: For production, store credentials in environment variables or secret manager.
// Example .env (at project root):
// REACT_APP_FIREBASE_API_KEY=your_api_key
// REACT_APP_FIREBASE_AUTH_DOMAIN=your_auth_domain
// ...
