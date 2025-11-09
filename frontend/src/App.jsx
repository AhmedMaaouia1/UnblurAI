import React, { useState } from 'react';
import ImageUploader from './components/ImageUploader';
import ImageComparison from './components/ImageComparison';
import LoadingSpinner from './components/LoadingSpinner';
import axios from 'axios';

// Configuration de l'API URL
// En développement local ou depuis le navigateur, utiliser localhost
// En production Docker, la variable d'environnement peut être définie
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [originalImage, setOriginalImage] = useState(null);
  const [restoredImage, setRestoredImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleImageUpload = (file, previewUrl) => {
    setOriginalImage({ file, previewUrl });
    setRestoredImage(null);
    setError(null);
  };

  const handleEnhanceImage = async () => {
    if (!originalImage) {
      setError('Please upload an image first');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Créer le FormData
      const formData = new FormData();
      formData.append('file', originalImage.file);

      // Envoyer la requête au backend
      const response = await axios.post(`${API_URL}/restore`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', // Important pour recevoir l'image
      });

      // Créer une URL pour l'image restaurée
      const restoredUrl = URL.createObjectURL(response.data);
      setRestoredImage(restoredUrl);
    } catch (err) {
      console.error('Error enhancing image:', err);
      
      if (err.response) {
        // Le serveur a répondu avec un code d'erreur
        if (err.response.status === 503) {
          setError('The AI model is not loaded. Please check the server logs.');
        } else if (err.response.status === 413) {
          setError('Image file is too large. Maximum size is 15 MB.');
        } else if (err.response.status === 415) {
          setError('Unsupported file format. Please use JPEG or PNG.');
        } else {
          setError(`Server error: ${err.response.statusText}`);
        }
      } else if (err.request) {
        // La requête a été envoyée mais pas de réponse
        setError('Cannot connect to the server. Please check if the backend is running.');
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setOriginalImage(null);
    setRestoredImage(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-dark py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Unblur<span className="text-primary">AI</span>
          </h1>
          <p className="text-gray-300 text-xl">
            Bring clarity back to your images
          </p>
        </header>

        {/* Main Content */}
        <div className="bg-gray-800 rounded-2xl shadow-2xl p-8">
          {!originalImage ? (
            // Upload Section
            <ImageUploader onImageUpload={handleImageUpload} />
          ) : (
            // Processing Section
            <div>
              <ImageComparison
                originalImage={originalImage.previewUrl}
                restoredImage={restoredImage}
              />

              {/* Action Buttons */}
              <div className="flex justify-center gap-4 mt-8">
                {!restoredImage && !isProcessing && (
                  <button
                    onClick={handleEnhanceImage}
                    className="bg-primary hover:bg-blue-500 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105 shadow-lg"
                  >
                    ✨ Enhance Image
                  </button>
                )}

                <button
                  onClick={handleReset}
                  className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-8 rounded-lg transition duration-300"
                >
                  🔄 Upload New Image
                </button>

                {restoredImage && (
                  <a
                    href={restoredImage}
                    download="restored_image.png"
                    className="bg-green-600 hover:bg-green-500 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105 shadow-lg"
                  >
                    📥 Download
                  </a>
                )}
              </div>

              {/* Loading Spinner */}
              {isProcessing && (
                <div className="mt-8">
                  <LoadingSpinner />
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="mt-8 p-4 bg-red-900 border border-red-700 rounded-lg">
                  <p className="text-red-200 text-center">❌ {error}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="text-center mt-12 text-gray-400">
          <p>Powered by U-Net deep learning model</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
