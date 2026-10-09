<template>
	<Card :title="t('Profile')" v-if="user" class="mx-auto max-w-3xl">
		<div class="flex items-center border-b pb-3">
			<div class="relative">
				<Avatar size="2xl" :label="user.first_name" :image="user.user_image" />
				<FileUploader
					@success="onProfilePhotoChange"
					fileTypes="image/*"
					:upload-args="{
						doctype: 'User',
						docname: user.name,
						method: 'press.api.account.update_profile_picture',
					}"
				>
					<template v-slot="{ openFileSelector, uploading, progress, error }">
						<div class="ml-4">
							<button
								@click="openFileSelector()"
								class="absolute inset-0 grid h-10 w-full place-items-center rounded-full bg-black text-xs font-medium text-white opacity-0 transition hover:opacity-50 focus:opacity-50 focus:outline-none"
								:class="{ 'opacity-50': uploading }"
							>
								<span v-if="uploading">{{ progress }}%</span>
								<span v-else>{{ t('Edit') }}</span>
							</button>
						</div>
					</template>
				</FileUploader>
			</div>
			<div class="ml-4">
				<h3 class="text-base font-semibold">
					{{ user.first_name }} {{ user.last_name }}
				</h3>
				<p class="mt-1 text-base text-ink-gray-6">{{ user.email }}</p>
			</div>
			<div class="ml-auto">
				<Button icon-left="edit" @click="showProfileEditDialog = true">
					{{ t('Edit') }}
				</Button>
			</div>
		</div>
		<ListItem
			:title="t('Notification Settings')"
			:subtitle="t('Manage notification channels')"
			v-if="$team?.doc?.user === $session?.user"
		>
			<template #actions>
				<Button @click="showCommunicationInfoDialog = true">
					{{ t('Manage') }}
				</Button>
			</template>
		</ListItem>
		<div>
			<ListItem
				:title="t('Become Marketplace Developer')"
				:subtitle="t('Become a marketplace app publisher')"
				v-if="!$team.doc.is_developer"
			>
				<template #actions>
					<Button @click="confirmPublisherAccount">
						<span>{{ t('Become a Publisher') }}</span>
					</Button>
				</template>
			</ListItem>
			<ListItem
				class="border-t"
				:title="user.is_2fa_enabled ? t('Disable 2FA') : t('Enable 2FA')"
				:subtitle="
					user.is_2fa_enabled
						? t('Disable two-factor authentication for your account')
						: t(
								'Enable two-factor authentication for your account to add an extra layer of security',
							)
				"
			>
				<template #actions>
					<Button @click="show2FADialog = true">
						{{ user.is_2fa_enabled ? t('Disable') : t('Enable') }}
					</Button>
				</template>
			</ListItem>
			<ListItem
				v-if="user.is_2fa_enabled"
				:title="t('View Recovery Codes')"
				:subtitle="t('View your two-factor authentication recovery codes')"
			>
				<template #actions>
					<Button @click="show2FARecoveryCodesDialog = true">
						{{ t('Show') }}
					</Button>
				</template>
			</ListItem>
			<ListItem
				v-if="user.is_2fa_enabled"
				:title="t('Recovery Code Reminders')"
				:subtitle="t('Get an email every month until you review your recovery codes')"
			>
				<template #actions>
					<Switch v-model="recoveryCodeReminders" />
				</template>
			</ListItem>
			<ListItem
				class="border-t"
				:title="teamEnabled ? t('Disable Account') : t('Enable Account')"
				:subtitle="
					teamEnabled
						? t('Disable your account and stop billing')
						: t('Enable your account and resume billing')
				"
			>
				<template #actions>
					<Button
						@click="
							() => {
								if (teamEnabled) {
									showDisableAccountDialog = true;
								} else {
									showEnableAccountDialog = true;
								}
							}
						"
					>
						<span :class="{ 'text-red-600': teamEnabled }"
							>{{ teamEnabled ? t('Disable') : t('Enable') }}</span
						>
					</Button>
				</template>
			</ListItem>
		</div>
		<Dialog
			:options="{
				title: t('Update Profile Information'),
				actions: [
					{
						variant: 'solid',
						label: t('Save Changes'),
						onClick: () => $resources.updateProfile.submit(),
					},
				],
			}"
			v-model="showProfileEditDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl :label="t('First Name')" v-model="user.first_name" />
					<FormControl :label="t('Last Name')" v-model="user.last_name" />
				</div>
				<ErrorMessage class="mt-4" :message="$resources.updateProfile.error" />
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: t('Disable Account'),
				actions: [
					{
						label: t('Disable Account'),
						variant: 'solid',
						theme: 'red',
						loading: $resources.disableAccount.loading,
						onClick: () => deactivateAccount(disableAccount2FACode),
					},
				],
			}"
			v-model="showDisableAccountDialog"
		>
			<template v-slot:body-content>
				<div class="prose text-base">
					{{ t('By confirming this action:') }}
					<ul>
						<li>{{ t('Your account will be disabled') }}</li>
						<li>
							{{
								t(
									'Your active sites will be suspended immediately and will be deleted after a week.',
								)
							}}
						</li>
						<li>{{ t('Your account billing will be stopped') }}</li>
					</ul>
					{{ t('You can log in later to enable your account. Do you want to continue?') }}
				</div>
				<FormControl
					v-if="user.is_2fa_enabled"
					class="mt-4"
					:label="t('Enter your 2FA code to confirm')"
					v-model="disableAccount2FACode"
				/>
				<ErrorMessage class="mt-2" :message="$resources.disableAccount.error" />
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: t('Enable Account'),
				actions: [
					{
						label: t('Enable Account'),
						variant: 'solid',
						loading: $resources.enableAccount.loading,
						onClick: () => $resources.enableAccount.submit(),
					},
				],
			}"
			v-model="showEnableAccountDialog"
		>
			<template v-slot:body-content>
				<div class="prose text-base">
					{{ t('By confirming this action:') }}
					<ul>
						<li>{{ t('Your account will be enabled') }}</li>
						<li>{{ t('Your suspended sites will become active') }}</li>
						<li>{{ t('Your account billing will be resumed') }}</li>
					</ul>
					{{ t('Do you want to continue?') }}
				</div>
				<ErrorMessage class="mt-2" :message="$resources.enableAccount.error" />
			</template>
		</Dialog>

		<AddPrepaidCreditsDialog
			:showMessage="showMessage"
			v-if="showAddPrepaidCreditsDialog"
			v-model="showAddPrepaidCreditsDialog"
			@success="reloadAccount"
		/>

		<CommunicationInfoDialog
			v-if="showCommunicationInfoDialog"
			v-model="showCommunicationInfoDialog"
			@close="showCommunicationInfoDialog = false"
			reference-doctype="Team"
			:reference-name="$team.doc.name"
		/>
	</Card>
	<TFADialog v-model="show2FADialog" />
	<TFARecoveryCodesDialog v-model="show2FARecoveryCodesDialog" />
</template>

<script>
import { Switch } from 'frappe-ui'
import { defineAsyncComponent, h } from 'vue'
import { toast } from 'vue-sonner'
import FileUploader from '@/components/FileUploader.vue'
import router from '../../../router'
import { confirmDialog, renderDialog } from '../../../utils/components'
import { t, tr } from '../../../utils/language'
import AddPrepaidCreditsDialog from '../../billing/AddPrepaidCreditsDialog.vue'
import CommunicationInfoDialog from '../../CommunicationInfoDialog.vue'
import TFADialog from './TFADialog.vue'
import TFARecoveryCodesDialog from './TFARecoveryCodesDialog.vue'

export default {
	name: 'AccountProfile',
	components: {
		TFADialog,
		TFARecoveryCodesDialog,
		FileUploader,
		AddPrepaidCreditsDialog,
		Switch,
	},
	data() {
		return {
			show2FADialog: false,
			show2FARecoveryCodesDialog: false,
			disableAccount2FACode: '',
			showProfileEditDialog: false,
			showEnableAccountDialog: false,
			showDisableAccountDialog: false,
			showAddPrepaidCreditsDialog: false,
			showCommunicationInfoDialog: false,
			showActiveServersDialog: false,
			showMessage: false,
			draftInvoice: {},
			unpaidInvoices: [] | {},
		}
	},
	computed: {
		teamEnabled() {
			return this.$team.doc.enabled
		},
		user() {
			return this.$team?.doc?.user_info
		},
		recoveryCodeReminders: {
			get() {
				return !this.user.unsubscribed_from_recovery_code_reminders
			},
			set(value) {
				this.$resources.setRecoveryCodeReminders.submit({ enabled: value })
			},
		},
	},
	resources: {
		updateProfile() {
			let { first_name, last_name, email } = this.user
			return {
				url: 'press.api.account.update_profile',
				params: {
					first_name,
					last_name,
					email,
				},
				onSuccess() {
					this.showProfileEditDialog = false
					this.notifySuccess()
				},
			}
		},
		disableAccount: {
			url: 'press.api.account.disable_account',
			onSuccess() {
				this.showDisableAccountDialog = false

				const ChurnFeedbackDialog = defineAsyncComponent(
					() => import('../../ChurnFeedbackDialog.vue'),
				)

				renderDialog(
					h(ChurnFeedbackDialog, {
						team: this.$team.doc.name,
						onUpdated: () => {
							toast.success(t('Your feedback was submitted successfully'))
						},
					}),
				)
				toast.success(t('Your account was disabled successfully'))
				this.reloadAccount()
			},
		},
		enableAccount: {
			url: 'press.api.account.enable_account',
			onSuccess() {
				toast.success(t('Your account was enabled successfully'))
				this.reloadAccount()
				this.showEnableAccountDialog = false
			},
		},
		upcomingInvoice: {
			url: 'press.api.billing.upcoming_invoice',
			auto: true,
			onSuccess(data) {
				this.draftInvoice = data.upcoming_invoice
			},
		},
		unPaidInvoices: {
			url: 'press.api.billing.get_unpaid_invoices',
			auto: true,
			onSuccess(data) {
				this.unpaidInvoices = data
			},
		},
		setRecoveryCodeReminders: {
			url: 'press.api.account.set_2fa_recovery_code_reminders',
			onSuccess() {
				this.reloadAccount()
			},
		},
		hasActiveServers() {
			return {
				url: 'press.api.account.has_active_servers',
				auto: true,
				params: {
					team: this.$team.doc.name,
				},
				onSuccess(data) {
					if (data) {
						this.showActiveServersDialog = true
					}
				},
			}
		},
	},
	methods: {
		t,
		reloadAccount() {
			this.$team.reload()
		},
		onProfilePhotoChange() {
			this.reloadAccount()
			this.notifySuccess()
		},
		notifySuccess() {
			toast.success(t('Your profile was updated successfully'))
		},
		deactivateAccount(disableAccount2FACode) {
			const currency = this.$team.doc.currency
			const minAmount = currency === 'INR' ? 410 : 5
			if (this.draftInvoice && this.draftInvoice.amount_due > minAmount) {
				const finalizeInvoicesDialog = defineAsyncComponent(
					() => import('../../billing/FinalizeInvoicesDialog.vue'),
				)
				renderDialog(h(finalizeInvoicesDialog))
			} else if (this.unpaidInvoices) {
				if (this.unpaidInvoices.length > 1) {
					this.showDisableAccountDialog = false
					if (this.$team.doc.payment_mode === 'Prepaid Credits') {
						this.showAddPrepaidCreditsDialog = true
					} else {
						confirmDialog({
							title: t('Multiple unpaid invoices'),
							message: t(
								'You have multiple unpaid invoices. Please pay them from the invoices page',
							),
							primaryAction: {
								label: t('Go to invoices'),
								variant: 'solid',
								onClick: ({ hide }) => {
									router.push({ name: 'BillingInvoices' })
									hide()
								},
							},
						})
					}
				} else {
					let invoice = this.unpaidInvoices
					if (invoice.amount_due > minAmount) {
						this.showDisableAccountDialog = false
						confirmDialog({
							title: t('Clear Unpaid Invoice'),
							message: tr(
								'You have an unpaid invoice of {symbol} {amount}. Please clear it before disabling the account.',
								{
									symbol: invoice.currency === 'INR' ? '₹' : '$',
									amount: invoice.amount_due,
								},
							),
							primaryAction: {
								label: t('Settle it now'),
								variant: 'solid',
								onClick: ({ hide }) => {
									if (
										invoice.stripe_invoice_url &&
										this.$team.doc.payment_mode === 'Card'
									) {
										window.open(
											`/api/method/press.api.client.run_doc_method?dt=Invoice&dn=${invoice.name}&method=stripe_payment_url`,
										)
									} else {
										this.showAddPrepaidCreditsDialog = true
									}
									hide()
								},
							},
						})
					}
				}
			}

			// validate if any active servers
			if (this.showActiveServersDialog) {
				const activeServersDialog = defineAsyncComponent(
					() => import('../../ActiveServersDialog.vue'),
				)
				renderDialog(h(activeServersDialog))
				return
			}
			this.$resources.disableAccount.submit({
				totp_code: disableAccount2FACode,
			})
		},
		confirmPublisherAccount() {
			confirmDialog({
				title: t('Become a marketplace app developer?'),
				message: t(
					'You will be able to publish apps to our Marketplace upon confirmation.',
				),
				onSuccess: ({ hide }) => {
					toast.promise(
						this.$team.setValue.submit(
							{
								is_developer: 1,
							},
							{
								onSuccess: () => {
									hide()
									this.$router.push({
										name: 'Marketplace App List',
									})
								},
								onError(e) {
									console.error(e)
								},
							},
						),
						{
							success: t('You can now publish apps to our Marketplace'),
							error: t('Failed to mark you as a developer'),
							loading: t('Making you a developer...'),
						},
					)
				},
			})
		},
	},
}
</script>
