from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "API is Running! Use /api/download?url=YOUR_YOUTUBE_URL"

@app.route('/api/download', methods=['GET'])
def get_video_info():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Konfigurasi yt-dlp agar tidak mendownload, hanya mengambil info
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'quiet': True,
            'skip_download': True, # PENTING: Jangan download di server
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Ambil Data Video (MP4)
            video_url_direct = None
            # Ambil Data Audio (M4A/WEBM - mendekati MP3)
            audio_url_direct = None

            # Loop formats untuk mencari yang terbaik (ada suara dan gambar)
            for f in info['formats']:
                # Cari video yang ada audio dan videonya (biasanya format 22 atau 18)
                if f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    video_url_direct = f['url']
                
                # Cari audio only (m4a biasanya)
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_url_direct = f['url']

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'download_links': {
                    'mp4': video_url_direct or info['url'], # Fallback ke default
                    'mp3_audio_source': audio_url_direct # Browser akan membacanya sebagai audio
                }
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Entry point untuk Vercel
if __name__ == '__main__':
    app.run(debug=True)
