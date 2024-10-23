from flask import Flask, request, jsonify
import os
import numpy as np
import librosa
from tensorflow.keras.models import load_model

# Initialize Flask app
app = Flask(__name__)

# Load the pre-trained model
model = load_model(os.path.join('Audio Deepfake Detection Service','audio_classifier.h5'));

# Define constants based on model training parameters
SAMPLE_RATE = 22050  # Same as used in training
DURATION = 5  # For example, if your model uses 5-second clips
N_MELS = 128  # Number of Mel bands
MAX_TIME_STEPS = 109  # Set to match model input dimensions (time steps)

def preprocess_audio(file_path):
    # Load audio file using librosa
    audio, _ = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)

    # Extract Mel spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=SAMPLE_RATE, n_mels=N_MELS)
    mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

    # Ensure all spectrograms have the same width (time steps)
    if mel_spectrogram.shape[1] < MAX_TIME_STEPS:
        mel_spectrogram = np.pad(mel_spectrogram, ((0, 0), (0, MAX_TIME_STEPS - mel_spectrogram.shape[1])), mode='constant')
    else:
        mel_spectrogram = mel_spectrogram[:, :MAX_TIME_STEPS]

    # Expand dimensions to match model input shape (batch_size, height, width, channels)
    mel_spectrogram = np.expand_dims(mel_spectrogram, axis=-1)  # Add channel dimension
    return mel_spectrogram

def classify_audio(file_path):
    # Preprocess the audio file
    mel_spectrogram = preprocess_audio(file_path)

    # Expand dimensions to match batch size (1, height, width, channels)
    mel_spectrogram = np.expand_dims(mel_spectrogram, axis=0)

    # Predict using the loaded model
    y_pred = model.predict(mel_spectrogram)

    # Convert probabilities to predicted class (0 for real, 1 for fake)
    y_pred_class = np.argmax(y_pred, axis=1)[0]

    return "Real" if y_pred_class == 1 else "Fake"

# Route to handle file upload and classification
@app.route('/classify', methods=['POST'])
def upload_and_classify():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file temporarily
    file_path = os.path.join('Audio Deepfake Detection Service','uploads', file.filename)
    file.save(file_path)

    try:
        # Classify the uploaded audio file
        result = classify_audio(file_path)
        return jsonify({'result': result})
    finally:
        # Clean up: Remove the uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

# Main route to check server status
@app.route('/')
def index():
    return "Audio Classifier is running!"

# Run the app
if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists('Audio Deepfake Detection Service/uploads'):
        os.makedirs('Audio Deepfake Detection Service/uploads')

    app.run(debug=True, host='0.0.0.0', port=5001)
