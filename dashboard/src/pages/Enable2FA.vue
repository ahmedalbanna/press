<template>
	<div class="mx-auto mt-16 max-w-xl space-y-4">
		<h1 class="text-center text-2xl font-semibold">{{ t('Enable 2FA') }}</h1>

		<AlertBanner
			:title="
				tr(
					'Two-Factor Authentication is enforced for all members of the team <strong>{user}</strong> by the team owner/admin. You must enable it to continue.',
					{ user: $team.doc.user },
				)
			"
			type="error"
		/>
		<Configure2FA @enabled="handleEnabled" />
	</div>
</template>

<script>
import Configure2FA from '../components/auth/Configure2FA.vue'
import AlertBanner from '../components/AlertBanner.vue'

export default {
	components: {
		Configure2FA,
		AlertBanner,
	},
	methods: {
		handleEnabled() {
			this.$team.reload()

			// sometimes the reload is too fast
			// and the user is not redirected back here due to the 2FA requirement
			setTimeout(() => {
				this.$router.push({ name: 'Site List' })
			}, 100)
		},
	},
}
</script>
