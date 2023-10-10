<script>
import { ref, reactive, computed } from 'vue'
import { getCookie } from '../utils.js';

export default {
  setup(props, context) {
  	const baseUrl = window.location.origin
  	var posts = ref([])
  	var guestbookFormError = ref("")
  	var guestbookForm = reactive({
  		'name': "",
  		'location': "",
  		'message': ""
  	})

  	function getPosts() {
        fetch(`${baseUrl}/api/guestbook`)
        .then(response => response.json())
        .then((response) => {
        	if (response && !response.error && response.posts) {
        		posts.value = response.posts
        		context.emit('guestbookVisible')
        	}
        });
  	}
  	getPosts()

  	function createPost() {
  		let formData = new FormData()
  		formData.append('name', guestbookForm.name)
  		formData.append('location', guestbookForm.location)
  		formData.append('message', guestbookForm.message)
  		fetch(`${baseUrl}/api/guestbook`, {
          method: 'POST',
          body: formData,
          headers: {
          	'X-CSRFToken': getCookie('csrftoken')
          }
        })
        .then(response => response.json())
        .then((response) => {
        	if (response && !response.error) {
        		resetGuestbookForm()
        		getPosts()
        	}
			else {
	            console.error(response);
	            if (response.error) {
	              guestbookFormError.value = response.error
	              // Track Errors
	              plausible('Guestbook Error', {props: {error: response.error}})
	            }
	            if (response.code == 403) {
	            	// Reset the Form
	            	guestbookForm.name = ""
	            	guestbookForm.location = ""
	            	guestbookForm.message = ""
	            }
          }
        })
        .catch((error) => {
          console.error('An error occurred:', error);
        });
  	}

    function resetGuestbookForm() {
    	guestbookFormError.value = ""
    	guestbookForm.name = ""
    	guestbookForm.location = ""
    	guestbookForm.message = ""
    }

  	return {
  		posts, getPosts, createPost, guestbookFormError, guestbookForm, resetGuestbookForm
  	}
  }
}
</script>

<template>
    <div v-if="guestbookFormError" class="p-4 mb-5 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
      <span class="font-medium">Error —</span> {{ guestbookFormError }}
    </div>
	<div class="mb-5">
		<h2 class="font-semibold text-lg block mb-2">Sign the Guestbook</h2>
		<p class="text-sm">🥳 Yay! You're seeing this because you've successfully converted a JSON to CSV. Sign the guestbook with a friendly note for others, or feel free to just hang out. </p>
	</div>
	<form class="mb-8 bg-amber-50 border-amber-200 p-5" @submit.prevent="createPost()">
		<div class="mb-3">
			<textarea id="guest_message" name="message" rows="1" class="h-16 md:h-fit w-full border-0 bg-amber-50 font-serif text-lg" aria-label="note" placeholder="A friendly note" v-model="guestbookForm.message"></textarea>
		</div>
		<div class="md:flex md:flex-row">
			<div class="flex flex-row items-center py-1 px-3">
				<label for="guest_name" id="guest_name_label" class="text-sm block me-3">
					<span class="font-semibold text-slate-500">By</span>
				</label>
				<input type="text" id="guest_name" aria-labeledby="guest_name_label" name="name" class="w-full border-0 border-b bg-amber-50 border-gray-300 text-sm" placeholder="Anonymous" v-model="guestbookForm.name" autocomplete="given-name" />
			</div>
			<div class="flex flex-row items-center py-1 px-3">
				<label for="guest_location" id="guest_location_label" class="text-sm block me-3">
					<span class="font-semibold text-slate-500">From</span>
				</label>
				<input type="text" id="guest_location" aria-labeledby="guest_location_label" name="location" class="w-full border-0 border-b bg-amber-50 border-gray-300 text-sm" placeholder="Austin, TX" v-model="guestbookForm.location" />
			</div>
			<div class="md:grow md:flex md:justify-end py-1 px-3 mt-3 md:mt-0">
				<button type="button" @click="createPost()" class="w-full md:w-auto py-2 px-6 text-sm font-semibold rounded-full border border-amber-600 text-amber-600 hover:bg-amber-600 hover:text-amber-50">Sign</button>
			</div>
		</div>
	</form>
	<div class="grid grid-cols-1 gap-6 py-4">
		<div v-for="post in posts" class="px-6 py-2">
			<p class="mb-1 font-serif text-lg">"{{ post.message }}"</p>
			<span class="text-sm"><strong>{{ post.author }}</strong> from {{ post.location }}</span>
		</div>
	</div>
</template>