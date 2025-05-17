'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  
  useEffect(() => {
    // Redirect to dataset page
    router.push('/dashboard/dataset');
  }, [router]);
  
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-purple-600 mb-2">Sapdo</h1>
        <p className="text-gray-500">Redirecting to dataset page...</p>
      </div>
    </div>
  );
}
