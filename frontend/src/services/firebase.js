import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  GoogleAuthProvider, 
  PhoneAuthProvider,
  RecaptchaVerifier
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyChdLYqbQuzIEhZFv0o2LRY3l2tSN9LPLA",
  authDomain: "cognix-25436.firebaseapp.com",
  projectId: "cognix-25436",
  storageBucket: "cognix-25436.appspot.com",
  messagingSenderId: "879124327677",
  appId: "1:879124327677:web:b4453e07e8b9baee06a294"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Helper to setup reCAPTCHA verifier for phone auth
export const setupRecaptcha = (containerId) => {
  try {
    // Clear any existing instances
    if (window.recaptchaVerifier) {
      window.recaptchaVerifier.clear();
      window.recaptchaVerifier = null;
    }

    // Create new instance
    const recaptchaVerifier = new RecaptchaVerifier(auth, containerId, {
      size: 'normal',
      callback: (response) => {
        console.log('reCAPTCHA solved with response:', response);
        // Enable your submit button here if needed
      },
      'expired-callback': () => {
        console.log('reCAPTCHA expired');
        // Handle expiration - maybe show a message to refresh
        if (window.recaptchaVerifier) {
          window.recaptchaVerifier.clear();
          window.recaptchaVerifier = null;
        }
        setupRecaptcha(containerId); // Reset the widget
      }
    });
    
    // Render the reCAPTCHA widget
    recaptchaVerifier.render().then(() => {
      console.log('reCAPTCHA rendered successfully');
      window.recaptchaVerifier = recaptchaVerifier;
    });
    
    return recaptchaVerifier;
  } catch (error) {
    console.error('reCAPTCHA setup error:', error);
    throw new Error(`Failed to initialize reCAPTCHA: ${error.message}`);
  }
};
