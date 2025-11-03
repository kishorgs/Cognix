import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signInWithEmailAndPassword, sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../services/firebase';
import AuthMethods from '../components/AuthMethods';

// A polished login UI using Tailwind CSS. Keeps existing firebase behavior.

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotMessage, setForgotMessage] = useState(null);
  const [forgotError, setForgotError] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);

  const setAuthCookie = (token) => {
    // Set cookie for 7 days (not HTTP-only from client). For production, set cookie from server as httpOnly.
    const maxAge = 7 * 24 * 60 * 60; // 7 days in seconds
    document.cookie = `authToken=${token}; path=/; max-age=${maxAge}`;
  };

  const handleForgotPassword = async () => {
    setForgotError(null);
    setForgotMessage(null);
    if (!email) {
      setForgotError('Please enter your email above to reset your password.');
      return;
    }
    setForgotLoading(true);
    try {
      await sendPasswordResetEmail(auth, email);
      setForgotMessage('Password reset email sent. Check your inbox.');
    } catch (err) {
      setForgotError(err?.message || 'Failed to send reset email');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleAuthSuccess = (token) => {
    setAuthCookie(token);
    navigate('/dashboard');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError('Please enter email and password.');
      return;
    }

    setLoading(true);
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      const token = await user.getIdToken();
      handleAuthSuccess(token);
    } catch (err) {
      const msg = err?.message || 'Login failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-sky-50 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white/80 backdrop-blur-lg shadow-2xl rounded-2xl overflow-hidden transition-transform transform hover:scale-[1.01]">
          <div className="p-8 sm:p-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-12 w-12 rounded-full bg-gradient-to-tr from-indigo-500 to-sky-400 flex items-center justify-center text-white font-bold">CX</div>
              <div>
                <h1 className="text-2xl font-semibold">Welcome back</h1>
                <p className="text-sm text-slate-500">Sign in to continue to Cognix</p>
              </div>
            </div>

            {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                <div className="relative">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pr-12 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-300"
                    placeholder="you@example.com"
                    aria-label="email"
                  />
                  <div className="absolute right-3 top-3 text-slate-400 text-sm">@</div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pr-12 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-300"
                    placeholder="Enter your password"
                    aria-label="password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className="absolute right-2 top-2 text-slate-500 px-2 py-1 rounded"
                    aria-label="toggle password visibility"
                  >
                    {showPassword ? (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10 3C6 3 2.7 5.3 1 9c1.7 3.7 5 6 9 6s7.3-2.3 9-6c-1.7-3.7-5-6-9-6zM10 13a3 3 0 110-6 3 3 0 010 6z" /></svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0110 19c-4 0-7.3-2.3-9-6a18.67 18.67 0 014.3-5.15m3.9-.85A9.97 9.97 0 0110 5c4 0 7.3 2.3 9 6a19.2 19.2 0 01-1.3 2.3M3 3l18 18"/></svg>
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className="h-4 w-4" />
                  Remember me
                </label>
                <button type="button" onClick={handleForgotPassword} disabled={forgotLoading} className="text-sm text-sky-600 hover:underline">
                  {forgotLoading ? 'Sending...' : 'Forgot password?'}
                </button>
              </div>

              {forgotMessage && <div className="text-sm text-green-600">{forgotMessage}</div>}
              {forgotError && <div className="text-sm text-red-600">{forgotError}</div>}

              <div>
                <button type="submit" disabled={loading} className="w-full py-3 rounded-lg bg-gradient-to-r from-indigo-600 to-sky-500 text-white font-semibold shadow">
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
              </div>
            </form>

            <AuthMethods 
              onSuccess={handleAuthSuccess}
              onError={setError}
              mode="login"
            />

            <p className="mt-6 text-center text-sm text-slate-500">
              Don't have an account? <Link to="/register" className="text-sky-600 font-medium">Create one</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
