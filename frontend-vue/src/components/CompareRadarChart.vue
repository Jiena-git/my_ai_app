<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, markRaw } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  summaries: { type: Object, default: () => ({}) },
  rooms: { type: Array, default: () => [] },
})

const chartRef = ref(null)
let chart = null
let resizeObserver = null

const COLORS = ['#56b6c2', '#e0556a', '#e8c170', '#8e7cc3', '#5b9bd5']

const indicator = [
  { name: '手机使用率', max: 100 },
  { name: '后排聚集度', max: 100 },
  { name: '人数波动', max: 100 },
  { name: '前排缺失', max: 100 },
  { name: '综合预警', max: 100 },
]

function initChart() {
  if (!chartRef.value) return
  chart = markRaw(echarts.init(chartRef.value))
  resizeObserver = new ResizeObserver(() => chart?.resize())
  resizeObserver.observe(chartRef.value)
}

function updateChart() {
  if (!chart) return
  const seriesData = props.rooms.map((room, i) => {
    const r = props.summaries?.[room]?.radar || {}
    return {
      name: room,
      value: [
        r.phone_rate ?? 0,
        r.back_ratio ?? 0,
        r.person_volatility ?? 0,
        r.front_engagement ?? 0,
        r.warning_index ?? 0,
      ],
    }
  })

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: {
      data: props.rooms,
      bottom: 0,
      textStyle: { color: '#788296', fontSize: 9 },
    },
    radar: {
      center: ['50%', '48%'],
      radius: '65%',
      indicator,
      axisName: { color: '#788296', fontSize: 9 },
      axisLine: { lineStyle: { color: '#1a1e2a' } },
      splitLine: { lineStyle: { color: '#151a26' } },
    },
    series: [{
      type: 'radar',
      data: seriesData.map((d, i) => ({
        ...d,
        lineStyle: { color: COLORS[i % COLORS.length], width: 2 },
        itemStyle: { color: COLORS[i % COLORS.length] },
        areaStyle: { color: COLORS[i % COLORS.length].replace(')', ',0.08)').replace('rgb', 'rgba') },
        symbol: 'circle',
        symbolSize: 3,
      })),
    }],
  }, true)
}

watch([() => props.summaries, () => props.rooms], updateChart, { deep: true })

onMounted(() => { initChart(); updateChart() })
onUnmounted(() => { resizeObserver?.disconnect(); chart?.dispose() })
</script>

<style scoped>
.chart-container { flex: 1; min-height: 260px; }
</style>
