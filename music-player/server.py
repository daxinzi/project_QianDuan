from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = 'KXl4O1ifFEknBEUNa0E'
API_BASE = 'https://api.yaohud.cn/api/music/kg'

@app.route('/api/music/search', methods=['GET'])
def search_music():
    try:
        keyword = request.args.get('msg', '')
        n = request.args.get('n', '')
        g = request.args.get('g', '12')
        quality = request.args.get('quality', 'flac')
        
        params = {
            'key': API_KEY,
            'msg': keyword,
            'g': g,
            'quality': quality
        }
        
        if n:
            params['n'] = n
        
        response = requests.get(API_BASE, params=params, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/playlist', methods=['GET'])
def get_playlist():
    try:
        keyword = request.args.get('msg', '')
        g = request.args.get('g', '12')
        quality = request.args.get('quality', 'flac')
        
        params = {
            'key': API_KEY,
            'msg': keyword,
            'g': g,
            'quality': quality
        }
        
        response = requests.get(API_BASE, params=params, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/song', methods=['GET'])
def get_song():
    try:
        keyword = request.args.get('msg', '')
        n = request.args.get('n', '1')
        quality = request.args.get('quality', 'flac')
        
        params = {
            'key': API_KEY,
            'msg': keyword,
            'n': n,
            'quality': quality
        }
        
        response = requests.get(API_BASE, params=params, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
