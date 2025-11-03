import React, { useState } from 'react';
import { PhoneAuthProvider, signInWithCredential, signInWithPopup, signInWithPhoneNumber } from 'firebase/auth';
import { auth, googleProvider, setupRecaptcha } from '../services/firebase';
import EmailPasswordForm from './EmailPasswordForm';
import PhoneAuthForm from './PhoneAuthForm';

export default function AuthMethods({ onSuccess, onError, mode = 'register' }) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [verificationId, setVerificationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPhoneAuth, setShowPhoneAuth] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const toggleAuthMethod = () => {
    setShowPhoneAuth(!showPhoneAuth);
    // Reset states when toggling
    setPhoneNumber('');
    setVerificationCode('');
    setVerificationId(null);
    setEmail('');
    setPassword('');
    // Clear any existing reCAPTCHA
    if (window.recaptchaVerifier) {
      window.recaptchaVerifier.clear();
      window.recaptchaVerifier = null;
    }
  };

  const handleEmailPasswordSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      onError('Please fill in all fields');
      return;
    }
    try {
      setLoading(true);
      // Here you would handle email/password auth
      // For now, just show an error
      onError('Email/password authentication not implemented yet');
    } catch (error) {
      onError(error?.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    try {
      setLoading(true);
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      onSuccess(token);
    } catch (error) {
      onError(error?.message || 'Google authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePhoneNumberSubmit = async () => {
    if (!phoneNumber) return onError('Please enter your phone number');
    if (phoneNumber.length !== 10) return onError('Please enter a valid 10-digit phone number');
    
    try {
      setLoading(true);
      // Format the phone number to E.164 format for India (+91)
      const e164Phone = `+91${phoneNumber}`;

      // Get existing reCAPTCHA verifier or create a new one
      let recaptchaVerifier = window.recaptchaVerifier;
      if (!recaptchaVerifier) {
        recaptchaVerifier = setupRecaptcha('recaptcha-container');
        window.recaptchaVerifier = recaptchaVerifier;
      }

      // Attempt phone number verification
      const confirmationResult = await signInWithPhoneNumber(
        auth,
        e164Phone,
        recaptchaVerifier
      );
      setVerificationId(confirmationResult.verificationId);
      onError(null); // Clear any previous errors
      
      // Reset reCAPTCHA for next use
      if (window.recaptchaVerifier) {
        window.recaptchaVerifier.clear();
        window.recaptchaVerifier = null;
      }
    } catch (error) {
      console.error('Phone auth error:', error);
      onError('Failed to send verification code. Please try again and make sure to complete the reCAPTCHA.');
      
      // Reset reCAPTCHA on error
      if (window.recaptchaVerifier) {
        window.recaptchaVerifier.clear();
        window.recaptchaVerifier = null;
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationCodeSubmit = async () => {
    if (!verificationCode) return onError('Please enter verification code');

    try {
      setLoading(true);
      const credential = PhoneAuthProvider.credential(verificationId, verificationCode);
      const result = await signInWithCredential(auth, credential);
      const token = await result.user.getIdToken();
      onSuccess(token);
    } catch (error) {
      onError(error?.message || 'Invalid verification code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg space-y-6">
      <div className="flex items-center justify-center space-x-4 mb-6">
        <div className="h-px flex-1 bg-gray-200"></div>
        <span className="text-sm font-medium text-gray-500">
          Continue with
        </span>
        <div className="h-px flex-1 bg-gray-200"></div>
      </div>

      <div className="space-y-4">
        <button
          onClick={handleGoogleAuth}
          disabled={loading}
          className="w-full px-6 py-3 text-base font-medium text-gray-700 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200 ease-in-out transform hover:scale-[1.02] active:scale-[0.98]"
        >
          <div className="flex items-center justify-center">
            <svg className="w-6 h-6 mr-3" viewBox="0 0 24 24">
              <path
                fill="#EA4335"
                d="M12.1 6.9c2 0 3.8.7 5.2 2l4-4A11.9 11.9 0 0012.1 0 12 12 0 001.8 6.4l4.7 3.6c1-3 4-5.1 7.4-5.1z"
              />
              <path
                fill="#4285F4"
                d="M23.5 12.2c0-1-.1-1.9-.3-2.8h-11v5.3H18a5.5 5.5 0 01-2.4 3.6l4.6 3.6c2.7-2.5 4.3-6.2 4.3-10.5z"
              />
              <path
                fill="#FBBC05"
                d="M6.5 14.3a7.3 7.3 0 010-4.7L1.8 6.4A12 12 0 000 12c0 2 .5 3.9 1.3 5.6l4.7-3.6c.3-.6.4-1.2.4-1.9z"
              />
              <path
                fill="#34A853"
                d="M12.1 24c3.2 0 6-1 8-3l-4.6-3.6c-1.3.9-3 1.4-4.7 1.4-3.5 0-6.4-2.3-7.4-5.4L1.3 17.6A12 12 0 0012 24z"
              />
            </svg>
            Continue with Google
          </div>
        </button>

        <div className="mt-8 bg-gray-50 p-6 rounded-xl border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Phone Verification</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">+91</span>
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="Enter your number (e.g., 8748067523)"
                  className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                />
              </div>
              <p className="mt-2 text-sm text-gray-500 flex items-center">
                <svg className="w-4 h-4 mr-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Enter 10-digit number without +91
              </p>
            </div>

            {/* reCAPTCHA container with better styling */}
            <div id="recaptcha-container" className="flex justify-center p-3 bg-white rounded-lg shadow-sm"></div>

            {!verificationId ? (
              <button
                onClick={handlePhoneNumberSubmit}
                disabled={loading || !phoneNumber || phoneNumber.length !== 10}
                className="w-full px-6 py-3 text-base font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 ease-in-out transform hover:scale-[1.02] active:scale-[0.98]"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending Code...
                  </span>
                ) : 'Send Verification Code'}
            </button>
          ) : (
            <div className="mt-2">
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="Enter verification code"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
              <button
                onClick={handleVerificationCodeSubmit}
                disabled={loading || !verificationCode}
                className="mt-2 w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                {loading ? 'Verifying...' : 'Verify Code'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
    </div>
  );
}