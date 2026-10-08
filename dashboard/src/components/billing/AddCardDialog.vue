<template>
	<Dialog v-model="show" :options="{ title: t('Add new card') }">
		<template #body-content>
			<div
				v-if="showMessage"
				class="mb-5 inline-flex gap-1.5 text-base text-ink-gray-7"
			>
				<FeatherIcon class="h-4" name="info" />
				<span>
					{{ t('Add at least one card before changing the payment mode.') }}
				</span>
			</div>
			<CardForm
				@success="
					() => {
						show = false;
						emit('success');
					}
				"
			/>
		</template>
	</Dialog>
</template>
<script setup>
import CardForm from './CardForm.vue';
import { Dialog, FeatherIcon } from 'frappe-ui';
import { t } from '../../utils/language';

const props = defineProps({
	showMessage: {
		type: Boolean,
		default: false,
	},
});

const emit = defineEmits(['success']);
const show = defineModel();
</script>
