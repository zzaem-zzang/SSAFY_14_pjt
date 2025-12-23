<template>
  <div ref="splineContainer" class="spline-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Application } from '@splinetool/runtime'

const splineContainer = ref(null)
let splineApp = null

onMounted(async () => {
  if (splineContainer.value) {
    try {
      const canvas = document.createElement('canvas')
      canvas.style.width = '100%'
      canvas.style.height = '100%'
      canvas.style.display = 'block'
      
      splineContainer.value.appendChild(canvas)
      
      splineApp = new Application(canvas)
      await splineApp.load('https://prod.spline.design/WURCBmJbmx9BOC8p/scene.splinecode')
      
      console.log('Spline scene loaded successfully')
    } catch (error) {
      console.error('Spline loading error:', error)
    }
  }
})

onBeforeUnmount(() => {
  if (splineApp) {
    splineApp.dispose()
    splineApp = null
  }
})
</script>

<style scoped>
.spline-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
}

.spline-container canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
  object-fit: cover;
  pointer-events: auto;
}
</style>