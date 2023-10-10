<script setup>
import { RouterLink, RouterView } from 'vue-router'
import ConvertForm from './components/ConvertForm.vue'
</script>

<template>
  <header>
    <div class="wrapper bg-slate-50 relative min-h-screen">
      <ConvertForm />
      <div class="container mx-auto pb-10 flex flex-col items-center antialiased px-10 text-slate-600">
        <div class="mb-6 w-full lg:w-2/3 flex items-top">
          <a href="https://www.diffbot.com" class="me-3 pt-1"><img src="./assets/diffbot-logomark.svg" width="50" /></a>
          <span class="text-sm">
            <strong>With ❤️ from <a href="https://www.diffbot.com" class="text-sky-600 hover:underline">Diffbot</a></strong>
            <br />Because Jerome is tired of writing conversion scripts
          </span>
        </div>
      </div>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>

</style>
