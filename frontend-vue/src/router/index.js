import { createRouter, createWebHashHistory } from 'vue-router'
import SingleClass from '../views/SingleClass.vue'
import CompareClasses from '../views/CompareClasses.vue'

const routes = [
  { path: '/', name: 'SingleClass', component: SingleClass },
  { path: '/compare', name: 'CompareClasses', component: CompareClasses },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
