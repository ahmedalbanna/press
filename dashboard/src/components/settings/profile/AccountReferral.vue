<template>
	<Card
		v-if="referralLink"
		:title="t('Refer & Earn')"
		:subtitle="t('Your unique referral link')"
		class="mx-auto max-w-3xl"
	>
		<div class="flex flex-col space-y-4 overflow-hidden">
			<ClickToCopyField :textContent="referralLink" />
			<span class="text-sm font-medium leading-4 text-ink-gray-7">
				{{
					tr(
						'Invite someone to AlbannaTech and get {amount} in AlbannaTech credits',
						{ amount: creditAmountInTeamCurrency },
					)
				}}
				{{
					tr(
						'when they sign up and spend at least {amount}!',
						{ amount: minimumSpentAmount },
					)
				}}
			</span>
		</div>
	</Card>
</template>
<script>
import ClickToCopyField from '../../ClickToCopyField.vue';

export default {
	name: 'AccountReferral',
	components: {
		ClickToCopyField,
	},
	computed: {
		referralLink() {
			if (this.$team.doc?.referrer_id) {
				return `${location.origin}/dashboard/signup?referrer=${this.$team.doc?.referrer_id}`;
			}
			return '';
		},
		minimumSpentAmount() {
			return this.$team.doc?.country == 'India' ? '₹1800' : '$25';
		},
		creditAmountInTeamCurrency() {
			return this.$team.doc?.country == 'India' ? '₹750' : '$10';
		},
	},

};
</script>
