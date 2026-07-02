<template>
  <div class="compare-page">
    <!-- 班级选择器 -->
    <div class="compare-toolbar">
      <span class="hint">选择要对比的班级（点击卡片切换选中状态）：</span>
      <div class="room-chips">
        <button
          v-for="r in store.classrooms"
          :key="r.id"
          :class="{ selected: selectedRooms.includes(r.id) }"
          @click="toggleRoom(r.id)"
        >{{ r.name }}</button>
      </div>
      <span class="count">{{ selectedRooms.length }} / {{ store.classrooms.length }} 已选</span>
    </div>

    <!-- 对比内容 -->
    <div class="compare-content" v-if="selectedRooms.length > 0">
      <!-- 出勤人数卡片行 -->
      <div class="cards-compare">
        <div
          v-for="room in selectedRooms"
          :key="'card-' + room"
          class="mini-card"
        >
          <div class="room-label">{{ room }}</div>
          <div class="room-value" :style="{ color: roomColor(room) }">
            {{ summaries[room]?.person_count ?? 0 }}
          </div>
          <div class="room-sub">出勤人数</div>
          <div class="room-extra">
            抬头率 {{ summaries[room]?.attention ?? 100 }}%
          </div>
        </div>
      </div>

      <!-- 图表对比行 -->
      <div class="charts-row">
        <!-- 抬头率曲线对比 -->
        <div class="compare-chart-box">
          <div class="chart-label">整节课抬头率曲线对比</div>
          <CompareLineChart :compareData="store.compareTimelines" :rooms="selectedRooms" />
        </div>

        <!-- 雷达图对比 -->
        <div class="compare-chart-box narrow">
          <div class="chart-label">走神雷达对比</div>
          <CompareRadarChart :summaries="summaries" :rooms="selectedRooms" />
        </div>
      </div>

      <!-- 热力图对比行 -->
      <div class="heatmaps-row">
        <div
          v-for="room in selectedRooms"
          :key="'heat-' + room"
          class="heatmap-cell"
        >
          <div class="cell-label">{{ room }}</div>
          <CompareHeatmap :room="room" />
        </div>
      </div>
    </div>

    <div v-else class="empty-hint">
      请至少选择一个班级进行对比
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useClassroomStore } from '../stores/classroom'
import CompareLineChart from '../components/CompareLineChart.vue'
import CompareRadarChart from '../components/CompareRadarChart.vue'
import CompareHeatmap from '../components/CompareHeatmap.vue'

const store = useClassroomStore()
const selectedRooms = ref([])
let pollTimer = null

const summaries = computed(() => store.allSummaries || {})

const ROOM_COLORS = ['#56b6c2', '#e0556a', '#e8c170', '#8e7cc3', '#5b9bd5']

function roomColor(room) {
  const idx = store.classrooms.findIndex(r => r.id === room)
  return ROOM_COLORS[idx % ROOM_COLORS.length]
}

function toggleRoom(id) {
  const i = selectedRooms.value.indexOf(id)
  if (i >= 0) {
    if (selectedRooms.value.length > 1) {
      selectedRooms.value.splice(i, 1)
    }
  } else {
    if (selectedRooms.value.length < 5) {
      selectedRooms.value.push(id)
    }
  }
}

onMounted(() => {
  // 默认选两个班级
  if (store.classrooms.length >= 2) {
    selectedRooms.value = [store.classrooms[0].id, store.classrooms[1].id]
  } else if (store.classrooms.length === 1) {
    selectedRooms.value = [store.classrooms[0].id]
  }
  store.refreshCompare()
  pollTimer = setInterval(() => store.refreshCompare(), 1600)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.compare-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 12px;
  gap: 12px;
}

/* ---- 工具栏 ---- */
.compare-toolbar {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px;
  background: #101520;
  border: 1px solid #1a1e2a;
  border-radius: 6px;
}
.compare-toolbar .hint { font-size: 12px; color: #788296; }
.room-chips { display: flex; gap: 6px; }
.room-chips button {
  padding: 5px 14px;
  font-size: 12px;
  background: #1a1f2e;
  color: #8a8f9a;
  border: 1px solid #2a3040;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
}
.room-chips button.selected {
  background: #2a5080;
  color: #fff;
  border-color: #3a6fa0;
  font-weight: bold;
}
.count { font-size: 12px; color: #5a6070; margin-left: auto; }

/* ---- 卡片行 ---- */
.cards-compare {
  display: flex; gap: 10px;
}
.mini-card {
  flex: 1;
  background: linear-gradient(180deg, #1e2940 0%, #162032 100%);
  border: 1px solid #1e2a3a;
  border-radius: 6px;
  padding: 12px 14px;
  text-align: center;
}
.mini-card .room-label { font-size: 12px; color: #788296; margin-bottom: 4px; }
.mini-card .room-value { font-size: 36px; font-weight: bold; line-height: 1.1; }
.mini-card .room-sub { font-size: 10px; color: #5a6070; margin-top: 2px; }
.mini-card .room-extra { font-size: 11px; color: #56b6c2; margin-top: 4px; }

/* ---- 图表行 ---- */
.charts-row {
  display: flex; gap: 10px;
  min-height: 340px;
}
.compare-chart-box {
  flex: 2;
  background: #101520;
  border: 1px solid #1a1e2a;
  border-radius: 6px;
  padding: 10px;
  display: flex;
  flex-direction: column;
}
.compare-chart-box.narrow { flex: 1; }
.chart-label {
  font-size: 12px; color: #5a6378;
  letter-spacing: 1px;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #151a26;
}

/* ---- 热力图行 ---- */
.heatmaps-row {
  display: flex; gap: 10px;
  min-height: 280px;
}
.heatmap-cell {
  flex: 1;
  background: #101520;
  border: 1px solid #1a1e2a;
  border-radius: 6px;
  padding: 10px;
  display: flex;
  flex-direction: column;
}
.cell-label {
  font-size: 12px; color: #5a6378;
  letter-spacing: 1px;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #151a26;
}

.empty-hint {
  flex: 1;
  display: flex; align-items: center; justify-content: center;
  color: #5a6070; font-size: 14px;
}
</style>
