import os
from flask import Flask, render_template, request, redirect,Response,url_for
from werkzeug.utils import secure_filename
import ImageSlidingAndHandTracking as imgsliding
import VideoPresentationUsingHandTracking as videoHandler
app = Flask(__name__)
import os

# for image
UPLOAD_FOLDER = 'presentation'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# for video
VIDEO_FOLDER = 'video_presentation'  # Folder for uploaded videos
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
  files = request.files.getlist('files[]')
  files1 = request.files.getlist('files[]')

  if not files:
    return redirect(request.url)

  # Remove existing files in the "presentation" folder
  if os.path.exists(app.config['UPLOAD_FOLDER']):
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    for f in files:
      os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
  for file in files1:
    print(file.filename)
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

  # Redirect to the presentation page after upload
  return redirect(url_for('presentation'))

@app.route('/video_upload', methods=['POST'])
def video_upload():
    files = request.files.getlist('files[]')
    if not files:
        return redirect(request.url)

    # Remove existing files in the "video_presentation" folder
    if os.path.exists(app.config['VIDEO_FOLDER']):
        existing_videos = os.listdir(app.config['VIDEO_FOLDER'])
        for video in existing_videos:
            os.remove(os.path.join(app.config['VIDEO_FOLDER'], video))
    
    # Save uploaded videos
    for video in files:
        print(video.filename)
        filename = secure_filename(video.filename)
        video.save(os.path.join(app.config['VIDEO_FOLDER'], filename))

    # Redirect to the presentation page or another endpoint after upload
    return redirect(url_for('video_presentation'))

@app.route('/video_feed')
def video_feed():
    return Response(imgsliding.gen_frames_main(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_for_videos')
def video_feed_for_videos():
    return Response(videoHandler.gen_video_frames_main(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_presentation')
def video_presentation():
  # Presentation page with video feed
  return render_template('video_presentation.html')

@app.route('/presentation')
def presentation():
  # Presentation page with video feed
  return render_template('presentation.html')

@app.route('/thankyou')
def thank_you():
  # Thank you page
  return render_template('thankyou.html')

if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)
  
# create video folder if not exits
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
  
# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port, debug=True)