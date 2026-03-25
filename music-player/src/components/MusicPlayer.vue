<template>
  <div class="music-player">
    <div class="player-main">
      <div class="album-cover" :class="{ playing: isPlaying }">
        <img :src="currentSong.cover" alt="Album Cover" />
      </div>
      <div class="song-info">
        <h2 class="song-title">{{ currentSong.title }}</h2>
        <p class="song-artist">{{ currentSong.artist }}</p>
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
        <button class="btn-play" @click="togglePlay">
          <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        </button>
        <button class="btn-next" @click="nextSong">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zm2-12v12l6.5-6L8 6zm8 0v12h2V6h-2z"/></svg>
        </button>
      </div>
      <div class="volume-control">
        <svg class="volume-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
        <input type="range" min="0" max="100" v-model="volume" @input="setVolume" class="volume-slider" />
      </div>
    </div>
    <div class="playlist">
      <h3>播放列表</h3>
      <ul>
        <li 
          v-for="(song, index) in songs" 
          :key="song.id"
          :class="{ active: index === currentIndex }"
          @click="playSong(index)"
        >
          <span class="song-index">{{ index + 1 }}</span>
          <div class="song-details">
            <span class="song-name">{{ song.title }}</span>
            <span class="song-singer">{{ song.artist }}</span>
          </div>
          <span class="song-duration">{{ song.duration }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const songs = ref([
  {
    id: 1,
    title: '光年之外',
    artist: '邓紫棋',
    duration: '03:55',
    cover: 'https://p2.music.126.net/TQmF--wD4zQC_aGZ-ZLD0g==/109951166952713766.jpg',
    src: 'https://music.163.com/song/media/outer/url?id=462378761.mp3'
  },
  {
    id: 2,
    title: '演员',
    artist: '薛之谦',
    duration: '04:21',
    cover: 'https://p2.music.126.net/AGq1m83cFR7JfOB3B7Glow==/18806129305310480.jpg',
    src: 'https://music.163.com/song/media/outer/url?id=33123306.mp3'
  },
  {
    id: 3,
    title: '起风了',
    artist: '买辣椒也用券',
    duration: '04:33',
    cover: 'https://p2.music.126.net/siH6-v_1l3J7bZ7VEHH0lw==/109951163495882537.jpg',
    src: 'https://music.163.com/song/media/outer/url?id=1345976016.mp3'
  },
  {
    id: 4,
    title: '稻香',
    artist: '周杰伦',
    duration: '03:43',
    cover: 'https://p2.music.126.net/E512IQ_5D万物皆可-owjI-A==/3399246873918681.jpg',
    src: 'https://music.163.com/song/media/outer/url?id=1868532235.mp3'
  },
  {
    id: 5,
    title: '晴天',
    artist: '周杰伦',
    duration: '04:29',
    cover: 'https://p2.music.126.net/E512IQ_5D万物皆可-owjI-A==/3399246873918681.jpg',
    src: 'https://music.163.com/song/media/outer/url?id=1868532241.mp3'
  }
])

const currentIndex = ref(0)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(70)

let audio = null

const currentSong = computed(() => songs.value[currentIndex.value])

const progress = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

const initAudio = () => {
  audio = new Audio(currentSong.value.src)
  audio.volume = volume.value / 100
  
  audio.addEventListener('timeupdate', () => {
    currentTime.value = audio.currentTime
  })
  
  audio.addEventListener('loadedmetadata', () => {
    duration.value = audio.duration
  })
  
  audio.addEventListener('ended', () => {
    nextSong()
  })
}

const togglePlay = () => {
  if (isPlaying.value) {
    audio.pause()
  } else {
    audio.play()
  }
  isPlaying.value = !isPlaying.value
}

const playSong = (index) => {
  currentIndex.value = index
  audio.src = currentSong.value.src
  audio.play()
  isPlaying.value = true
}

const prevSong = () => {
  currentIndex.value = (currentIndex.value - 1 + songs.value.length) % songs.value.length
  audio.src = currentSong.value.src
  if (isPlaying.value) audio.play()
}

const nextSong = () => {
  currentIndex.value = (currentIndex.value + 1) % songs.value.length
  audio.src = currentSong.value.src
  if (isPlaying.value) audio.play()
}

const seek = (e) => {
  const rect = e.target.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  audio.currentTime = percent * duration.value
}

const setVolume = () => {
  audio.volume = volume.value / 100
}

const formatTime = (time) => {
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

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
  max-width: 900px;
  margin: 0 auto;
}

.player-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.album-cover {
  width: 250px;
  height: 250px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
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

.song-info {
  text-align: center;
  color: #fff;
}

.song-title {
  font-size: 24px;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.song-artist {
  font-size: 16px;
  color: #aaa;
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
  color: #888;
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

.controls button:hover {
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

.btn-play:hover {
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
  width: 280px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  color: #fff;
}

.playlist h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #ffd93d;
}

.playlist ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.playlist li {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.playlist li:hover {
  background: rgba(255, 255, 255, 0.1);
}

.playlist li.active {
  background: rgba(255, 107, 107, 0.2);
}

.song-index {
  width: 24px;
  font-size: 14px;
  color: #666;
}

.playlist li.active .song-index {
  color: #ff6b6b;
}

.song-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.song-name {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-singer {
  font-size: 12px;
  color: #888;
}

.song-duration {
  font-size: 12px;
  color: #666;
}

@media (max-width: 768px) {
  .music-player {
    flex-direction: column;
    padding: 24px;
  }
  
  .playlist {
    width: 100%;
  }
  
  .album-cover {
    width: 200px;
    height: 200px;
  }
}
</style>
