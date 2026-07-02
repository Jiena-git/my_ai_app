<template>
  <div class="app-shell">
    <!-- 顶部栏 -->
    <header>
      <span class="title">Smart Classroom Monitor</span>
      <span class="info">{{ clock }}</span>
    </header>

    <!-- 工具栏 -->
    <div class="toolbar">
      <label>Classroom</label>
      <select v-model="selectedRoom" @change="onRoomChange">
        <option v-for="r in store.classrooms" :key="r.id" :value="r.id">{{ r.name }}</option>
      </select>

      <div class="spacer"></div>

      <!-- 视图切换 -->
      <div class="view-tabs">
        <button
          :class="{ active: store.viewMode === 'single' }"
          @click="switchView('single')"
        >单班级</button>
        <button
          :class="{ active: store.viewMode === 'compare' }"
          @click="switchView('compare')"
        >多班级对比</button>
      </div>

      <label style="margin-left:16px">Model: YOLOv8s</label>
      <span class="ws-dot" :class="{ green: store.wsConnected, red: !store.wsConnected }"></span>
      <span class="ws-label">{{ store.wsConnected ? '检测中' : 'Offline' }}</span>
    </div>

    <!-- 主内容区 -->
    <div class="main-area">
      <router-view />
    </div>

    <!-- 底部状态栏 -->
    <footer>
      <span>
        <span class="dot" :class="store.wsConnected ? 'green' : 'red'"></span>
        {{ store.wsConnected ? 'Running' : 'Disconnected' }}
      </span>
      <span>Smart Classroom Monitor v3.0 · Vue3 + ECharts</span>
      <span>{{ clock }}</span>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useClassroomStore } from './stores/classroom'

const store = useClassroomStore()
const router = useRouter()
const clock = ref('--:--:--')
const selectedRoom = ref('')

let clockTimer = null

function updateClock() {
  clock.value = new Date().toLocaleTimeString()
}

function onRoomChange() {
  store.switchClassroom(selectedRoom.value)
}

function switchView(mode) {
  store.viewMode = mode
  if (mode === 'single') {
    router.push('/')
  } else {
    router.push('/compare')
    store.refreshCompare()
  }
}

onMounted(async () => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  await store.init()
  if (store.classrooms.length > 0) {
    selectedRoom.value = store.activeClassroom
    store.connectWS(store.activeClassroom)
    store.startPolling()
  }
})

onUnmounted(() => {
  clearInterval(clockTimer)
  store.destroy()
})
</script>

<style>
/* ========== Shell 布局 ========== */
.app-shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0a0e1a;
  color: #c8cdd4;
}

/* ========== Header ========== */
header {
  height: 46px; line-height: 46px;
  background: #0d1018;
  padding: 0 20px;
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #1a1e2a;
  flex-shrink: 0;
}
header .title { font-size: 18px; font-weight: bold; color: #e0e4ea; letter-spacing: 1px; }
header .info { font-size: 12px; color: #8a8f9a; }

/* ========== Toolbar ========== */
.toolbar {
  padding: 8px 20px;
  background: #0d111a;
  display: flex; align-items: center; gap: 16px;
  border-bottom: 1px solid #151a26;
  flex-shrink: 0;
}
.toolbar label { font-size: 13px; color: #8a8f9a; }
.toolbar select {
  padding: 4px 12px; font-size: 13px;
  background: #1a1f2e; color: #c8cdd4;
  border: 1px solid #2a3040; border-radius: 3px; outline: none;
}
.toolbar .spacer { flex: 1; }
.toolbar .view-tabs { display: flex; gap: 0; }
.toolbar .view-tabs button {
  padding: 5px 14px;
  font-size: 12px;
  background: #1a1f2e;
  color: #8a8f9a;
  border: 1px solid #2a3040;
  cursor: pointer;
  transition: all 0.2s;
}
.toolbar .view-tabs button:first-child { border-radius: 3px 0 0 3px; }
.toolbar .view-tabs button:last-child { border-radius: 0 3px 3px 0; }
.toolbar .view-tabs button.active {
  background: #2a5080;
  color: #fff;
  border-color: #3a6fa0;
  font-weight: bold;
}
.ws-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.ws-dot.green { background: #4dcb7b; }
.ws-dot.red { background: #e0556a; }
.ws-label { font-size: 12px; color: #8a8f9a; }

/* ========== Main area ========== */
.main-area {
  flex: 1;
  overflow: hidden;
  display: flex;
}

/* ========== Footer ========== */
footer {
  height: 28px; line-height: 28px;
  background: #0a0c12;
  padding: 0 20px;
  font-size: 11px; color: #4a5060;
  display: flex; justify-content: space-between;
  border-top: 1px solid #151924;
  flex-shrink: 0;
}
footer .dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; margin-right: 4px; }
footer .dot.green { background: #4dcb7b; }
footer .dot.red { background: #e0556a; }
</style>
