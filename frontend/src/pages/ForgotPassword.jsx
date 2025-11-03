import React, { useState } from 'react';
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../services/firebase';
import { Link } from 'react-router-dom';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    if (!email) return setError('Please enter your email');
    setLoading(true);
    try {
      await sendPasswordResetEmail(auth, email);
      setMessage('Password reset email sent. Check your inbox.');
    } catch (err) {
      setError(err?.message || 'Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-amber-50 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white/80 backdrop-blur-lg shadow-2xl rounded-2xl overflow-hidden">
          <div className="p-8 sm:p-10">
            <h2 className="text-2xl font-semibold mb-2">Reset your password</h2>
            <p className="text-sm text-slate-500 mb-6">Enter the email you used to create your account and we'll send a reset link.</p>

            {message && <div className="mb-4 text-sm text-green-600">{message}</div>}
            {error && <div className="mb-4 text-sm text-red-600">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-300"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <button type="submit" disabled={loading} className="w-full py-3 rounded-lg bg-gradient-to-r from-amber-600 to-yellow-500 text-white font-semibold shadow">
                  {loading ? 'Sending...' : 'Send reset email'}
                </button>
              </div>
            </form>

            <p className="mt-6 text-center text-sm text-slate-500">
              <Link to="/login" className="text-amber-600 font-medium">Back to login</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
