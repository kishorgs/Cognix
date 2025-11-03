import React from 'react';
import FileUpload from '../components/FileUpload';

export default function Dashboard() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Upload and manage your documents securely.</p>
        </div>

        <div className="mb-8">
          <FileUpload />
        </div>
      </div>
    </div>
  );
}