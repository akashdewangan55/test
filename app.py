import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
# This is crucial for allowing your HTML frontend to communicate with this backend.
CORS(app)

@app.route('/download', methods=['GET'])
def download_video():
    """
    This endpoint takes a YouTube URL as a query parameter,
    fetches available video formats, and returns them as JSON.
    """
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is missing"}), 400

    try:
        # yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True # Suppress console output from yt-dlp
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video information
            info = ydl.extract_info(video_url, download=False)
            
            # Prepare a list to hold format details
            formats = []
            
            # The 'formats' key contains a list of available formats
            if 'formats' in info:
                for f in info['formats']:
                    # We only want to show video formats that have both video and audio
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                        formats.append({
                            "format_id": f.get('format_id'),
                            "ext": f.get('ext'),
                            "resolution": f.get('resolution') or f.get('format_note'),
                            "url": f.get('url') # The direct download link
                        })

            if not formats:
                 return jsonify({"error": "No suitable MP4 formats found."}), 404

            # Return the title and the list of formats
            return jsonify({
                "title": info.get('title', 'No title'),
                "formats": formats
            })

    except yt_dlp.utils.DownloadError as e:
        # Handle errors from yt-dlp (e.g., invalid URL, video unavailable)
        return jsonify({"error": f"Failed to process video: {str(e)}"}), 500
    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the app. 
    # Use 0.0.0.0 to make it accessible from other devices on your network.
    # The default port is 5000.
    app.run(host='0.0.0.0', port=5000, debug=True)
