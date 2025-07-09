<template>
    <h1>资源管理</h1>
    <div class="resource-admin">
      <!-- 学科筛选 -->
      <el-select v-model="filter.subject" placeholder="按学科筛选">
        <el-option v-for="sub in subjects" :key="sub.id" :label="sub.name" :value="sub.id" />
      </el-select>
      <br>
      <br>
  
      <!-- 上传组件 -->
      <el-upload
        action="/api/resources/"
        :headers="{ 'Authorization': 'Bearer ' + token }"
        :data="{ shared: false }"
        :on-success="handleUploadSuccess"
      >
        <el-button type="primary">上传资源</el-button>
      </el-upload>
  
      <!-- 资源表格 -->
      <el-table :data="filteredResources">
        <el-table-column prop="name" label="资源名" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="subject.name" label="学科" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button @click="downloadResource(row.id)">下载</el-button>
            <el-button @click="toggleShare(row)">
              {{ row.shared ? '取消共享' : '共享' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const resources = ref([])
const subjects = ref([])
const filter = ref({ subject: null })
const token = localStorage.getItem('token')

// 获取资源列表
const fetchResources = async () => {
  const res = await axios.get('/api/django/resources/')
  resources.value = res.data
}

// 获取学科列表
const fetchSubjects = async () => {
  const res = await axios.get('/api/django/subjects/')
  subjects.value = res.data
}

// 下载资源
const downloadResource = (id) => {
  window.open(`/api/resources/${id}/download/`)
}

// 切换共享状态
const toggleShare = async (row) => {
  await axios.patch(`/api/django/resources/${row.id}/`, { shared: !row.shared })
  fetchResources()
}

// 计算过滤后的资源
const filteredResources = computed(() => {
  return filter.value.subject 
    ? resources.value.filter(r => r.subject?.id === filter.value.subject)
    : resources.value
})

onMounted(() => {
  fetchResources()
  fetchSubjects()
})
</script>

<style scoped>
.resource-admin {
    background-color: #f8f8f8;;
    margin: 0;
    padding: 60px 100px 100px;
    border-radius: 10px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}
</style>