<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, markRaw } from 'vue'
import * as echarts from 'echarts'
import { fetchHeatmap } from '../api'

const props = defineProps({
  room: { type: String, required: true },
})

const chartRef = ref(null)
let chart = null
let resizeObserver = null
let pollTimer = null

function initChart() {
  if (!chartRef.value) return
  chart = markRaw(echarts.init(chartRef.value))
  resizeObserver = new ResizeObserver(() => chart?.resize())
  resizeObserver.observe(chartRef.value)
}

async function refresh() {
  try {
    const data = await fetchHeatmap(props.room)
    updateChart(data)
  } catch { /* */ }
}

function updateChart(data) {
  if (!chart) return
  const grid = data?.grid || []
  const rows = grid.length
  const cols = grid[0]?.length || 0
  const hm = []
  let maxVal = 0
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const v = Math.round(grid[r][c] * 10) / 10
      hm.push([c, r, v])
      if (v > maxVal) maxVal = v
    }
  }
  const rowLabels = []
  for (let r = 0; r < rows; r++) {
    if (r < 3) rowLabels.push('前排')
    else if (r >= 7) rowLabels.push('后排')
    else rowLabels.push('中排')
  }

  chart.setOption({
    tooltip: {
      position: 'top',
      backgroundColor: 'rgba(20,24,40,0.95)',
      borderColor: '#2a3040',
      textStyle: { color: '#c8cdd4', fontSize: 11 },
    },
    grid: { top: 4, right: 8, bottom: 4, left: 36 },
    xAxis: {
      type: 'category',
      data: Array.from({ length: cols }, (_, i) => `${i + 1}`),
      axisLabel: { color: '#5a6070', fontSize: 8 },
      axisLine: { show: false },
      axisTick: { show: false },
      position: 'top',
    },
    yAxis: {
      type: 'category',
      data: rowLabels,
      axisLabel: { color: '#5a6070', fontSize: 8 },
      axisLine: { show: false },
      axisTick: { show: false },
      inverse: true,
    },
    visualMap: {
      show: false,
      min: 0,
      max: Math.max(maxVal, 1),
      inRange: {
        color: ['#0d111a', '#1a3a4a', '#1e5a5e', '#2a7a5e', '#56b6c2', '#8ed6c4', '#e8c170', '#e0556a'],
      },
    },
    series: [{
      type: 'heatmap',
      data: hm,
      label: { show: false },
      itemStyle: { borderColor: '#151a26', borderWidth: 1 },
    }],
  }, true)
}

onMounted(() => {
  initChart()
  refresh()
  pollTimer = setInterval(refresh, 1600)
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.chart-container { flex: 1; min-height: 220px; }
</style>
