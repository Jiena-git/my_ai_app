import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  fetchTimeline, fetchHeatmap, fetchRadar,
  fetchAllSummaries, fetchCompareTimelines, fetchClassrooms,
} from '../api'

export const useClassroomStore = defineStore('classroom', () => {
  // ---- 教室列表 ----
  const classrooms = ref([])
  const activeClassroom = ref('')

  // ---- 实时检测数据（WebSocket 推送） ----
  const liveStats = ref({
    person_count: 0,
    phone_count: 0,
    front_people: 0,
    attention: 100,
    front_rate: 0,
  })
  const liveImageUrl = ref(null)
  const wsConnected = ref(false)

  // ---- 图表数据 ----
  const timeline = ref({ points: [] })
  const heatmap = ref({ grid: [], rows: 10, cols: 10 })
  const radar = ref({ dimensions: [] })
  const allSummaries = ref({})
  const compareTimelines = ref({})

  // ---- 视图模式 ----
  const viewMode = ref('single') // 'single' | 'compare'
  const compareClassrooms = ref([]) // 对比时选中的教室

  let ws = null
  let pollTimer = null

  // ---- 初始化 ----
  async function init() {
    const list = await fetchClassrooms()
    classrooms.value = list
    if (list.length > 0) {
      activeClassroom.value = list[0].id
    }
  }

  // ---- WebSocket 连接 ----
  function connectWS(room) {
    if (ws) {
      ws.onclose = null
      ws.onerror = null
      ws.close()
    }

    // WebSocket 直连后端 8000 端口，不受前端 Vite 端口影响
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${location.hostname}:8000/api/ws?classroom=${encodeURIComponent(room)}`
    ws = new WebSocket(url)
    ws.binaryType = 'arraybuffer'

    ws.onopen = () => { wsConnected.value = true }
    ws.onmessage = (e) => {
      if (e.data instanceof ArrayBuffer) {
        const blob = new Blob([e.data], { type: 'image/jpeg' })
        if (liveImageUrl.value) URL.revokeObjectURL(liveImageUrl.value)
        liveImageUrl.value = URL.createObjectURL(blob)
      } else {
        liveStats.value = JSON.parse(e.data)
      }
    }
    ws.onclose = () => {
      wsConnected.value = false
      ws = null
      setTimeout(() => connectWS(activeClassroom.value), 2000)
    }
    ws.onerror = () => { if (ws) ws.close() }
  }

  // ---- 数据轮询（图表用） ----
  function startPolling() {
    stopPolling()
    pollTimer = setInterval(refreshAll, 1600)
    refreshAll()
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  async function refreshAll() {
    const room = activeClassroom.value
    if (!room) return
    try {
      const [tl, hm, rd] = await Promise.all([
        fetchTimeline(room),
        fetchHeatmap(room),
        fetchRadar(room),
      ])
      timeline.value = tl
      heatmap.value = hm
      radar.value = rd
    } catch {
      // 静默失败
    }
  }

  async function refreshSummaries() {
    try {
      allSummaries.value = await fetchAllSummaries()
    } catch { /* */ }
  }

  async function refreshCompare() {
    try {
      const [sums, ctl] = await Promise.all([
        fetchAllSummaries(),
        fetchCompareTimelines(),
      ])
      allSummaries.value = sums
      compareTimelines.value = ctl
    } catch { /* */ }
  }

  function switchClassroom(room) {
    activeClassroom.value = room
    connectWS(room)
    refreshAll()
  }

  // ---- 清理 ----
  function destroy() {
    stopPolling()
    if (ws) {
      ws.onclose = null
      ws.close()
      ws = null
    }
    if (liveImageUrl.value) {
      URL.revokeObjectURL(liveImageUrl.value)
      liveImageUrl.value = null
    }
  }

  return {
    classrooms, activeClassroom, liveStats, liveImageUrl, wsConnected,
    timeline, heatmap, radar, allSummaries, compareTimelines,
    viewMode, compareClassrooms,
    init, connectWS, startPolling, stopPolling,
    refreshAll, refreshSummaries, refreshCompare,
    switchClassroom, destroy,
  }
})
