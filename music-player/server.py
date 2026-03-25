from flask import Flask, request, jsonify, Response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = 'KXl4O1ifFEknBEUNa0E'
API_BASE = 'https://api.yaohud.cn/api/music/kg'
LRC_API = 'https://api.yaohud.cn/api/music/lrc'

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
        g = request.args.get('g', '20')
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

@app.route('/api/music/lrc', methods=['GET'])
def get_lrc():
    try:
        hash_val = request.args.get('hash', '')
        song_name = request.args.get('song', '')
        
        results = {}
        
        if hash_val:
            kg_params = {
                'key': API_KEY,
                'mid': hash_val,
                'type': 'kg'
            }
            kg_response = requests.get(LRC_API, params=kg_params, timeout=10)
            kg_data = kg_response.json()
            if kg_data.get('data', {}).get('lyric'):
                results['kg'] = kg_data['data']['lyric']
        
        if song_name:
            wy_params = {
                'key': API_KEY,
                'mid': song_name,
                'type': 'wy'
            }
            try:
                wy_response = requests.get(LRC_API, params=wy_params, timeout=5)
                wy_data = wy_response.json()
                if wy_data.get('data', {}).get('lyric'):
                    results['wy'] = wy_data['data']['lyric']
            except:
                pass
            
            qq_params = {
                'key': API_KEY,
                'mid': song_name,
                'type': 'qq'
            }
            try:
                qq_response = requests.get(LRC_API, params=qq_params, timeout=5)
                qq_data = qq_response.json()
                if qq_data.get('data', {}).get('lyric'):
                    results['qq'] = qq_data['data']['lyric']
            except:
                pass
        
        if results:
            return jsonify({'code': 200, 'data': {'lyric': results.get('kg') or results.get('wy') or results.get('qq'), 'sources': list(results.keys())}})
        else:
            return jsonify({'code': 400, 'data': {'msg': '未找到歌词'}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/play', methods=['GET'])
def play_music():
    try:
        url = request.args.get('url', '')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.kugou.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        
        return Response(
            response.iter_content(chunk_size=1024*1024),
            headers={
                'Content-Type': 'audio/mpeg',
                'Content-Length': response.headers.get('content-length', ''),
                'Accept-Ranges': 'bytes'
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
