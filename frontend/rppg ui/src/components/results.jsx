import React from 'react';

const ClassificationDisplay = () => {
  // Sample data - replace with your actual data
  const data = {
    classification: "Not Deepfake",
    plot_image: "iVBORw0KGgoAAAANSUhEUgAAA..." // your base64 string
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-blue-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-white mb-8">
          Image Analysis Results
        </h1>
        
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          {/* Image Section */}
          <div className="p-6">
            <img
              src={`data:image/png;base64,${data.plot_image}`}
              alt="Classification Plot"
              className="w-full h-auto rounded-lg shadow-lg hover:scale-105 transition-transform duration-300"
            />
          </div>

          {/* Result Section */}
          <div className="p-6 border-t border-gray-200">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Classification Result
            </h2>
            
            <div className={`inline-block px-4 py-2 rounded-full text-white font-medium ${
              data.classification === "Not Deepfake" 
                ? "bg-green-500" 
                : "bg-red-500"
            }`}>
              {data.classification}
            </div>

            {/* Analysis Details */}
            <div className="mt-6 space-y-4">
              <h3 className="text-xl font-medium text-gray-700">
                Analysis Details
              </h3>
              
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-700 mb-2">Confidence Score</h4>
                <div className="w-full h-2 bg-gray-200 rounded-full">
                  <div className="h-full w-4/5 bg-blue-500 rounded-full" />
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-gray-600">
                  This analysis was performed using advanced machine learning techniques
                  to detect potential image manipulations.
                </p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
            <button className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors duration-300">
              Download Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClassificationDisplay;