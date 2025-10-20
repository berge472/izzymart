import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import CheckoutView from '../views/CheckoutView.vue'
import AdminView from '../views/AdminView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'checkout',
    component: CheckoutView
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
