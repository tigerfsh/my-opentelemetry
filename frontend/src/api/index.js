import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 将空字符串转换为null
api.interceptors.request.use(
  config => {
    // 处理请求参数，将空字符串转换为null
    if (config.data) {
      config.data = convertEmptyStringsToNull(config.data);
    }
    
    // 如果是GET请求，处理params中的空字符串
    if (config.params) {
      config.params = convertEmptyStringsToNull(config.params);
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

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

// 递归函数：将对象或数组中的空字符串转换为null
function convertEmptyStringsToNull(obj) {
  if (obj === null || obj === undefined) {
    return obj;
  }
  
  if (typeof obj === 'string') {
    return obj === '' ? null : obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => convertEmptyStringsToNull(item));
  }
  
  if (typeof obj === 'object') {
    const result = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        result[key] = convertEmptyStringsToNull(obj[key]);
      }
    }
    return result;
  }
  
  return obj;
}

export const userAPI = {
  // 获取用户列表
  getUsers: (params = {}) => api.get('/users/', { params }),
  
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