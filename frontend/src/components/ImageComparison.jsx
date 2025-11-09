import React from 'react';

const ImageComparison = ({ originalImage, restoredImage }) => {
  return (
    <div className="grid md:grid-cols-2 gap-8">
      {/* Original Image */}
      <div className="space-y-3">
        <h3 className="text-xl font-semibold text-white text-center">
          📷 Original
        </h3>
        <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg aspect-square flex items-center justify-center">
          {originalImage ? (
            <img
              src={originalImage}
              alt="Original"
              className="w-full h-full object-contain"
            />
          ) : (
            <p className="text-gray-500">No image uploaded</p>
          )}
        </div>
      </div>

      {/* Restored Image */}
      <div className="space-y-3">
        <h3 className="text-xl font-semibold text-white text-center">
          ✨ Enhanced
        </h3>
        <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg aspect-square flex items-center justify-center">
          {restoredImage ? (
            <img
              src={restoredImage}
              alt="Restored"
              className="w-full h-full object-contain"
            />
          ) : (
            <div className="text-center p-8">
              <svg
                className="w-16 h-16 text-gray-600 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="text-gray-500">Enhanced image will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageComparison;
