import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../services/firebase';
import AuthMethods from '../components/AuthMethods';

export default function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const setAuthCookie = (token) => {
    const maxAge = 7 * 24 * 60 * 60;
    document.cookie = `authToken=${token}; path=/; max-age=${maxAge}`;
  };

  const handleAuthSuccess = (token) => {
    setAuthCookie(token);
    navigate('/dashboard');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!email || !password) return setError('Email and password are required');
    if (password !== confirm) return setError('Passwords do not match');

    setLoading(true);
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const token = await userCredential.user.getIdToken();
      handleAuthSuccess(token);
    } catch (err) {
      setError(err?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-rose-50 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white/80 backdrop-blur-lg shadow-2xl rounded-2xl overflow-hidden">
          <div className="p-8 sm:p-10">
            <h2 className="text-2xl font-semibold mb-2">Create your account</h2>
            <p className="text-sm text-slate-500 mb-6">Start building with Cognix — it's quick and easy.</p>

            {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300" placeholder="you@example.com" />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                <div className="relative">
                  <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-3 pr-12 border rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300" placeholder="Create a strong password" />
                  <button type="button" onClick={() => setShowPassword(s => !s)} className="absolute right-2 top-2 text-slate-500">{showPassword ? 'Hide' : 'Show'}</button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Confirm password</label>
                <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300" placeholder="Confirm password" />
              </div>

              <div>
                <button type="submit" disabled={loading} className="w-full py-3 rounded-lg bg-gradient-to-r from-rose-600 to-pink-500 text-white font-semibold shadow">
                  {loading ? 'Creating...' : 'Create account'}
                </button>
              </div>
            </form>

            <AuthMethods 
              onSuccess={handleAuthSuccess}
              onError={setError}
              mode="register"
            />

            <p className="mt-6 text-center text-sm text-slate-500">
              Already have an account? <Link to="/login" className="text-rose-600 font-medium">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
