import React, { useState, useRef } from 'react';

const ImageUploader = ({ onImageUpload }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file) => {
    // Vérifier que c'est une image
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    // Vérifier la taille (15 MB max)
    const maxSize = 15 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('File is too large. Maximum size is 15 MB.');
      return;
    }

    // Créer une URL de prévisualisation
    const previewUrl = URL.createObjectURL(file);
    onImageUpload(file, previewUrl);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div
      className={`border-4 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
        isDragging
          ? 'border-primary bg-blue-900 bg-opacity-20'
          : 'border-gray-600 hover:border-primary hover:bg-gray-700'
      }`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/webp"
        onChange={handleFileInput}
        className="hidden"
      />

      <div className="flex flex-col items-center">
        {/* Icon */}
        <div className="mb-6">
          <svg
            className="w-24 h-24 text-primary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>

        {/* Text */}
        <h3 className="text-2xl font-semibold text-white mb-2">
          {isDragging ? 'Drop your image here' : 'Upload your blurry image'}
        </h3>
        <p className="text-gray-400 mb-4">
          Drag & drop or click to browse
        </p>
        <p className="text-sm text-gray-500">
          Supported formats: JPEG, PNG, WebP (max 15 MB)
        </p>

        {/* Button */}
        <button
          onClick={handleClick}
          className="mt-6 bg-primary hover:bg-blue-500 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105"
        >
          Choose File
        </button>
      </div>
    </div>
  );
};

export default ImageUploader;
