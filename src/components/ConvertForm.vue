<script>
import { ref, reactive, computed } from 'vue'

export default {
  setup() {
    const currentTab = ref("online")
    const tabActiveClass = "text-blue-600 bg-white rounded-t-lg active"
    const tabInactiveClass = "rounded-t-lg hover:text-gray-600"
    const convertForm = ref(null)
    const convertFormStep = ref(1)
    const convertFormAdvanced = reactive({
      'allAttributes': false
    })
    const convertFormError = ref("")
    const convertFormFileName = ref("")
    const convertFormOntology = reactive({
      "ontology": {},
      "selected_ontology": {},
      "example_record": {}
    })
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

    const appIsLocal = computed(() => {
      return false // baseUrl.includes('127.0.0.1') || baseUrl.includes('localhost')
    })

    const numSelectedOntologyColumns = computed(() => {
      return Object.values(convertFormOntology.selected_ontology).filter(value => value === true).length;
    })

    function convertFormSubmit(e) {
      if (convertFormStep.value == 1) {
        e.preventDefault()
        let formData = new FormData()
        if (jsonPaste.value.value) {
          formData.append('json_paste', jsonPaste.value.value)
        }
        else if (jsonFile.value.files && jsonFile.value.files[0]) {
          formData.append('json_file', jsonFile.value.files[0]) 
        }
        formData.append('advanced', JSON.stringify(convertFormAdvanced))
        fetch(`${baseUrl}/api/convert`, {
          method: 'POST',
          body: formData,
        })
        .then(response => response.json())
        .then((response) => {
          if (response && !response.error) {
            // Track Step 1 Completions
            plausible('Step 1: Upload JSON', {props: {method: jsonPaste.value.value ? 'json_paste' : 'json_file'}})
            // Set File Path
            convertFormFileName.value = response?.file_name
            // Set Ontology
            convertFormOntology.ontology = response["ontology"]
            convertFormOntology.selected_ontology = {}
            response["ontology"].forEach((ont) => convertFormOntology.selected_ontology[ont] = true)
            convertFormOntology.example_record = response["example_record"]
            convertFormStep.value = 2
            // Reset Form Step 1
            jsonPaste.value.value = ""
            jsonFile.value.value = ""
            convertFormError.value = ""
          } 
          else {
            console.error(response);
            if (response.error) {
              convertFormError.value = response.error
              // Track Step 1 Errors
              plausible('Step 1: JSON / Error', {props: {error: response.error}})
            }
          }
        })
        .catch((error) => {
          console.error('An error occurred:', error);
        });
      }
    }

    function resetConvertForm() {
      // Track Step 2 Completions
      plausible('Step 2: Download CSV')
      convertFormFileName.value = ""
      convertFormStep.value = 1
      jsonFile.value.value = ""
      convertFormError.value = ""
      convertFormOntology.ontology = {}
      convertFormOntology.selected_ontology = {}
      convertFormOntology.example_record = {}
    }

    return {
      currentTab,
      tabActiveClass,
      tabInactiveClass,
      baseUrl, 
      convertForm,
      convertFormStep,
      convertFormAdvanced,
      convertFormFileName,
      convertFormOntology,
      convertFormError,
      convertFormSubmit,
      numSelectedOntologyColumns,
      jsonPaste, 
      jsonFile, 
      jsonPastePlaceholder,
      appIsLocal,
      resetConvertForm
    }
  }
}
</script>

<template>
  <div class="container mx-auto pb-10 flex flex-col items-center antialiased px-10 pt-12">
    <div class="mb-6 w-full lg:w-2/3 flex items-top">
      <div class="grow">
        <h1 class="text-4xl font-bold tracking-tighter mb-2">JSON to CSV</h1>
        <p class="text-md mb-4">A fast and unopinionated converter built with <a href="https://jcristharif.com/msgspec/" target="_blank" class="text-sky-500 hover:text-sky-700">msgspec</a>.</p>
        <ul class="text-sm">
          <li class="flex items-top sm:items-center my-2">
            <span class="me-2 mt-1 sm:mt-0 text-cyan-600"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg></span>
            <span><span class="font-semibold">Accepts all types of JSON.</span> Even large and complicated ones.</span>
          </li>
          <li class="flex items-top sm:items-center my-2">
            <span class="me-2 mt-1 sm:mt-0 text-cyan-600"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg></span>
            <span><span class="font-semibold">Customizable.</span> Choose only the columns you need.</span>
          </li>
          <li class="flex items-top sm:items-center my-2">
            <span class="me-2 mt-1 sm:mt-0 text-cyan-600"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg></span>
            <span><span class="font-semibold">Open source.</span> Self-host and run the app entirely offline.</span>
          </li>
        </ul>
      </div>
      <div class="pt-1">
        <a class="text-gray-500 hover:text-gray-700" href="https://github.com/diffbot/jsonToCsv" target="_blank" aria-label="Github Link">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
        </a>
      </div>
    </div>
    <ul class="w-full lg:w-2/3 relative top-1 flex flex-wrap justify-start text-sm font-medium text-center text-gray-500" v-if="!appIsLocal">
        <li class="me-1">
            <a href="#" @click="currentTab = 'online'" :aria-selected="currentTab == 'online'" class="flex items-center p-4 pb-5 px-6" :class="[currentTab == 'online' ? tabActiveClass : tabInactiveClass]">
              <span class="inline-block me-2"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg></span> Online
            </a>
        </li>
        <li class="me-1">
            <a href="#" @click="currentTab = 'hosted'" :aria-selected="currentTab == 'hosted'" class="flex items-center p-4 pb-5 px-6" :class="[currentTab == 'hosted' ? tabActiveClass : tabInactiveClass]">
              <span class="inline-block me-2"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></span> Self-Hosted
            </a>
        </li>
    </ul>
    <div class="w-full lg:w-2/3 bg-white flex flex-col justify-center items-center px-6 rounded-lg shadow-sm">
      <div v-show="currentTab == 'hosted'" class="w-full py-6">
        <h2 class="font-semibold text-lg block mb-2">Why Self-Host?</h2>
        <ul class="text-sm block mb-5 ms-1">
          <li class="my-2">
            🔒 You are working with sensitive data
          </li>
          <li class="my-2">
            📁 Your JSON file is too large and timing out the server
          </li>
        </ul>
        <h2 class="font-semibold text-lg block mb-2">Instructions</h2>
        <p class="text-sm mb-3">
          Verify that your system has Python 3.8+ installed, then follow the steps below.
        </p>
        <ul class="text-sm list-decimal list-outside block ms-4">
          <li class="my-3">
            Git clone the app <a href="https://github.com/diffbot/jsonToCsv" target="_blank" class="text-blue-600">repository</a>
          </li>
          <li class="my-3">
            (Optional) Instantiate a Python environment for the app
            <code class="block bg-slate-100 text-slate-600 font-normal p-3 rounded-lg my-2">
              python3 -m venv env;
              <br />source env/bin/activate
            </code>
          </li>
          <li class="my-3">
            Install dependencies 
            <code class="block bg-slate-100 text-slate-600 font-normal p-3 rounded-lg my-2">
              pip install requirements.txt
            </code>
          </li>
          <li class="my-3">
            Run the app
            <code class="block bg-slate-100 text-slate-600 font-normal p-3 rounded-lg my-2">
              flask run
            </code>
          </li>
          <li class="my-3">
            Open the app on any browser at <a href="http://127.0.0.1:5000" target="_blank" class="text-blue-600">http://127.0.0.1:5000</a>
          </li>
        </ul>
      </div>
      <form v-show="currentTab == 'online'" ref="convertForm" enctype="multipart/form-data" method="POST" class="w-full flex flex-col space-y-4 py-6" :action="baseUrl + '/api/convert'" @submit="convertFormSubmit">
        <div v-if="convertFormError" class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
          <span class="font-medium">Error —</span> {{ convertFormError }}
        </div>
        <input type="hidden" name="file_name" :value="convertFormFileName" />
        <input type="hidden" name="selected_ontology" :value="encodeURIComponent(JSON.stringify(convertFormOntology.selected_ontology))" />
        <div id="formStep1">
          <div class="mb-6">
            <label for="json_file" class="text-sm block">
              <span class="font-semibold">Option 1:</span> Upload a JSON file
            </label>
            <input type="file" id="json_file" name="json_file" ref="jsonFile" @change="jsonPaste.value = ''" class="block w-full mt-3 text-sm text-slate-500
              file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100" />
          </div>
          <div class="mb-4">
            <label for="json_paste" class="text-sm block">
              <span class="font-semibold">Option 2:</span> Paste JSON
            </label>
            <textarea id="json_paste" name="json_paste" ref="jsonPaste" @change="jsonFile.value = ''" class="w-full border border-slate-100 font-mono text-sm p-3 mt-3" rows="10" :placeholder="jsonPastePlaceholder"></textarea>
          </div>
          <div class="mb-6">
            <div class="text-sm font-semibold mb-2">
              Advanced Settings
            </div>
            <div class="flex items-center space-x-2">
              <input type="checkbox" id="allAttributes" name="allAttributes" v-model="convertFormAdvanced.allAttributes" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 
              dark:border-gray-600">
              <label for="allAttributes" class="text-sm text-gray-600">Flatten as a single record</label>
            </div>
          </div>
          <div
            class="w-full pt-4 mb-8">
            <div class="flex justify-center">
              <button type="submit" class="w-full sm:w-auto block py-2 px-6 font-semibold rounded-full border-0 bg-sky-600 text-sky-100 hover:bg-sky-500">Convert to CSV</button>
            </div>
            <div class="flex justify-center mt-2">
              <a href="https://github.com/diffbot/jsonToCsv/blob/main/app.py#L20" target="_blank" class="text-xs">All data wiped at the top of every hour</a>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
  <div v-if="convertFormStep == 2" class="absolute inset-0 flex items-center justify-center">
    <transition name="fade" appear>
      <div v-if="convertFormStep == 2" class="absolute bg-black opacity-60 inset-0 z-0" @click="convertFormStep = 1"></div>
    </transition>
    <transition name="fadeDrop" appear>
      <div id="formStep2" v-if="convertFormStep == 2" class="w-full max-w-4xl relative mx-auto my-auto px-3">
        <div class="relative rounded-lg shadow-lg bg-white">
          <div class="header p-5 py-4 border-b border-gray-100 bg-white rounded-t-lg flex items-center">
            <div class="grow">
              <span class="text-lg font-semibold">Columns to Keep</span>
              <br /><span class="text-sm text-slate-500">{{ numSelectedOntologyColumns }} Selected</span>
            </div>
            <div>
              <button type="button" @click="convertForm.submit(); resetConvertForm()" class="w-auto py-2 px-6 text-sm font-semibold rounded-full border-0 bg-sky-600 text-sky-100 hover:bg-sky-500">Finish Conversion</button>
            </div>
          </div>
          <div class="max-h-[400px] overflow-x-auto overflow-y-auto relative rounded-b-lg">
            <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400 relative">
                <thead class="text-xs text-slate-700 uppercase">
                    <tr>
                        <th scope="col" class="bg-gray-50 px-6 py-3 sticky top-0">
                            Selected
                        </th>
                        <th scope="col" class="bg-gray-50 px-6 py-3 sticky top-0">
                            Column
                        </th>
                        <th scope="col" class="bg-gray-50 px-6 py-3 sticky top-0">
                            Example (First Record)
                        </th>
                    </tr>
                </thead>
                <tbody>
                  <tr v-for="ont in convertFormOntology.ontology" class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600" @click="convertFormOntology.selected_ontology[ont] = !convertFormOntology.selected_ontology[ont]">
                    <th scope="row" class="px-6 py-4">
                        <input type="checkbox" :name="ont" v-model="convertFormOntology.selected_ontology[ont]" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600" checked>
                    </th>
                    <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                        {{ ont }}
                    </td>
                    <td class="px-6 py-4">
                        {{ convertFormOntology.example_record[ont] }}
                    </td>
                  </tr>
                </tbody>
            </table>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fadeDrop-enter-from,
.fadeDrop-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.1s ease-out;
}

.fadeDrop-enter-active,
.fadeDrop-leave-active {
  transition: all 0.2s ease-out;
}
</style>
