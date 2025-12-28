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
  
  // 获取用户简介
  getUserProfile: (id) => api.get(`/users/${id}/profile/`),
  
  // 更新用户简介（完整简介对象）
  updateUserProfile: (id, profileData) => {
    // 如果是FormData对象，需要设置content-type为multipart/form-data
    if (profileData instanceof FormData) {
      return api.put(`/users/${id}/profile/`, profileData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
    } else {
      // 普通对象仍然使用application/json
      return api.put(`/users/${id}/profile/`, profileData);
    }
  },
  
  // 更新用户简介（包含文件上传）
  updateUserProfileWithFile: (id, formData) => api.put(`/users/${id}/profile/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    }
  }),
}