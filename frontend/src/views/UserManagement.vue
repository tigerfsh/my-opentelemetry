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
              <th>简介</th>
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
              <td class="bio">
                <button class="bio-btn" @click="showUserProfile(user)">
                  查看简介
                </button>
              </td>
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
    
    <!-- 简介编辑模态框 -->
    <div v-if="showBioModal" class="modal-overlay" @click="closeBioModal">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">编辑简介</h2>
        <form @submit.prevent="submitBio">
          <div class="form-group">
            <label>简介</label>
            <textarea 
              v-model="bioForm.bio" 
              class="form-input"
              rows="4"
              placeholder="请输入个人简介..."
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeBioModal">取消</button>
            <button type="submit" class="save-btn">更新简介</button>
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
  
  <!-- 用户Profile详情模态框 -->
  <div v-if="showProfileModal" class="modal-overlay" @click="closeProfileModal">
    <div class="modal-content" @click.stop style="max-width: 600px;">
      <h2 class="modal-title">用户资料详情</h2>
      <div v-if="profileDetail">
        <div class="form-group">
          <label>个人简介</label>
          <textarea 
            v-model="profileDetail.bio" 
            class="form-input"
            rows="4"
            placeholder="请输入个人简介..."
          ></textarea>
        </div>
        <div class="form-group">
          <label>手机号</label>
          <input 
            v-model="profileDetail.phone_number" 
            type="tel" 
            class="form-input"
            :class="{ 'error': phoneError }"
            placeholder="请输入手机号"
            @input="validatePhone"
          />
          <div v-if="phoneError" class="error-message">{{ phoneError }}</div>
        </div>
        <div class="form-group">
          <label>位置</label>
          <input 
            v-model="profileDetail.location" 
            type="text" 
            class="form-input"
            placeholder="请输入位置"
          />
        </div>
        <div class="form-group">
          <label>生日</label>
          <input 
            v-model="profileDetail.birth_date" 
            type="date" 
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label>头像</label>
          <div class="avatar-section">
            <div class="image-preview-container">
              <img 
                :src="profileDetail.avatar || defaultAvatarImage" 
                :alt="profileDetail.avatar ? '用户头像' : '默认头像'"
                class="image-preview"
                @error="handleAvatarImageError"
              />
            </div>
            <div 
              class="image-upload-area-square"
              @dragover="handleDragOver"
              @drop="handleDrop"
              @click="triggerFileSelect"
            >
              <input 
                type="file"
                ref="avatarFileInput"
                class="file-input"
                accept="image/*"
                @change="handleFileSelect"
              />
              <p class="upload-text">拖拽图片到此处或点击上传</p>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label>头像缩略图</label>
          <div class="image-preview-container">
            <img 
              :src="profileDetail.thumbnail || placeholderImage" 
              :alt="profileDetail.thumbnail ? '头像缩略图' : '暂无图片'"
              class="image-preview"
              @error="handleImageError"
            />
          </div>
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="cancel-btn" @click="closeProfileModal">取消</button>
        <button type="button" class="save-btn" @click="updateProfile">更新资料</button>
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
      showBioModal: false,
      showDeleteConfirm: false,
      showProfileModal: false,
      isEditing: false,
      editingUserId: null,
      editingUser: null,
      currentProfileUserId: null, // Track the user ID for profile operations
      form: {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        is_staff: false
      },
      bioForm: {
        bio: ''
      },
      profileDetail: null,
      phoneError: null,
      placeholderImage: null,
      defaultAvatarImage: null,
    }
  },
  created() {
    this.generatePlaceholderImage();
    this.generateDefaultAvatarImage();
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
        
        // 为每个用户添加bio字段，后续会单独获取完整profile
        const usersWithBioPlaceholder = usersData.map(user => ({
          ...user,
          bio: ''  // 初始化为空，稍后从profile接口获取
        }));
        
        console.log('处理后的用户数据:', usersWithBioPlaceholder)
        
        this.users = usersWithBioPlaceholder;
        this.filteredUsers = [...this.users]; // 确保复制数组
        
        // 为每个用户获取其profile数据
        for (let i = 0; i < this.users.length; i++) {
          try {
            const profileResponse = await userAPI.getUserProfile(this.users[i].id);
            // 将bio等profile信息合并到用户对象中
            this.users[i].bio = profileResponse.data.bio || '';
          } catch (error) {
            console.error(`获取用户 ${this.users[i].id} 简介失败:`, error);
            // 如果获取profile失败，保持空值
            this.users[i].bio = '';
          }
        }
        
        // 更新filteredUsers以反映最新的用户数据
        this.filteredUsers = [...this.users];
        
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
    async openBioModal(user) {
      console.log('打开简介编辑模态框', user)
      this.editingUser = user
      
      // 获取用户的完整profile信息
      try {
        const response = await userAPI.getUserProfile(user.id);
        // 将profile信息保存到用户对象中
        user.bio = response.data.bio || '';
      } catch (error) {
        console.error('获取用户简介失败:', error);
        // 如果获取profile失败，尝试获取用户基本信息
        try {
          const response = await userAPI.getUser(user.id);
          user.bio = response.data.bio || '';
        } catch (err) {
          console.error('获取用户详情失败:', err);
        }
      }
      
      this.bioForm.bio = user.bio || ''
      this.showBioModal = true
    },
    closeModal() {
      console.log('关闭模态框')
      this.showModal = false
    },
    closeBioModal() {
      console.log('关闭简介模态框')
      this.showBioModal = false
    },
    closeDeleteConfirm() {
      console.log('关闭删除确认框')
      this.showDeleteConfirm = false
    },
    closeProfileModal() {
      console.log('关闭Profile模态框')
      this.showProfileModal = false
      this.profileDetail = null;
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
    async submitBio() {
      console.log('提交简介数据', this.bioForm)
      try {
        // 使用profile接口更新简介
        const profileData = {
          bio: this.bioForm.bio
        };
        
        await userAPI.updateUserProfile(this.editingUser.id, profileData)
        
        // 更新本地用户数据中的简介
        const userIndex = this.users.findIndex(u => u.id === this.editingUser.id);
        if (userIndex !== -1) {
          this.users[userIndex].bio = this.bioForm.bio;
        }
        // 更新过滤后的用户数据
        const filteredUserIndex = this.filteredUsers.findIndex(u => u.id === this.editingUser.id);
        if (filteredUserIndex !== -1) {
          this.filteredUsers[filteredUserIndex].bio = this.bioForm.bio;
        }
        this.closeBioModal()
      } catch (error) {
        console.error('更新简介失败:', error)
        console.error('错误详情:', error.response || error.message)
        if (error.response) {
          console.error('响应状态:', error.response.status)
          console.error('响应数据:', error.response.data)
          alert(`更新简介失败: ${JSON.stringify(error.response.data)}`)
        } else {
          alert('更新简介失败: ' + error.message || '未知错误')
        }
      }
    },
    
    async showUserProfile(user) {
      console.log('显示用户资料', user);
      try {
        const response = await userAPI.getUserProfile(user.id);
        this.profileDetail = { ...response.data };
        this.currentProfileUserId = user.id; // Store the current profile user ID
        this.showProfileModal = true;
      } catch (error) {
        console.error('获取用户资料失败:', error);
        alert('获取用户资料失败: ' + (error.message || '未知错误'));
      }
    },
    validatePhone() {
      // 简单的手机号格式验证（中国手机号）
      if (!this.profileDetail.phone_number) {
        this.phoneError = null;
        return;
      }
      
      const phoneRegex = /^1[3-9]\d{9}$/;
      if (!phoneRegex.test(this.profileDetail.phone_number)) {
        this.phoneError = '请输入有效的手机号码';
      } else {
        this.phoneError = null;
      }
    },
    generatePlaceholderImage() {
      // Create a canvas to generate a placeholder image
      const canvas = document.createElement('canvas');
      canvas.width = 200;
      canvas.height = 200;
      const ctx = canvas.getContext('2d');
      
      // Fill with light gray background
      ctx.fillStyle = '#e0e0e0';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw a simple icon or text
      ctx.fillStyle = '#9e9e9e';
      ctx.font = '30px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('?', canvas.width / 2, canvas.height / 2);
      
      // Draw a border
      ctx.strokeStyle = '#bdbdbd';
      ctx.lineWidth = 2;
      ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);
      
      this.placeholderImage = canvas.toDataURL('image/png');
    },
    handleImageError(event) {
      // When actual image fails to load, show the generated placeholder
      event.target.src = this.placeholderImage;
    },
    generateDefaultAvatarImage() {
      // Create a canvas to generate a default avatar image
      const canvas = document.createElement('canvas');
      canvas.width = 200;
      canvas.height = 200;
      const ctx = canvas.getContext('2d');
      
      // Fill with a light blue background
      ctx.fillStyle = '#d1e7ff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw a simple user icon or text
      ctx.fillStyle = '#5b9bd5';
      ctx.font = '80px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('👤', canvas.width / 2, canvas.height / 2);
      
      // Draw a border
      ctx.strokeStyle = '#9cc5f8';
      ctx.lineWidth = 2;
      ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);
      
      this.defaultAvatarImage = canvas.toDataURL('image/png');
    },
    handleAvatarImageError(event) {
      // When actual avatar fails to load, show the default avatar
      event.target.src = this.defaultAvatarImage;
    },
    handleDragOver(event) {
      event.preventDefault();
      event.stopPropagation();
    },
    handleDrop(event) {
      event.preventDefault();
      event.stopPropagation();
      
      const files = event.dataTransfer.files;
      if (files && files.length > 0) {
        this.processImageFile(files[0]);
      }
    },
    triggerFileSelect() {
      this.$refs.avatarFileInput.click();
    },
    handleFileSelect(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        this.processImageFile(files[0]);
      }
    },
    processImageFile(file) {
      if (!file.type.match('image.*')) {
        alert('请选择图片文件');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        // For now, we just update the avatar field with the data URL
        // In a real implementation, you might want to upload the file to a server
        this.profileDetail.avatar = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    async updateProfile() {
      console.log('更新用户资料', this.profileDetail);
      if (this.phoneError) {
        alert('请修正手机号格式');
        return;
      }
      
      try {
        // 移除缩略图字段，因为它不应该被编辑
        const profileData = { ...this.profileDetail };
        delete profileData.thumbnail;
        
        await userAPI.updateUserProfile(this.currentProfileUserId, profileData);
        this.closeProfileModal();
        // 重新加载用户列表以更新显示
        await this.loadUsers();
      } catch (error) {
        console.error('更新用户资料失败:', error);
        alert('更新用户资料失败: ' + (error.message || '未知错误'));
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

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 4px;
}

.error {
  border-color: #e74c3c;
}

.image-preview-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.avatar-section {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.image-preview {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #d2d2d7;
  background-color: #f5f5f5; /* 灰色背景表示无图片 */
}

.image-upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
  min-width: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-upload-area:hover {
  border-color: #007aff;
}

.image-upload-area-square {
  border: 2px dashed #ccc;
  border-radius: 8px;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.image-upload-area-square:hover {
  border-color: #007aff;
}

.image-upload-area.dragover {
  border-color: #007aff;
  background-color: #f0f8ff;
}

.upload-text {
  margin: 0;
  color: #888;
  font-size: 14px;
  word-break: break-word;
  padding: 0 5px;
}

.file-input {
  display: none;
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