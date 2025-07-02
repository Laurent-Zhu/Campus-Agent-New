<script setup>

import Navbar from './components/navbar.vue';

</script>

<template>
  <!-- 导航栏渲染 -->
  <Navbar></Navbar>

  <div class="container">
    <router-view></router-view>
  </div>
</template>

<style scoped>
  /* 添加全局样式 */
  .container {
    padding-top: 80px; /* 大于导航栏高度（60px） */
    max-width: 1200px;
    margin: 0 auto;
    padding: 80px 20px 20px;
  }
</style>
