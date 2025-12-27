<template>
  <div class="user-management">
    <h1 class="page-title">用户管理</h1>
    
    <!-- 用户列表 -->
    <div class="users-container">
      <div class="controls">
        <input 
          v-model="searchQuery" 
          placeholder="搜索用户..." 
          class="search-input"
          @input="filterUsers"
        />
        <button class="add-user-btn" @click="openCreateModal">添加用户</button>
      </div>
      
      <!-- 表格形式的用户列表 -->
      <div class="users-table-container" v-if="filteredUsers.length > 0">
        <table class="users-table">
          <thead>
            <tr>
              <th>用户名</th>
              <th>邮箱</th>
              <th>姓名</th>
              <th>加入时间</th>
              <th>角色</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(user, index) in filteredUsers" 
              :key="user.id || index"
              class="user-row"
            >
              <td class="username">{{ user && user.username ? user.username : '未设置用户名' }}</td>
              <td class="email">{{ user && user.email ? user.email : '未设置邮箱' }}</td>
              <td class="name">{{ user && (user.first_name || user.last_name) ? (user.first_name || '') + ' ' + (user.last_name || '') : '' }}</td>
              <td class="date">{{ user ? formatDate(user.date_joined) : '' }}</td>
              <td class="role">{{ user && user.is_staff ? '管理员' : '普通用户' }}</td>
              <td class="actions">
                <select class="action-select" @change="handleAction($event, user)">
                  <option value="" disabled selected>操作</option>
                  <option :value="'edit'">编辑</option>
                  <option :value="'delete'">删除</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 加载指示器 -->
    <div v-if="loading" class="loading">加载中...</div>
    
    <!-- 无数据提示 -->
    <div v-if="!loading && filteredUsers.length === 0 && users.length === 0" class="no-data">
      暂无用户数据
    </div>
    
    <div v-if="!loading && filteredUsers.length === 0 && users.length > 0" class="no-data">
      没有找到匹配的用户
    </div>
    
    <!-- 模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">{{ isEditing ? '编辑用户' : '添加用户' }}</h2>
        <form @submit.prevent="submitUser">
          <div class="form-group">
            <label>用户名</label>
            <input 
              v-model="form.username" 
              type="text" 
              required 
              class="form-input"
              :disabled="isEditing"
            />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input 
              v-model="form.email" 
              type="email" 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>名字</label>
            <input 
              v-model="form.first_name" 
              type="text" 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>姓氏</label>
            <input 
              v-model="form.last_name" 
              type="text" 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input 
              v-if="!isEditing"
              v-model="form.password" 
              type="password" 
              required
              class="form-input"
            />
            <p v-else class="password-placeholder">密码保持不变</p>
          </div>
          <div class="form-group">
            <label>
              <input 
                v-model="form.is_staff" 
                type="checkbox"
              />
              管理员权限
            </label>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeModal">取消</button>
            <button type="submit" class="save-btn">{{ isEditing ? '更新' : '创建' }}</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 确认删除模态框 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="closeDeleteConfirm">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">确认删除</h2>
        <p>确定要删除这个用户吗？此操作不可撤销。</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="closeDeleteConfirm">取消</button>
          <button class="delete-btn confirm" @click="deleteUser">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { userAPI } from '@/api'

export default {
  name: 'UserManagement',
  data() {
    return {
      users: [],
      filteredUsers: [],
      loading: false,
      searchQuery: '',
      showModal: false,
      showDeleteConfirm: false,
      isEditing: false,
      editingUserId: null,
      form: {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_staff: false
      }
    }
  },
  async created() {
    await this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        console.log('正在获取用户列表...')
        const response = await userAPI.getUsers()
        console.log('API响应数据:', response.data)
        
        // 确保数据是数组格式
        const usersData = Array.isArray(response.data) ? response.data : (response.data?.results || []);
        console.log('处理后的用户数据:', usersData)
        
        this.users = usersData;
        this.filteredUsers = [...this.users]; // 确保复制数组
        
        console.log('设置后的users:', this.users)
        console.log('设置后的filteredUsers:', this.filteredUsers)
      } catch (error) {
        console.error('加载用户失败:', error)
        console.error('错误详情:', error.response || error.message)
        // 尝试获取错误响应
        if (error.response) {
          console.error('响应状态:', error.response.status)
          console.error('响应数据:', error.response.data)
        }
        alert(`加载用户失败: ${error.message || '未知错误'}`)
        // 即使出错也要隐藏加载状态
        this.users = []
        this.filteredUsers = []
      } finally {
        this.loading = false
      }
    },
    filterUsers() {
      console.log('执行过滤，搜索词:', this.searchQuery)
      console.log('原始用户数:', this.users.length)
      
      if (!this.searchQuery) {
        this.filteredUsers = [...this.users] // 确保复制数组
      } else {
        const query = this.searchQuery.toLowerCase()
        this.filteredUsers = this.users.filter(user => 
          user && // 确保user存在
          (user.username && user.username.toLowerCase().includes(query)) || 
          (user.email && user.email.toLowerCase().includes(query)) ||
          (`${user.first_name || ''} ${user.last_name || ''}`).toLowerCase().includes(query)
        )
      }
      console.log('过滤后的用户数:', this.filteredUsers.length)
    },
    openCreateModal() {
      console.log('打开创建用户模态框')
      this.isEditing = false
      this.form = {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_staff: false
      }
      this.showModal = true
    },
    openEditModal(user) {
      console.log('打开编辑用户模态框', user)
      this.isEditing = true
      this.editingUserId = user.id
      this.form = {
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        // 编辑时不需要设置密码字段
        is_staff: user.is_staff || false
      }
      this.showModal = true
    },
    closeModal() {
      console.log('关闭模态框')
      this.showModal = false
    },
    closeDeleteConfirm() {
      console.log('关闭删除确认框')
      this.showDeleteConfirm = false
    },
    handleAction(event, user) {
      const action = event.target.value;
      event.target.value = ''; // 重置选择框
      
      if (action === 'edit') {
        this.openEditModal(user);
      } else if (action === 'delete') {
        this.confirmDeleteUser(user.id);
      }
    },
    async submitUser() {
      console.log('提交用户数据', this.form)
      try {
        if (this.isEditing) {
          console.log('更新用户', this.editingUserId)
          // 在编辑模式下，创建一个不包含密码的用户数据对象
          const userUpdateData = { ...this.form };
          if (!userUpdateData.password) {
            delete userUpdateData.password;
          }
          await userAPI.updateUser(this.editingUserId, userUpdateData)
        } else {
          console.log('创建新用户')
          await userAPI.createUser(this.form)
        }
        await this.loadUsers()
        this.closeModal()
        // 重置表单
        this.form = {
          username: '',
          email: '',
          first_name: '',
          last_name: '',
          password: '',
          is_staff: false
        }
      } catch (error) {
        console.error('保存用户失败:', error)
        console.error('错误详情:', error.response || error.message)
        if (error.response) {
          console.error('响应状态:', error.response.status)
          console.error('响应数据:', error.response.data)
          alert(`保存用户失败: ${JSON.stringify(error.response.data)}`)
        } else {
          alert('保存用户失败: ' + error.message || '未知错误')
        }
      }
    },
    confirmDeleteUser(userId) {
      console.log('确认删除用户', userId)
      this.editingUserId = userId
      this.showDeleteConfirm = true
    },
    async deleteUser() {
      console.log('删除用户', this.editingUserId)
      try {
        await userAPI.deleteUser(this.editingUserId)
        await this.loadUsers()
        this.closeDeleteConfirm()
      } catch (error) {
        console.error('删除用户失败:', error)
        console.error('错误详情:', error.response || error.message)
        console.error('错误详情:', error.response || error.message)
        alert('删除用户失败: ' + error.message || '未知错误')
      }
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.user-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.debug-info {
  padding: 10px;
  background-color: #f0f0f0;
  margin-bottom: 20px;
  border-radius: 4px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #1d1d1f;
  text-align: left;
}

.controls {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 250px;
  padding: 10px 14px;
  border: 1px solid #d2d2d7;
  border-radius: 10px;
  font-size: 16px;
  background-color: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.search-input:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.add-user-btn {
  padding: 10px 20px;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-user-btn:hover {
  background-color: #0062cc;
}

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border-radius: 12px;
  overflow: hidden;
}

.users-table th,
.users-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e6;
}

.users-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #1d1d1f;
}

.user-row:hover {
  background-color: #f8f9fa;
}

.action-select {
  padding: 6px 10px;
  border: 1px solid #d2d2d7;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  min-width: 80px;
}

.action-select:focus {
  outline: none;
  border-color: #007aff;
}

.loading,
.no-data {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #636366;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 20px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #d2d2d7;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.password-placeholder {
  font-style: italic;
  color: #8e8e93;
  margin: 8px 0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn,
.save-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn {
  background-color: #e0e0e6;
  color: #1d1d1f;
}

.cancel-btn:hover {
  background-color: #d2d2d7;
}

.save-btn {
  background-color: #007aff;
  color: white;
}

.save-btn:hover {
  background-color: #0062cc;
}

@media (max-width: 768px) {
  .users-table {
    font-size: 14px;
  }
  
  .users-table th,
  .users-table td {
    padding: 8px;
  }
  
  .controls {
    flex-direction: column;
  }
}
</style>