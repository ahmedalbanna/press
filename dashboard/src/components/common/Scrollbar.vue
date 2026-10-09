<script setup lang="ts">
import {
	ScrollAreaRoot,
	ScrollAreaViewport,
	ScrollAreaThumb,
	ScrollAreaScrollbar,
} from 'reka-ui'
import { computed } from 'vue'

interface Props {
	as?: string
}

defineProps<Props>()

// reka-ui defaults an absent dir to 'ltr', which pinned every scrollable
// subtree (including the Sites table) to LTR even when the document is
// rtl. Resolve it the same way Tabs.vue does so scroll content inherits the
// page direction.
const dir = computed<'rtl' | 'ltr'>(() =>
	typeof document !== 'undefined' && document.documentElement.dir === 'rtl'
		? 'rtl'
		: 'ltr',
)
</script>

<template>
	<ScrollAreaRoot
		class="relative overflow-hidden"
		style="--scrollbar-size: 10px"
		:scroll-hide-delay="0"
		:dir
	>
		<ScrollAreaViewport class="w-full h-full" :as>
			<slot />
		</ScrollAreaViewport>

		<ScrollAreaScrollbar
			class="flex select-none touch-none p-0.5 z-20 transition-colors duration-[160ms] ease-out data-[orientation=vertical]:w-2.5"
			orientation="vertical"
		>
			<ScrollAreaThumb
				class="flex-1 bg-surface-gray-3 rounded-[10px] relative ..."
			/>
		</ScrollAreaScrollbar>

		<ScrollAreaScrollbar
			class="flex select-none touch-none p-0.5 z-20 transition-colors duration-[160ms] ease-out data-[orientation=horizontal]:h-2.5"
			orientation="horizontal"
		>
			<ScrollAreaThumb
				class="flex-1 bg-surface-gray-3 rounded-[10px] relative before:content-[''] before:absolute before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:w-full before:h-full before:min-w-[44px] before:min-h-[44px]"
			/>
		</ScrollAreaScrollbar>
	</ScrollAreaRoot>
</template>
