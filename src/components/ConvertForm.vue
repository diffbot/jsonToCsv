<script>
import { ref } from 'vue'

export default {
  setup() {
    const convertForm = ref(null)
    const jsonPaste = ref(null)
    const jsonFile = ref(null)
    const jsonPastePlaceholder = ref(null)
    const baseUrl = window.location.origin

    jsonPastePlaceholder.value = `{
      "request": {
        "pageUrl": "https://www.technologyreview.com/2020/09/04/1008156/knowledge-graph-ai-reads-web-machine-learning-natural-language-processing/",
        "api": "analyze",
        "version": 3
      }\n}`

    return {
       baseUrl, convertForm, jsonPaste, jsonFile, jsonPastePlaceholder
    }
  }
}
</script>

<template>
  <div class="container mx-auto flex flex-col h-screen items-center antialiased px-10 pt-12">
    <div class="mb-10 w-full lg:w-1/2">
      <h1 class="text-4xl font-bold tracking-tight mb-2">JSON to CSV</h1>
      <p class="text-md">A fast and unopinionated converter. <a href="" class="text-sky-500 hover:text-sky-700">Use without caution.</a></p>
    </div>
    <div class="w-full lg:w-1/2 bg-white flex flex-col justify-center items-center px-6 rounded-lg shadow-sm">
      <form ref="convertForm" enctype="multipart/form-data" method="POST" class="w-full flex flex-col space-y-4 py-6" :action="baseUrl + '/api/convert'">
        <div>
          <label for="json_paste" class="text-sm block">
            <span class="font-semibold">Option 1:</span> Paste JSON
          </label>
          <textarea id="json_paste" name="json_paste" ref="jsonPaste" @change="jsonFile.value = ''" class="w-full border border-slate-100 font-mono text-sm p-3 mt-3" rows="10" :placeholder="jsonPastePlaceholder"></textarea>
        </div>
        <div>
          <label for="json_file" class="text-sm block">
            <span class="font-semibold">Option 2:</span> Upload a JSON file
          </label>
          <input type="file" id="json_file" name="json_file" ref="jsonFile" @change="jsonPaste.value = ''" class="block w-full mt-3 text-sm text-slate-500
            file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100" />
        </div>
        <div
          class="w-full pt-4 mb-8">
          <div class="flex justify-center">
            <button type="submit" class="block py-2 px-6 text-lg font-semibold rounded-full border-0 bg-sky-600 text-sky-100 hover:bg-sky-500">Convert to CSV</button>
          </div>
          <div class="flex justify-center mt-2">
            <span class="text-xs">All data wiped at the turn of every hour</span>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>

</style>
