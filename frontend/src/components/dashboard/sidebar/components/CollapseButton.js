'use client';

export default function CollapseButton({ collapsed, onClick }) {
  return (
    <button
      onClick={onClick}
      className="absolute -right-3 top-12 bg-white border border-gray-200 rounded-full p-1.5 shadow-md hover:bg-gray-50 transition-colors"
      aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
    >
      {collapsed ? (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="13 17 18 12 13 7"></polyline>
          <polyline points="6 17 11 12 6 7"></polyline>
        </svg>
      ) : (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="11 17 6 12 11 7"></polyline>
          <polyline points="18 17 13 12 18 7"></polyline>
        </svg>
      )}
    </button>
  );
}
