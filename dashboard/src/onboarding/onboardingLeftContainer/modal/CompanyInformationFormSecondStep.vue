<script setup lang="ts">
import { FormControl } from 'frappe-ui'
import { computed } from 'vue'
import type { PartnerOnboardingDoc } from '@/onboarding/usePartnerOnboarding'
import { t } from '../../../utils/language'

const emit = defineEmits(['continue'])
const props = defineProps<{
	form: PartnerOnboardingDoc
}>()

const verticalOptions = [
	{ label: t('Manufacturing'), value: 'Manufacturing' },
	{ label: t('Retail'), value: 'Retail' },
	{ label: t('Services'), value: 'Services' },
	{ label: t('Banking and Finance'), value: 'Banking and Finance' },
	{ label: t('Distribution and Trading'), value: 'Distribution and Trading' },
	{ label: t('Hospitality'), value: 'Hospitality' },
	{ label: t('Real Estate'), value: 'Real Estate' },
	{ label: t('Automotive'), value: 'Automotive' },
	{ label: t('Government'), value: 'Government' },
	{ label: t('Education'), value: 'Education' },
	{ label: t('Healthcare'), value: 'Healthcare' },
	{ label: t('Non-profit'), value: 'Non-profit' },
	{ label: t('Other'), value: 'Other' },
]

const customerRangeOptions = [
	{ label: '1-10', value: '1-10' },
	{ label: '11-50', value: '11-50' },
	{ label: '51-200', value: '51-200' },
	{ label: '201+', value: '201+' },
]

const verticalsServed = computed<string[]>({
	get() {
		const value = props.form.verticals_served
		if (!value) return []
		return String(value)
			.split(',')
			.map((vertical) => vertical.trim())
			.filter(Boolean)
	},
	set(value) {
		props.form.verticals_served = value.join(', ')
	},
})

function tryContinue() {
	emit('continue')
}

defineExpose({ tryContinue })
</script>

<template>
	<form
		id="company-information-form-2"
		class="flex flex-col gap-5"
		@submit.prevent="tryContinue"
	>
		<div class="flex flex-col gap-1">
			<div class="flex items-center justify-between gap-2">
				<span class="text-xs text-ink-gray-6">{{ t('Verticals served') }}</span>
				<span class="text-xs text-ink-gray-5">{{ t('Optional') }}</span>
			</div>
			<FormControl
				v-model="verticalsServed"
				type="select"
				size="sm"
				variant="outline"
				:placeholder="t('Select')"
				:options="verticalOptions"
				multiple
			/>
		</div>

		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
			<div class="flex flex-col gap-1">
				<div class="flex items-center justify-between gap-2">
					<span class="text-xs text-ink-gray-6">{{ t('No. of customers') }}</span>
					<span class="text-xs text-ink-gray-5">{{ t('Optional') }}</span>
				</div>
				<FormControl
					v-model="props.form.customer_count_range"
					type="select"
					size="sm"
					variant="outline"
					:placeholder="t('Select')"
					:options="customerRangeOptions"
				/>
			</div>

			<div class="flex flex-col gap-1">
				<div class="flex items-center justify-between gap-2">
					<span class="text-xs text-ink-gray-6">{{ t('No. of ERPNext customers') }}</span>
					<span class="text-xs text-ink-gray-5">{{ t('Optional') }}</span>
				</div>
				<FormControl
					v-model="props.form.erpnext_customer_count_range"
					type="select"
					size="sm"
					variant="outline"
					:placeholder="t('Select')"
					:options="customerRangeOptions"
				/>
			</div>
		</div>
	</form>
</template>
