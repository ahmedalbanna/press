<script setup lang="ts">
import { Tooltip } from 'frappe-ui'
import type { NavItemProps } from './types'
import { inject } from 'vue'

const collapsed = inject('collapsed')
const collapsedCss = inject('collapsedCss')

const props = withDefaults(defineProps<NavItemProps>(), {
	is: 'router-link',
})
</script>

<template>
	<Tooltip :text="collapsed ? name : ''">
		<component
			:to="route"
			:is
			@click="onClick"
			class="flex text-left items-center rounded w-full py-1.5 px-2 text-gray-300 transition"
			:class="[
      isActive
        ? 'bg-white/10 text-white md:shadow-sm'
        : 'hover:bg-white/10',
      disabled ? 'pointer-events-none opacity-50' : '',
      collapsed ? 'md:w-fit gap-2 md:gap-0' : 'gap-2 md:w-full',
      css
    ]"
		>
			<slot name="prefix">
				<component
					:is="prefix? prefix() : icon"
					class="shrink-0 size-4 text-gray-400"
					:class="isActive ? 'text-white' : ''"
				/>
			</slot>

			<span class="text-sm flex-1" :class="collapsedCss">{{ name }}</span>
			<slot name="suffix">
				<span v-if="suffix" :class="collapsedCss" class="text-xs text-gray-500"
					>{{ suffix }}
				</span>
			</slot>
		</component>
	</Tooltip>
</template>
