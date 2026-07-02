<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, markRaw } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  heatmap: { type: Object, default: () => ({ grid: [], rows: 10, cols: 10 }) },
})

const chartRef = ref(null)
let chart = null
let resizeObserver = null

function initChart() {
  if (!chartRef.value) return
  chart = markRaw(echarts.init(chartRef.value))
  resizeObserver = new ResizeObserver(() => chart?.resize())
  resizeObserver.observe(chartRef.value)
}

function updateChart() {
  if (!chart) return
  const grid = props.heatmap?.grid || []
  const rows = grid.length
  const cols = grid[0]?.length || 0

  // 将网格转为热力图数据 [col, row, value]
  const data = []
  let maxVal = 0
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const v = Math.round(grid[r][c] * 10) / 10
      data.push([c, r, v])
      if (v > maxVal) maxVal = v
    }
  }

  // 摄像头在教室后方 → 画面顶部=靠近黑板=前排, 画面底部=靠近摄像头=后排
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
      formatter: (params) => {
        const r = params.value[1]
        const v = params.value[2]
        const zone = r < 3 ? '前排' : r >= 7 ? '后排' : '中排'
        return `${zone} · 活跃度: ${v.toFixed(1)}`
      },
    },
    grid: { top: 8, right: 20, bottom: 8, left: 50 },
    xAxis: {
      type: 'category',
      data: Array.from({ length: cols }, (_, i) => `${i + 1}列`),
      axisLabel: { color: '#5a6070', fontSize: 9 },
      axisLine: { show: false },
      axisTick: { show: false },
      position: 'top',
    },
    yAxis: {
      type: 'category',
      data: rowLabels,
      axisLabel: { color: '#5a6070', fontSize: 9 },
      axisLine: { show: false },
      axisTick: { show: false },
      inverse: true,
    },
    visualMap: {
      show: false,
      min: 0,
      max: Math.max(maxVal, 1),
      inRange: {
        color: [
          '#0d111a',
          '#1a3a4a',
          '#1e5a5e',
          '#2a7a5e',
          '#56b6c2',
          '#8ed6c4',
          '#e8c170',
          '#e0556a',
        ],
      },
    },
    series: [{
      type: 'heatmap',
      data,
      label: { show: false },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(86,182,194,0.6)',
          borderColor: '#56b6c2',
          borderWidth: 1,
        },
      },
      itemStyle: {
        borderColor: '#151a26',
        borderWidth: 1,
      },
    }],
  }, true)
}

watch(() => props.heatmap, updateChart, { deep: true })

onMounted(() => {
  initChart()
  updateChart()
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<style scoped>
.chart-container { flex: 1; min-height: 220px; }
</style>
