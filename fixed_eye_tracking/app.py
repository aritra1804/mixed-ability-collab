from flask import Flask, render_template, jsonify
import threading
import os
from src.collect_data import collect_gaze_data
from src.ivt import process_gaze_data
from src.viz import capture_and_visualize

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_tracking', methods=['POST'])
def start_tracking():
    def run_pipeline():
        # Run the gaze tracking pipeline:
        # 1. Collect gaze data (this function should run for a fixed duration or until a condition is met)
        gaze_csv = collect_gaze_data()  
        # 2. Process the collected data using the IVT algorithm
        fixation_csv = process_gaze_data(gaze_csv)
        # 3. Capture a screenshot (if needed) and visualize the gaze overlay
        capture_and_visualize(gaze_csv, fixation_csv)
        # (Optional) Save a visualization image that can later be served by Flask

    # Run the pipeline in a separate thread so the HTTP response isn’t blocked.
    thread = threading.Thread(target=run_pipeline)
    thread.start()
    return jsonify({"status": "Tracking started. Check your visualization output when complete."})

if __name__ == '__main__':
    app.run(debug=True)
