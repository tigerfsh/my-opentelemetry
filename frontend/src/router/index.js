import { createRouter, createWebHistory } from 'vue-router'
import UserManagement from '@/views/UserManagement.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/users'
  },
  {
    path: '/users',
    name: 'users',
    component: UserManagement
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router