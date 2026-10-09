<template>
	<AlertBanner
		:title="
			title ?? t('Add a payment mode to start creating sites, benches, and more.')
		"
		:type="type ?? 'warning'"
	>
		<Button class="ml-auto" @click="addPaymentMode" variant="outline">
			{{ t('Add payment mode') }}
		</Button>
	</AlertBanner>
</template>
<script>
import AlertBanner from './AlertBanner.vue';

export default {
	name: 'AlertAddPaymentMode',
	props: {
		title: String,
		type: String,
	},
	components: { AlertBanner },
	methods: {
		// Options API templates see only the instance, never module imports.
		addPaymentMode() {
			this.$team.reload();

			this.$router.push({
				name: 'BillingOverview',
			});
		},
	},
};
</script>
