import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center">
      {/* Spinner */}
      <div className="relative">
        <div className="w-20 h-20 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <svg
            className="w-8 h-8 text-primary"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
            <path
              fillRule="evenodd"
              d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </div>

      {/* Text */}
      <p className="mt-6 text-white text-lg font-semibold">
        Enhancing your image...
      </p>
      <p className="mt-2 text-gray-400">
        This may take a few seconds
      </p>

      {/* Progress Bar */}
      <div className="w-64 h-2 bg-gray-700 rounded-full mt-6 overflow-hidden">
        <div className="h-full bg-primary rounded-full animate-pulse"></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
