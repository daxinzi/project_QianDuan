<script setup>
import MusicPlayer from './components/MusicPlayer.vue'
</script>

<template>
  <MusicPlayer />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}

#app {
  width: 100%;
}
</style>
