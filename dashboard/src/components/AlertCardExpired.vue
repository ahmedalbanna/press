<template>
	<AlertBanner
		:title="t('Your card has expired. Please update your payment details to avoid site suspension.')"
		type="warning"
	>
		<Button class="ml-auto" route="/billing" variant="outline">
			{{ t('Update Card') }}
		</Button>
	</AlertBanner>
</template>
<script>
import AlertBanner from './AlertBanner.vue'
import { t } from '../utils/language'

export default {
	name: 'AlertCardExpired',
	components: { AlertBanner },
}
</script>
