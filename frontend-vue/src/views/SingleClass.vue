<template>
  <div class="single-class">
    <!-- 左侧：实时画面 + 数据卡片 -->
    <div class="left-panel">
      <!-- 实时检测画面 -->
      <div class="live-viewer">
        <img
          v-if="store.liveImageUrl"
          :src="store.liveImageUrl"
          alt="Live Detection"
        />
        <div v-else class="placeholder">
          <span>等待图片检测...</span>
        </div>
        <div class="overlay">{{ store.wsConnected ? '图片轮询中' : '已断开' }}</div>
      </div>

      <!-- 实时卡片 -->
      <AttendanceCards :stats="store.liveStats" />
    </div>

    <!-- 右侧：图表面板 -->
    <div class="right-panel">
      <div class="chart-grid">
        <div class="chart-box chart-line">
          <div class="chart-title">整节课抬头率曲线</div>
          <HeadUpRateChart :timeline="store.timeline" />
        </div>

        <div class="chart-box chart-radar">
          <div class="chart-title">走神预警雷达</div>
          <WarningRadar :radar="store.radar" />
        </div>

        <div class="chart-box chart-heat">
          <div class="chart-title">课堂活跃度热力图</div>
          <ActivityHeatmap :heatmap="store.heatmap" />
        </div>

        <div class="chart-box chart-stats">
          <div class="chart-title">检测统计</div>
          <DetectionStats :stats="store.liveStats" :timeline="store.timeline" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useClassroomStore } from '../stores/classroom'
import AttendanceCards from '../components/AttendanceCards.vue'
import HeadUpRateChart from '../components/HeadUpRateChart.vue'
import WarningRadar from '../components/WarningRadar.vue'
import ActivityHeatmap from '../components/ActivityHeatmap.vue'
import DetectionStats from '../components/DetectionStats.vue'

const store = useClassroomStore()

onMounted(() => {
  if (store.activeClassroom) {
    store.refreshAll()
  }
})
</script>

<style scoped>
.single-class {
  flex: 1;
  display: flex;
  gap: 0;
  overflow: hidden;
}

/* ---- 左面板 ---- */
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #1a1e2a;
  min-width: 0;
}

.live-viewer {
  flex: 1;
  position: relative;
  background: #0c1018;
  display: flex; align-items: center; justify-content: center;
  min-height: 300px;
}
.live-viewer img {
  width: 100%; height: 100%; object-fit: contain;
}
.live-viewer .placeholder {
  color: #5a6070; font-size: 14px;
}
.live-viewer .overlay {
  position: absolute; top: 10px; left: 16px;
  font-size: 12px; color: #5a6070;
  background: rgba(0,0,0,0.5);
  padding: 4px 10px; border-radius: 3px;
}

/* ---- 右面板 ---- */
.right-panel {
  width: 560px;
  flex-shrink: 0;
  background: #0d111a;
  overflow-y: auto;
  padding: 8px;
}

.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 8px;
  min-height: 100%;
}

.chart-box {
  background: #101520;
  border: 1px solid #1a1e2a;
  border-radius: 6px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  min-height: 240px;
}

.chart-title {
  font-size: 12px;
  color: #5a6378;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #151a26;
}

.chart-line  { grid-column: 1 / -1; min-height: 260px; }
.chart-radar { min-height: 280px; }
.chart-heat  { min-height: 280px; }
.chart-stats { min-height: 280px; }
</style>
