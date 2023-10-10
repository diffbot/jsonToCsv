<script setup>
import { RouterLink, RouterView } from 'vue-router'
import ConvertForm from './components/ConvertForm.vue'
</script>

<template>
  <header>
    <div class="wrapper bg-slate-50 relative min-h-screen">
      <ConvertForm />
    </div>
  </header>

  <RouterView />
</template>

<style scoped>

</style>
