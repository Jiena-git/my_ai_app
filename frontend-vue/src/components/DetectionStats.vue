<template>
  <div class="stats-panel">
    <div class="stat-item">
      <span class="key">手机使用</span>
      <span class="val danger">{{ stats.phone_count ?? 0 }}</span>
    </div>
    <div class="stat-item">
      <span class="key">前排人数</span>
      <span class="val primary">{{ stats.front_people ?? 0 }}</span>
    </div>
    <div class="stat-item">
      <span class="key">总人数</span>
      <span class="val warn">{{ stats.person_count ?? 0 }}</span>
    </div>
    <div class="stat-item">
      <span class="key">抬头率</span>
      <span class="val accent">{{ stats.attention ?? 100 }}%</span>
    </div>
    <div class="stat-item">
      <span class="key">前排占比</span>
      <span class="val accent2">{{ frontRate }}%</span>
    </div>

    <div class="divider"></div>

    <div class="stat-item">
      <span class="key">数据点数</span>
      <span class="val mono">{{ pointCount }}</span>
    </div>
    <div class="stat-item">
      <span class="key">最新更新</span>
      <span class="val mono">{{ lastTime }}</span>
    </div>
    <div class="stat-item">
      <span class="key">平均抬头率</span>
      <span class="val accent">{{ avgAttention }}%</span>
    </div>
    <div class="stat-item">
      <span class="key">峰值人数</span>
      <span class="val warn">{{ maxPerson }}</span>
    </div>

    <!-- 状态指示 -->
    <div class="divider"></div>
    <div class="status-row">
      <span class="dot" :class="attentionLevel.color"></span>
      <span>{{ attentionLevel.text }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, default: () => ({}) },
  timeline: { type: Object, default: () => ({ points: [] }) },
})

const frontRate = computed(() => {
  const t = props.stats.person_count || 0
  const f = props.stats.front_people || 0
  return t > 0 ? Math.round(f / t * 100) : 0
})

const pointCount = computed(() => props.timeline?.points?.length || 0)

const lastTime = computed(() => {
  const pts = props.timeline?.points || []
  return pts.length > 0 ? pts[pts.length - 1].time_str : '--:--:--'
})

const avgAttention = computed(() => {
  const pts = props.timeline?.points || []
  if (pts.length === 0) return 100
  const sum = pts.reduce((s, p) => s + (p.attention || 100), 0)
  return Math.round(sum / pts.length)
})

const maxPerson = computed(() => {
  const pts = props.timeline?.points || []
  if (pts.length === 0) return 0
  return Math.max(...pts.map(p => p.person_count || 0))
})

const attentionLevel = computed(() => {
  const a = avgAttention.value
  if (a >= 85) return { color: 'green', text: '课堂专注度良好' }
  if (a >= 70) return { color: 'yellow', text: '课堂专注度一般' }
  return { color: 'red', text: '⚠ 专注度偏低' }
})
</script>

<style scoped>
.stats-panel {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 8px;
  background: #0d111a;
  border-radius: 3px;
  font-size: 12px;
}
.stat-item .key { color: #788296; }
.stat-item .val { font-weight: bold; font-family: "Consolas", monospace; }
.val.danger { color: #e0556a; }
.val.primary { color: #5b9bd5; }
.val.warn { color: #e8c170; }
.val.accent { color: #56b6c2; }
.val.accent2 { color: #8e7cc3; }
.val.mono { color: #8a8f9a; font-size: 11px; }

.divider {
  height: 1px;
  background: #151a26;
  margin: 4px 0;
}

.status-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: #c8cdd4; padding: 4px 8px;
}
.status-row .dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.dot.green { background: #4dcb7b; }
.dot.yellow { background: #e8c170; }
.dot.red { background: #e0556a; }
</style>
