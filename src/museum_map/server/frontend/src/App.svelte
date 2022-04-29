<script lang="ts">
	import Root from './routes/Root.svelte';
	import { fetchFloorTopics, fetchFloors } from './store';

	fetchFloorTopics();
	fetchFloors();
</script>

<div class="bg-neutral-700 h-screen v-screen overflow-hidden">
  <main class="flex flex-col container mx-auto h-full v-full overflow-hidden bg-neutral-600 text-white shadow-lg shadow-black font-serif">
	  <Root/>
  </main>
</div>

<style global>
	@tailwind base;
	@tailwind components;
	@tailwind utilities;

	@layer utilities {
		ol.child-separator li::after , ul.child-separator li::after {
			content: '»';
		}

		ol.child-separator li:last-child::after , ul.child-separator li:last-child::after {
			content: '';
		}

		ol.list-separator li::after , ul.list-separator li::after {
			content: ',';
		}

		ol.list-separator li:last-child::after , ul.list-separator li:last-child::after {
			content: '';
		}

		.hover-parent:hover .hover-child-underline, .hover-parent:focus .hover-child-underline {
			@apply underline;
		}
	}

	@layer components {
		figure.title-hover figcaption {
			@apply opacity-0 transition-opacity duration-300;
		}
		figure.title-hover:hover figcaption, figure.title-hover:focus figcaption {
			@apply opacity-100;
		}
	}
</style>
