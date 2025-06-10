from flask import Flask, render_template
import os

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello! The Flask app is running.'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
