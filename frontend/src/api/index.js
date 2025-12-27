import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 添加响应拦截器用于调试
api.interceptors.response.use(
  response => {
    console.log(`API响应: ${response.config.url}`, response);
    return response;
  },
  error => {
    console.error(`API错误: ${error.config?.url}`, error.response || error.message);
    return Promise.reject(error);
  }
);

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
  
  // 更新用户简介（仅bio字段）- 旧接口，保留兼容性
  updateUserBio: (id, bio) => api.put(`/users/${id}/bio/`, { bio }),
  
  // 获取用户简介
  getUserProfile: (id) => api.get(`/users/${id}/profile/`),
  
  // 更新用户简介（完整简介对象）
  updateUserProfile: (id, profileData) => api.put(`/users/${id}/profile/`, profileData),
}