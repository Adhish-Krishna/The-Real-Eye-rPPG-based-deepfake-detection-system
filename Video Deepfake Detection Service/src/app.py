from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import shutil
import io
import base64
import matplotlib.pyplot as plt
from vid_to_deepframes_rawframes import vid_to_frames_rawframes
from DeepFakesON_Phys_extract_predictions import predict_deepfake
from collections import defaultdict

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

def classify_video_by_frames(file_path, min_score_threshold, ratio_threshold=0.5):
    # Dictionary to store frame scores for each video
    video_scores = defaultdict(list)

    # Read and parse the frame scores from the input file
    with open(file_path, 'r') as file:
        for line in file:
            if "img;score" in line:  # Skip the header line
                continue

            line = line.strip().replace("\\", "/").split(';')
            video_path = os.path.splitext(line[0])[0]
            video_path = video_path.rsplit('.avi', 1)[0]
            video_name = os.path.split(video_path)[-1]  # Extract the video name

            score = float(line[1].strip('[]'))  # Extract the frame score

            # Append the score to the corresponding video entry
            video_scores[video_name].append(score)

    # List to store final classification results
    video_classification = []

    # Process each video's frames and make a final classification
    for video, scores in video_scores.items():
        # Calculate the ratio of frames above the threshold
        frames_above_threshold = sum(1 for score in scores if score > min_score_threshold)
        total_frames = len(scores)
        ratio_above_threshold = frames_above_threshold / total_frames

        # Classify the video based on the ratio of frames above the threshold
        if ratio_above_threshold >= ratio_threshold:
            classification = "Not Deepfake"
        else:
            classification = "Deepfake"

        # Calculate the combined score (e.g., average score)
        combined_score = sum(scores) / total_frames

        # Append the result (video name, classification, and combined score)
        video_classification.append((video, classification, combined_score, scores))

    return video_classification

# Helper function to clean up video and frames
def cleanup_video_and_frames(video_name):
    video_path = os.path.join('Video Deepfake Detection Service','videos', video_name)

    # Remove the video file
    if os.path.exists(video_path):
        os.remove(video_path)

    # Remove preprocessed frames in DeepFrames and RawFrames
    deepframes_path = os.path.join('Video Deepfake Detection Service','videos', 'DeepFrames', video_name)
    rawframes_path = os.path.join('Video Deepfake Detection Service','videos', 'RawFrames', video_name)

    # Clean up the folder with preprocessed images, but leave the main folders intact
    if os.path.exists(deepframes_path):
        shutil.rmtree(deepframes_path)
    if os.path.exists(rawframes_path):
        shutil.rmtree(rawframes_path)

# Route to handle video upload and detection
@app.route('/upload', methods=['POST'])
def upload_video():

    print("Request received:", request.data)
    print("Files in request:", request.files)

    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    video_path = os.path.join('Video Deepfake Detection Service','videos', video.filename)
    video_name = video.filename;
    video.save(video_path)

    print(video_name)
    print(video_path)

    # Process the video
    try:
        vid_to_frames_rawframes(video.filename)  # Extract frames from the video
        predict_deepfake()  # Apply deepfake detection

        min_score = 0.579  # Threshold for deepfake detection defined in the DOP paper
        ratio_threshold = 0.5  # Threshold: 50% of frames must have scores above the threshold
        DOP_output_file = 'Video Deepfake Detection Service/deepfake_scores.txt'  # Input file with frame scores

        # Classify the videos based on aggregated frame scores
        classified_videos = classify_video_by_frames(DOP_output_file, min_score, ratio_threshold)

        # Clean up by deleting the video and its preprocessed frames
        cleanup_video_and_frames(video_name)

        # Prepare the response data
        response_data = []

        for video, classification, combined_score, scores in classified_videos:
            # Plot the results
            plt.figure(figsize=(10, 6))
            plt.plot(range(len(scores)), scores, marker='o', linestyle='-', color='b')
            plt.axhline(y=min_score, color='r', linestyle='--', label='Threshold')
            plt.xlabel('Frame Number')
            plt.ylabel('Prediction Score')
            plt.title(f'Frame Scores for {video}')
            plt.legend()

            # Save the plot to a BytesIO object
            img_io = io.BytesIO()
            plt.savefig(img_io, format='png')
            img_io.seek(0)
            plt.close()

            # Encode the image to base64
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

            # Append the result to the response data
            response_data.append({
                "video": video,
                "classification": classification,
                "prediction": combined_score,
                "plot_image": img_base64
            })

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not os.path.exists('Video Deepfake Detection Service/videos'):
        os.makedirs('Video Deepfake Detection Service/videos')
        os.makedirs('Video Deepfake Detection Service/videos/DeepFrames')
        os.makedirs('Video Deepfake Detection Service/videos/RawFrames')
    app.run(debug=True, host='0.0.0.0', port=5000)