<template>
  <div class="cards-row">
    <div class="card card-phone">
      <div class="label">手机使用</div>
      <div class="value">{{ display.phone }}</div>
      <div class="sub">当前检测到使用手机的人数</div>
    </div>
    <div class="card card-front">
      <div class="label">前排人数</div>
      <div class="value">{{ display.front }}</div>
      <div class="sub">坐于前排区域的学生</div>
    </div>
    <div class="card card-attention">
      <div class="label">抬头率</div>
      <div class="value">{{ display.attention }}%</div>
      <div class="sub">当前课堂专注度指标</div>
    </div>
    <div class="card card-total">
      <div class="label">出勤人数</div>
      <div class="value">{{ display.total }}</div>
      <div class="sub">当前画面检测到的总人数</div>
    </div>
    <div class="card card-rate">
      <div class="label">前排占比</div>
      <div class="value">{{ display.frontRate }}%</div>
      <div class="sub">前排人数 / 总人数</div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  stats: { type: Object, default: () => ({}) },
})

const display = reactive({
  phone: 0, front: 0, attention: 100, total: 0, frontRate: 0,
})

function animateValue(key, target) {
  const start = display[key]
  const duration = 300
  const startTime = performance.now()
  function step(now) {
    const elapsed = now - startTime
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - (1 - progress) ** 3
    const current = start + (target - start) * eased
    display[key] = typeof target === 'number' && target % 1 !== 0
      ? Math.round(current * 10) / 10
      : Math.round(current)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

watch(() => props.stats, (val) => {
  if (!val) return
  animateValue('phone', val.phone_count ?? 0)
  animateValue('front', val.front_people ?? 0)
  animateValue('attention', val.attention ?? 100)
  animateValue('total', val.person_count ?? 0)
  const total = val.person_count || 0
  const front = val.front_people || 0
  animateValue('frontRate', total > 0 ? Math.round(front / total * 100) : 0)
}, { deep: true, immediate: true })
</script>

<style scoped>
.cards-row {
  display: flex; gap: 8px;
  padding: 8px 12px;
  background: #0d111a;
  flex-shrink: 0;
}
.card {
  flex: 1;
  background: linear-gradient(180deg, #1e2940 0%, #162032 100%);
  border-radius: 6px;
  padding: 10px 12px 8px;
  border: 1px solid #1e2a3a;
  min-width: 0;
  text-align: center;
}
.card .label { font-size: 11px; color: #788296; margin-bottom: 4px; }
.card .value {
  font-size: 28px; font-weight: bold;
  font-family: "DIN Alternate", "Consolas", monospace;
  line-height: 1.1;
  transition: color 0.5s;
}
.card .sub { font-size: 10px; color: #4a5060; margin-top: 3px; }
.card-phone .value { color: #e0556a; }
.card-front .value { color: #5b9bd5; }
.card-attention .value { color: #56b6c2; }
.card-total .value { color: #e8c170; }
.card-rate .value { color: #8e7cc3; }
</style>
