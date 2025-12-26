import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const userAPI = {
  // 获取用户列表
  getUsers: () => api.get('/users/'),
  
  // 获取单个用户
  getUser: (id) => api.get(`/users/${id}/`),
  
  // 创建用户
  createUser: (userData) => api.post('/users/', userData),
  
  // 更新用户
  updateUser: (id, userData) => api.put(`/users/${id}/`, userData),
  
  // 删除用户
  deleteUser: (id) => api.delete(`/users/${id}/`),
}