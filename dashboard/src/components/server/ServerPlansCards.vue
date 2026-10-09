<template>
	<PlansCards
		:plans="plansOption"
		v-model="selectedPlan"
		:hourly-pricing="hourlyPricing"
	/>
</template>

<script>
import PlansCards from '../PlansCards.vue';
import { t } from '../../utils/language';

export default {
	props: {
		modelValue: {
			type: [String, Object, Number, Boolean],
			default: null,
		},
		plans: {
			type: Array,
			default: () => [],
		},
		hourlyPricing: {
			type: Boolean,
			default: false,
		},
	},
	emits: ['update:modelValue'],
	components: {
		PlansCards,
	},
	computed: {
		plansOption() {
			return this.plans.map((plan) => {
				return {
					...plan,
					sublabel: plan.description || null,
					features: [
						{
							label: 'vCPUs',
							value: plan.vcpu,
						},
						{
							label: t('Memory'),
							value: this.$format.bytes(plan.memory, 0, 2),
						},
						{
							label: t('Disk'),
							value: `${plan.disk} GB`,
						},
						{
							label: t('Instance Type'),
							value: plan.instance_type,
						},
					],
				};
			});
		},
		selectedPlan: {
			get() {
				return this.modelValue;
			},
			set(value) {
				this.$emit('update:modelValue', value);
			},
		},
	},
};
</script>
