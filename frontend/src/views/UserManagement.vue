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
      
      <div class="users-grid">
        <div 
          v-for="user in filteredUsers" 
          :key="user.id" 
          class="user-card"
        >
          <div class="user-info">
            <div class="user-avatar">
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
            <div class="user-details">
              <h3 class="username">{{ user.username }}</h3>
              <p class="email">{{ user.email || '未设置邮箱' }}</p>
              <p class="name">{{ user.first_name }} {{ user.last_name }}</p>
              <p class="date">加入时间: {{ formatDate(user.date_joined) }}</p>
              <p class="role">{{ user.is_staff ? '管理员' : '普通用户' }}</p>
            </div>
          </div>
          <div class="user-actions">
            <button class="edit-btn" @click="openEditModal(user)">编辑</button>
            <button class="delete-btn" @click="confirmDeleteUser(user.id)">删除</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载指示器 -->
    <div v-if="loading" class="loading">加载中...</div>
    
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
              :required="!isEditing"
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
            <button type="submit" class="save-btn">保存</button>
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
        const response = await userAPI.getUsers()
        this.users = response.data
        this.filteredUsers = response.data
      } catch (error) {
        console.error('加载用户失败:', error)
        alert('加载用户失败')
      } finally {
        this.loading = false
      }
    },
    filterUsers() {
      if (!this.searchQuery) {
        this.filteredUsers = this.users
      } else {
        const query = this.searchQuery.toLowerCase()
        this.filteredUsers = this.users.filter(user => 
          user.username.toLowerCase().includes(query) || 
          user.email.toLowerCase().includes(query) ||
          `${user.first_name} ${user.last_name}`.toLowerCase().includes(query)
        )
      }
    },
    openCreateModal() {
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
      this.isEditing = true
      this.editingUserId = user.id
      this.form = {
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        password: '',
        is_staff: user.is_staff
      }
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    closeDeleteConfirm() {
      this.showDeleteConfirm = false
    },
    async submitUser() {
      try {
        if (this.isEditing) {
          await userAPI.updateUser(this.editingUserId, this.form)
        } else {
          await userAPI.createUser(this.form)
        }
        await this.loadUsers()
        this.closeModal()
      } catch (error) {
        console.error('保存用户失败:', error)
        alert('保存用户失败: ' + (error.response?.data || '未知错误'))
      }
    },
    confirmDeleteUser(userId) {
      this.editingUserId = userId
      this.showDeleteConfirm = true
    },
    async deleteUser() {
      try {
        await userAPI.deleteUser(this.editingUserId)
        await this.loadUsers()
        this.closeDeleteConfirm()
      } catch (error) {
        console.error('删除用户失败:', error)
        alert('删除用户失败')
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

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.user-card {
  background: white;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}

.user-info {
  padding: 20px;
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff, #34c759);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 16px;
}

.user-details {
  text-align: left;
}

.username {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 6px 0;
  color: #1d1d1f;
}

.email {
  font-size: 14px;
  color: #86868b;
  margin: 0 0 4px 0;
}

.name {
  font-size: 14px;
  color: #86868b;
  margin: 0 0 4px 0;
}

.date {
  font-size: 12px;
  color: #8e8e93;
  margin: 6px 0;
}

.role {
  font-size: 12px;
  background-color: #f2f2f7;
  display: inline-block;
  padding: 4px 8px;
  border-radius: 20px;
  color: #646464;
}

.user-actions {
  display: flex;
  border-top: 1px solid #f2f2f7;
  padding: 12px 20px;
  gap: 10px;
}

.edit-btn, .delete-btn {
  flex: 1;
  padding: 8px 0;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.edit-btn {
  background-color: #f2f2f7;
  color: #007aff;
}

.edit-btn:hover {
  background-color: #e5e5ea;
}

.delete-btn {
  background-color: #ff3b30;
  color: white;
}

.delete-btn:hover {
  background-color: #e3352d;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #86868b;
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
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 14px;
  width: 100%;
  max-width: 500px;
  padding: 0;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: modalAppear 0.3s ease-out;
}

@keyframes modalAppear {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-title {
  padding: 20px 20px 0 20px;
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
}

.form-group {
  padding: 16px 20px;
  border-bottom: 1px solid #f2f2f7;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #1d1d1f;
  font-size: 16px;
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
  color: #8e8e93;
  font-style: italic;
  margin: 0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px;
}

.cancel-btn, .save-btn {
  flex: 1;
  padding: 12px 0;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
}

.cancel-btn {
  background-color: #f2f2f7;
  color: #86868b;
  border: none;
}

.cancel-btn:hover {
  background-color: #e5e5ea;
}

.save-btn {
  background-color: #007aff;
  color: white;
  border: none;
}

.save-btn:hover {
  background-color: #0062cc;
}

.delete-btn.confirm {
  background-color: #ff3b30;
  color: white;
}

.delete-btn.confirm:hover {
  background-color: #e3352d;
}

@media (max-width: 768px) {
  .users-grid {
    grid-template-columns: 1fr;
  }
  
  .controls {
    flex-direction: column;
  }
  
  .search-input {
    min-width: 100%;
  }
}
</style>