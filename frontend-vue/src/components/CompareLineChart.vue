<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, markRaw } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  compareData: { type: Object, default: () => ({}) },
  rooms: { type: Array, default: () => [] },
})

const chartRef = ref(null)
let chart = null
let resizeObserver = null

const COLORS = ['#56b6c2', '#e0556a', '#e8c170', '#8e7cc3', '#5b9bd5']

function initChart() {
  if (!chartRef.value) return
  chart = markRaw(echarts.init(chartRef.value))
  resizeObserver = new ResizeObserver(() => chart?.resize())
  resizeObserver.observe(chartRef.value)
}

function updateChart() {
  if (!chart) return
  const series = props.rooms.map((room, i) => {
    const pts = props.compareData?.[room] || []
    return {
      name: `${room} 抬头率`,
      type: 'line',
      data: pts.map(p => p.attention ?? 100),
      smooth: true,
      symbol: 'none',
      lineStyle: { color: COLORS[i % COLORS.length], width: 2 },
    }
  })

  const maxLen = Math.max(...series.map(s => s.data.length), 1)
  const labels = Array.from({ length: maxLen }, (_, i) => i + 1)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20,24,40,0.95)',
      borderColor: '#2a3040',
      textStyle: { color: '#c8cdd4', fontSize: 12 },
    },
    legend: {
      data: props.rooms.map(r => `${r} 抬头率`),
      bottom: 0,
      textStyle: { color: '#788296', fontSize: 10 },
    },
    grid: { top: 12, right: 16, bottom: 30, left: 40 },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: { color: '#5a6070', fontSize: 10 },
      axisLine: { lineStyle: { color: '#1a1e2a' } },
    },
    yAxis: {
      type: 'value',
      min: 0, max: 100,
      splitLine: { lineStyle: { color: '#151a26' } },
      axisLabel: { color: '#5a6070', fontSize: 10, formatter: '{value}%' },
    },
    series,
  }, true)
}

watch([() => props.compareData, () => props.rooms], updateChart, { deep: true })

onMounted(() => { initChart(); updateChart() })
onUnmounted(() => { resizeObserver?.disconnect(); chart?.dispose() })
</script>

<style scoped>
.chart-container { flex: 1; min-height: 260px; }
</style>
