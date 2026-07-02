<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, markRaw } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  timeline: { type: Object, default: () => ({ points: [] }) },
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
  const points = props.timeline?.points || []
  const labels = points.map((_, i) => i + 1)
  const attentionData = points.map(p => p.attention ?? 100)
  const frontRateData = points.map(p => p.front_rate ?? 0)

  // 阈值参考线
  const threshold80 = Array(labels.length).fill(80)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20,24,40,0.95)',
      borderColor: '#2a3040',
      textStyle: { color: '#c8cdd4', fontSize: 12 },
    },
    legend: {
      data: ['抬头率', '前排占比', '警戒线(80%)'],
      bottom: 0,
      textStyle: { color: '#788296', fontSize: 10 },
    },
    grid: {
      top: 12, right: 16, bottom: 30, left: 40,
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#1a1e2a' } },
      axisTick: { show: false },
      axisLabel: {
        color: '#5a6070',
        fontSize: 10,
        interval: Math.max(1, Math.floor(labels.length / 10) - 1),
        formatter: (v, i) => points[i]?.time_str || v,
      },
    },
    yAxis: {
      type: 'value',
      min: 0, max: 100,
      splitLine: { lineStyle: { color: '#151a26' } },
      axisLabel: { color: '#5a6070', fontSize: 10, formatter: '{value}%' },
    },
    series: [
      {
        name: '抬头率',
        type: 'line',
        data: attentionData,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#56b6c2', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(86,182,194,0.15)' },
            { offset: 1, color: 'rgba(86,182,194,0.01)' },
          ]),
        },
      },
      {
        name: '前排占比',
        type: 'line',
        data: frontRateData,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#8e7cc3', width: 1.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(142,124,195,0.1)' },
            { offset: 1, color: 'rgba(142,124,195,0.01)' },
          ]),
        },
      },
      {
        name: '警戒线(80%)',
        type: 'line',
        data: threshold80,
        symbol: 'none',
        lineStyle: { color: '#e0556a', width: 1, type: 'dashed' },
        itemStyle: { opacity: 0.5 },
        silent: true,
      },
    ],
  }, true)
}

watch(() => props.timeline, updateChart, { deep: true })

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
.chart-container { flex: 1; min-height: 200px; }
</style>
