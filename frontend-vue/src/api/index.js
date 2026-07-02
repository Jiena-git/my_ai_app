const API = ''

export async function fetchTimeline(classroom) {
  const res = await fetch(`${API}/api/timeline?classroom=${encodeURIComponent(classroom)}`)
  return res.json()
}

export async function fetchHeatmap(classroom) {
  const res = await fetch(`${API}/api/heatmap?classroom=${encodeURIComponent(classroom)}`)
  return res.json()
}

export async function fetchRadar(classroom) {
  const res = await fetch(`${API}/api/radar?classroom=${encodeURIComponent(classroom)}`)
  return res.json()
}

export async function fetchAllSummaries() {
  const res = await fetch(`${API}/api/classrooms/summary`)
  return res.json()
}

export async function fetchCompareTimelines() {
  const res = await fetch(`${API}/api/classrooms/compare`)
  return res.json()
}

export async function fetchClassrooms() {
  const res = await fetch(`${API}/api/classrooms/list`)
  return res.json()
}
