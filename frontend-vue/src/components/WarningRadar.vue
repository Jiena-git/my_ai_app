<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, markRaw } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  radar: { type: Object, default: () => ({ dimensions: [] }) },
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
  const dims = props.radar?.dimensions || []
  const indicator = dims.map(d => ({
    name: d.name,
    max: d.max,
  }))
  const values = dims.map(d => d.value)

  // 预警色：超过阈值变红
  const areaColor = values.some((v, i) => {
    const threshold = indicator[i]?.max * 0.6 || 60
    return v > threshold && indicator[i]?.name !== '综合专注度'
  }) ? 'rgba(224,85,106,0.25)' : 'rgba(86,182,194,0.2)'

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(20,24,40,0.95)',
      borderColor: '#2a3040',
      textStyle: { color: '#c8cdd4', fontSize: 12 },
    },
    radar: {
      center: ['50%', '52%'],
      radius: '72%',
      indicator,
      axisName: { color: '#788296', fontSize: 10 },
      axisLine: { lineStyle: { color: '#1a1e2a' } },
      splitLine: { lineStyle: { color: '#151a26' } },
      splitArea: {
        areaStyle: { color: ['rgba(86,182,194,0.02)', 'rgba(86,182,194,0.04)'] },
      },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '当前状态',
        areaStyle: { color: areaColor },
        lineStyle: { color: '#56b6c2', width: 2 },
        itemStyle: { color: '#56b6c2' },
        symbol: 'circle',
        symbolSize: 5,
      }],
      emphasis: {
        lineStyle: { width: 3 },
        areaStyle: { color: 'rgba(86,182,194,0.35)' },
      },
    }],
  }, true)
}

watch(() => props.radar, updateChart, { deep: true })

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
