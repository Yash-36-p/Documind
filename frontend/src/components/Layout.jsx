import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import UploadModal from './UploadModal';

export default function Layout() {
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 font-sans">
      <Navbar onOpenUpload={() => setIsUploadOpen(true)} />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 overflow-x-hidden p-6 md:p-8">
          <Outlet context={{ openUpload: () => setIsUploadOpen(true) }} />
        </main>
      </div>

      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploaded={() => {
          // Can trigger refetch or let navigation handle it
        }}
      />
    </div>
  );
}
