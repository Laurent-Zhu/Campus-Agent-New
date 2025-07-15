<template>
    <div class="courseware-admin-container">
        <h1>课程资源管理</h1>

        <!-- 筛选和搜索框 -->
        <div class="filter-search-container">
            <select v-model="selectedSubject" @change="filterCoursewares" class="input-field">
                <option value="">所有课程</option>
                <option v-for="subject in subjects" :key="subject" :value="subject">{{ subject }}</option>
            </select>
            <input type="text" v-model="searchQuery" @input="filterCoursewares" placeholder="搜索课程" class="search-input">
        </div>

        <!-- 批量操作按钮 -->
        <div class="batch-actions">
            <input type="checkbox" v-model="selectAll" @change="toggleSelectAll"> 全选
            <button @click="handleBatchDelete" :disabled="!selectedCoursewares.length" class="action-button">批量删除</button>
        </div>

        <!-- 课件列表 -->
        <ul class="courseware-list">
            <li v-for="courseware in paginatedCoursewares" :key="courseware.id" class="courseware-item">
                <input type="checkbox" v-model="selectedCoursewares" :value="courseware.id">
                <div class="courseware-info">
                    <span class="courseware-name">{{ courseware.name }}</span>
                    <span class="subject badge">{{ courseware.subject }}</span>
                    <span class="upload-time">{{ courseware.uploadTime }}</span>
                    <span class="size">{{ courseware.size }}</span>
                    <span class="uploader">{{ courseware.uploader }}</span>
                </div>
                <div class="courseware-actions">
                    <button @click="handleDownload(courseware.id)" class="download-button">下载</button>
                    <button @click="handleDelete(courseware.id)" class="delete-button">删除</button>
                </div>
            </li>
        </ul>

        <!-- 分页组件 -->
        <div class="pagination">
            <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
            <span>{{ currentPage }} / {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
        </div>
    </div>

</template>

<script>
import { fetchCoursewares, deleteCourseware, downloadCourseware } from '@/api/Admin/courseware'

export default {
    data() {
        return {
            coursewares: [],
            filteredCoursewares: [],
            selectedSubject: '',
            searchQuery: '',
            selectedCoursewares: [],
            selectAll: false,
            currentPage: 1,
            itemsPerPage: 10,
            subjects: [] // 初始为空，从后端获取数据
        };
    },

    mounted() {
        this.loadCoursewares();
    },

    computed: {
        totalPages() {
            return Math.ceil(this.filteredCoursewares.length / this.itemsPerPage);
        },
        paginatedCoursewares() {
            const startIndex = (this.currentPage - 1) * this.itemsPerPage;
            const endIndex = startIndex + this.itemsPerPage;
            return this.filteredCoursewares.slice(startIndex, endIndex);
        }
    },

    methods: {
        // 加载课件
        async loadCoursewares() {
            const token = localStorage.getItem('token')

            try {
                const coursewares = await fetchCoursewares(token);
                this.coursewares = coursewares;
                this.filteredCoursewares = coursewares;
            } catch (error) {
                console.error('获取课件列表失败:', error);
            }
        },
        // 筛选课件
        filterCoursewares() {
            let filtered = this.coursewares;
            if(this.selectedSubject) {
                filtered = filtered.filter(courseware => courseware.subject === this.selectedSubject);
            }
            if (this.searchQuery){
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(courseware => courseware.name.toLowerCase().includes(query));
            }
            this.filteredCoursewares = filtered;
            this.currentPage = 1; // 重置当前页码
        },

        // 全选 / 取消全选
        toggleSelectAll() {
            if(this.selectAll){
                this.selectedCoursewares = this.filteredCoursewares.map(courseware => courseware.id);
            } else {
                this.selectedCoursewares = [];
            }
        },

        // 批量删除
        async handleBatchDelete() {
            if (!confirm('确定要删除所选课程吗？')) {
                return;
            }
            try {
                const token = localStorage.getItem('token')

                for (const id of this.selectedCoursewares ) {
                    await deleteCourseware(token, id);
                }
                this.loadCoursewares();
                this.selectedCoursewares = [];
                alert('删除成功');
            } catch (error) {
                console.error('删除课程失败:', error);
                alert('删除失败');
            }
        },

        // 下载课件
        async handleDownload(coursewareId) {
            const token = localStorage.getItem('token');
            try { 
                await downloadCourseware(token, coursewareId);
            } catch (error) {
                console.error('下载课件失败:', error);
                alert('下载失败');
            }
        },

        // 删除单个课件
        async handleDelete(coursewareId){
            if (!confirm('确定要删除此课件吗？')) {
                return;
            }
            try { 
                const token = localStorage.getItem('token');
                await deleteCourseware(token, coursewareId);
                this.loadCoursewares();
                alert('删除成功');
            } catch (error) {
                console.error('删除课件失败:', error);
                alert('删除失败');
            }
        },

        // 上一页
        prevPage() {
            if (this.currentPage > 1) {
                this.currentPage--;
                // this.loadCoursewares();
            }
        },

        // 下一页
        nextPage() {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                // this.loadCoursewares();
            }
        }

    }
}
</script>

<style scoped>
.courseware-admin-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.filter-search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.input-field {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.batch-actions {
  margin-bottom: 20px;
}

.courseware-list {
  list-style-type: none;
  padding: 0;
}

.courseware-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 10px;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.courseware-item:hover {
  background-color: #f0f0f0;
}

.courseware-info {
  flex: 1;
  display: flex;
  gap: 10px;
}

.courseware-name {
  font-weight: bold;
  color: #333;
}

.badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
  background-color: #e8f5e9;
  color: #2e7d32;
}

.courseware-actions {
  display: flex;
  gap: 5px;
}

.action-button,
.download-button,
.delete-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}

.action-button {
  background-color: #4caf50;
  color: white;
}

.download-button {
  background-color: #2196f3;
  color: white;
}

.delete-button {
  background-color: #f44336;
  color: white;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}
</style>