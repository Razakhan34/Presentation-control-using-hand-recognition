import os
from flask import Flask, render_template, request, redirect,Response,url_for
from werkzeug.utils import secure_filename
import ImageSlidingAndHandTracking as imgsliding
app = Flask(__name__)

UPLOAD_FOLDER = 'presentation'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/video_feed')
def video_feed():
    return Response(imgsliding.gen_frames_main(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
if __name__ == "__main__":
    app.run(debug=True)
