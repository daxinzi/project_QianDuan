<template>
  <div class="music-player">
    <div class="player-main">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索歌曲或歌手..." 
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button v-if="searchQuery" class="clear-btn" @click="clearSearch">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
      </div>
      <div class="album-cover" :class="{ playing: isPlaying }" @click="toggleLyricMode">
        <img v-if="!showLyric" :src="currentSong.cover || defaultCover" alt="Album Cover" />
        <div v-else class="lyric-display">
          <p v-for="(line, index) in currentLyric" :key="index" :class="{ active: index === lyricIndex }">
            {{ line }}
          </p>
        </div>
      </div>
      <div class="song-info">
        <h2 class="song-title" :title="currentSong.title">{{ currentSong.title || '搜索歌曲开始播放' }}</h2>
        <p class="song-artist">{{ currentSong.artist || '' }}</p>
      </div>
      <div class="progress-section">
        <div class="progress-bar" @click="seek">
          <div class="progress" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="time-display">
          <span>{{ formatTime(currentTime) }}</span>
          <span>{{ formatTime(duration) }}</span>
        </div>
      </div>
      <div class="controls">
        <button class="btn-prev" @click="prevSong">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6V6zm3.5 6l8.5 6V6l-8.5 6z"/></svg>
        </button>
        <button class="btn-play" @click="togglePlay" :disabled="!currentSong.src">
          <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        </button>
        <button class="btn-next" @click="nextSong" :disabled="songs.length === 0">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zm2-12v12l6.5-6L8 6zm8 0v12h2V6h-2z"/></svg>
        </button>
      </div>
      <div class="volume-control">
        <svg class="volume-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
        <input type="range" min="0" max="100" v-model="volume" @input="setVolume" class="volume-slider" />
      </div>
    </div>
    <div class="playlist">
      <h3>{{ searchQuery ? '搜索结果' : '播放列表' }}</h3>
      <div v-if="loading" class="loading">
        <p>加载中...</p>
      </div>
      <ul v-else-if="displayedSongs.length > 0" class="song-list">
        <li 
          v-for="(song, index) in displayedSongs" 
          :key="song.id || index"
          :class="{ active: song.id === currentSong.id }"
          @click="playSongById(song.id)"
        >
          <div class="song-cover">
            <img :src="song.cover || defaultCover" :alt="song.title" />
            <div class="play-overlay">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            </div>
          </div>
          <div class="song-info-card">
            <div class="song-name" :title="song.title">{{ song.title }}</div>
            <div class="song-artist" :title="song.artist">{{ song.artist }}</div>
            <div class="song-album" :title="song.album || '未知专辑'">{{ song.album || '未知专辑' }}</div>
          </div>
          <div class="song-quality" v-if="song.qualities && song.qualities.length">
            <span v-for="q in song.qualities.slice(0, 2)" :key="q" :class="'quality-' + q">{{ q }}</span>
          </div>
        </li>
      </ul>
      <div v-else class="no-results">
        <p>{{ searchQuery ? '未找到相关音乐，请尝试其他关键词' : '输入歌曲名称搜索音乐' }}</p>
      </div>
      <div v-if="totalPages > 1" class="pagination">
        <button class="page-btn" @click="prevPage" :disabled="currentPage === 1">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" @click="nextPage" :disabled="currentPage === totalPages">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const searchQuery = ref('')
const songs = ref([])
const currentIndex = ref(0)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(28)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = 4
const totalCount = ref(0)
const showLyric = ref(false)
const currentLyric = ref([])
const lyricIndex = ref(0)

const defaultCover = 'https://picsum.photos/seed/music/300/300'

let audio = null

const currentSong = computed(() => songs.value[currentIndex.value] || {})

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize) || 1)

const displayedSongs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return songs.value.slice(start, end)
})

const progress = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

const initAudio = () => {
  audio = new Audio()
  audio.volume = volume.value / 100
  
  audio.addEventListener('timeupdate', () => {
    currentTime.value = audio.currentTime
    if (showLyric.value) {
      updateLyric()
    }
  })
  
  audio.addEventListener('loadedmetadata', () => {
    duration.value = audio.duration
  })
  
  audio.addEventListener('ended', () => {
    nextSong()
  })
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  loading.value = true
  currentPage.value = 1
  try {
    const response = await fetch(`/api/music/playlist?msg=${encodeURIComponent(searchQuery.value)}&g=20&quality=flac`)
    const res = await response.json()
    
    if (res.data && res.data.songs && Array.isArray(res.data.songs)) {
      songs.value = res.data.songs.map((item, index) => ({
        id: index,
        title: item.name || '未知歌曲',
        artist: item.singer || '未知歌手',
        duration: item.duration || '--:--',
        album: item.album || '',
        cover: item.cover || defaultCover,
        qualities: item.qualities || [],
        src: '',
        n: item.n
      }))
      totalCount.value = songs.value.length
      currentIndex.value = 0
    } else {
      songs.value = []
      totalCount.value = 0
    }
  } catch (error) {
    console.error('搜索失败:', error)
    songs.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  songs.value = []
  currentIndex.value = 0
  totalCount.value = 0
  currentPage.value = 1
  if (audio) {
    audio.pause()
    audio.currentTime = 0
  }
  isPlaying.value = false
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const playSongById = (id) => {
  const index = songs.value.findIndex(song => song.id === id)
  if (index !== -1) {
    playSong(index)
  }
}

const toggleLyricMode = () => {
  showLyric.value = !showLyric.value
}

const updateLyric = () => {
  if (currentLyric.value.length === 0) return
  const time = currentTime.value
  for (let i = currentLyric.value.length - 1; i >= 0; i--) {
    if (time >= i * 3) {
      lyricIndex.value = i
      break
    }
  }
}

const fetchLyric = async (hash, songName) => {
  if (!hash && !songName) {
    currentLyric.value = ['暂无歌词']
    return
  }
  
  try {
    const params = new URLSearchParams()
    if (hash) params.append('hash', hash)
    if (songName) params.append('song', songName)
    
    const response = await fetch(`/api/music/lrc?${params.toString()}`)
    const res = await response.json()
    
    if (res.data && res.data.lyric) {
      const lyricText = res.data.lyric
      currentLyric.value = parseLyric(lyricText)
    } else {
      currentLyric.value = ['暂无歌词']
    }
  } catch (error) {
    console.error('获取歌词失败:', error)
    currentLyric.value = ['暂无歌词']
  }
}

const parseLyric = (lrcText) => {
  const lines = lrcText.split('\n')
  const result = []
  
  for (const line of lines) {
    const match = line.match(/\[.*?\](.*)/)
    if (match) {
      const text = match[1].trim()
      if (text) {
        result.push(text)
      }
    }
  }
  
  return result.length > 0 ? result : ['暂无歌词']
}

const playSong = async (index) => {
  if (songs.value.length === 0) return
  
  currentIndex.value = index
  const song = songs.value[index]
  
  try {
    const response = await fetch(`/api/music/song?msg=${encodeURIComponent(song.title)}&n=${song.n || 1}&quality=flac`)
    const res = await response.json()
    
    if (res.data && res.data.play_url) {
      const playUrl = `/api/music/play?url=${encodeURIComponent(res.data.play_url)}`
      const cover = res.data.cover || song.cover
      const duration = res.data.duration || song.duration
      const hash = res.data.hash ? res.data.hash['flac'] || res.data.hash['320'] || res.data.hash['128'] : ''
      
      audio.src = playUrl
      songs.value[index].src = playUrl
      songs.value[index].cover = cover
      songs.value[index].duration = duration
      
      await audio.play()
      isPlaying.value = true
      
      fetchLyric(hash, song.title)
      lyricIndex.value = 0
    } else {
      console.error('获取播放链接失败')
    }
  } catch (error) {
    console.error('播放失败:', error)
  }
}

const togglePlay = () => {
  if (!currentSong.value.src && songs.value.length > 0) {
    playSong(currentIndex.value)
    return
  }
  
  if (isPlaying.value) {
    audio.pause()
  } else {
    audio.play()
  }
  isPlaying.value = !isPlaying.value
}

const prevSong = () => {
  if (songs.value.length === 0) return
  currentIndex.value = (currentIndex.value - 1 + songs.value.length) % songs.value.length
  playSong(currentIndex.value)
}

const nextSong = () => {
  if (songs.value.length === 0) return
  currentIndex.value = (currentIndex.value + 1) % songs.value.length
  playSong(currentIndex.value)
}

const seek = (e) => {
  if (!audio.src) return
  const rect = e.target.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  audio.currentTime = percent * duration.value
}

const setVolume = () => {
  if (audio) {
    audio.volume = volume.value / 100
  }
}

const formatTime = (time) => {
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

watch(volume, (newVal) => {
  if (audio) {
    audio.volume = newVal / 100
  }
})

onMounted(() => {
  initAudio()
})

onUnmounted(() => {
  if (audio) {
    audio.pause()
    audio = null
  }
})
</script>

<style scoped>
.music-player {
  display: flex;
  gap: 40px;
  padding: 40px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  max-width: 1300px;
  margin: 10px auto;
  height: calc(100vh - 20px);
  box-sizing: border-box;
}

.player-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  min-height: 0;
  overflow: hidden;
}

.search-box {
  position: relative;
  width: 100%;
  max-width: 400px;
  margin-bottom: 10px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #888;
}

.search-input {
  width: 100%;
  padding: 12px 44px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 25px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: #888;
}

.search-input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 107, 107, 0.5);
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.2);
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-btn:hover {
  color: #ff6b6b;
}

.clear-btn svg {
  width: 18px;
  height: 18px;
}

.album-cover {
  width: 250px;
  height: 250px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
  cursor: pointer;
}

.album-cover.playing {
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lyric-display {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  overflow: hidden;
  padding: 20px;
  text-align: center;
}

.lyric-display p {
  margin: 0;
  font-size: 14px;
  color: #aaa;
  line-height: 2;
  transition: all 0.3s;
}

.lyric-display p.active {
  color: #ff6b6b;
  font-size: 16px;
  font-weight: 600;
}

.song-info {
  text-align: center;
  color: #fff;
}

.song-title {
  font-size: 24px;
  margin: 0 0 8px 0;
  font-weight: 600;
  color: #fff;
}

.song-artist {
  font-size: 16px;
  color: #ccc;
  margin: 0;
}

.progress-section {
  width: 100%;
  max-width: 400px;
}

.progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  cursor: pointer;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #ffd93d);
  border-radius: 3px;
  transition: width 0.1s linear;
}

.time-display {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #aaa;
}

.controls {
  display: flex;
  align-items: center;
  gap: 24px;
}

.controls button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  transition: transform 0.2s, color 0.2s;
  padding: 0;
}

.controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.controls button:hover:not(:disabled) {
  transform: scale(1.1);
  color: #ff6b6b;
}

.btn-prev svg, .btn-next svg {
  width: 32px;
  height: 32px;
}

.btn-play {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b, #ffd93d);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-play:hover:not(:disabled) {
  transform: scale(1.1);
  color: #fff !important;
}

.btn-play svg {
  width: 32px;
  height: 32px;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
}

.volume-icon {
  width: 24px;
  height: 24px;
}

.volume-slider {
  width: 100px;
  height: 4px;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ff6b6b;
}

.playlist {
  width: 380px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  color: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.playlist h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #ffd93d;
  flex-shrink: 0;
}

.playlist ul {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
}

.song-list li {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.03);
  margin-bottom: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.song-list li:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 107, 107, 0.3);
  transform: translateX(4px);
}

.song-list li.active {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 217, 61, 0.1));
  border-color: rgba(255, 107, 107, 0.5);
}

.song-cover {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  margin-right: 12px;
}

.song-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.song-list li:hover .play-overlay {
  opacity: 1;
}

.play-overlay svg {
  width: 24px;
  height: 24px;
  color: #fff;
}

.song-info-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.song-info-card .song-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-info-card .song-artist {
  font-size: 12px;
  color: #aaa;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-info-card .song-album {
  font-size: 11px;
  color: #777;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-quality {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 10px;
}

.song-quality span {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  text-align: center;
  font-weight: 600;
}

.quality-flac {
  background: linear-gradient(135deg, #ff6b6b, #ffd93d);
  color: #000;
}

.quality-320 {
  background: rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
}

.quality-128 {
  background: rgba(255, 255, 255, 0.1);
  color: #888;
}

.no-results, .loading {
  text-align: center;
  padding: 40px 20px;
  color: #aaa;
}

.no-results p, .loading p {
  margin: 0;
  font-size: 14px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.page-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 107, 107, 0.3);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-btn svg {
  width: 20px;
  height: 20px;
}

.page-info {
  font-size: 14px;
  color: #ccc;
  min-width: 50px;
  text-align: center;
}

@media (max-width: 768px) {
  .music-player {
    flex-direction: column;
    padding: 24px;
    height: auto;
    min-height: calc(100vh - 20px);
  }
  
  .playlist {
    width: 100%;
    max-height: none;
  }
  
  .album-cover {
    width: 180px;
    height: 180px;
  }
}
</style>
