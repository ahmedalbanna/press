<template>
	<div class="p-5">
		<ObjectList :options="options" ref="mandateList" />

		<BillingDetailsDialog
			v-if="showBillingDetailsDialog"
			v-model="showBillingDetailsDialog"
			:showMessage="true"
			@success="
				() => {
					$resources.billingDetails.reload();
					showSetupDialog = true;
				}
			"
		/>

		<Dialog
			v-model="showSetupDialog"
			:options="{ title: t('Setup UPI Autopay') }"
			:class="{ 'razorpay-active': razorpayOpen }"
		>
			<template #body-content>
				<UPIAutopayForm
					v-if="showSetupDialog"
					@success="onAutopaySuccess"
					@initiate="handleInitiate"
				/>
			</template>
		</Dialog>
		<UPIAutopayForm
			v-if="razorpayProcessing"
			class="hidden"
			:is-background="true"
			:passed-amount="tempAmount"
			@opened="dismissLoadingToast"
			@success="onAutopaySuccess"
			@cancel="onAutopayCancel"
		/>
	</div>
</template>
<script>
import { h } from 'vue';
import ObjectList from '../components/ObjectList.vue';
import BillingDetailsDialog from '../components/billing/BillingDetailsDialog.vue';
import UPIAutopayForm from '../components/billing/UPIAutopayForm.vue';
import { FeatherIcon, Dialog, Button } from 'frappe-ui';
import Badge from '@/components/global/Badge.vue';
import { toast } from 'vue-sonner';
import { confirmDialog, icon } from '../utils/components';
import { t } from '../utils/language';

export default {
	name: 'BillingUPIAutopay',
	components: {
		ObjectList,
		BillingDetailsDialog,
		UPIAutopayForm,
		Dialog,
		Button,
		FeatherIcon,
	},
	data() {
		return {
			showSetupDialog: false,
			razorpayProcessing: false,
			tempAmount: null,
			loadingToast: null,
			showBillingDetailsDialog: false,
		};
	},
	resources: {
		billingDetails() {
			return {
				url: 'press.api.account.get_billing_information',
				auto: true,
			};
		},
		cancelMandate() {
			return {
				url: 'press.api.billing.cancel_razorpay_mandate',
				onSuccess() {
					toast.success(t('Mandate cancelled'));
				},
				onError() {
					toast.error(t('Could not cancel mandate'));
				},
			};
		},
	},
	computed: {
		billingDetailsSummary() {
			const d = this.$resources.billingDetails.data;
			if (!d) return '';
			const { billing_name, address_line1, city, state, country, pincode } = d;
			return [billing_name, address_line1, city, state, country, pincode]
				.filter(Boolean)
				.join(', ');
		},
		options() {
			return {
				doctype: 'Razorpay Mandate',
				fields: [
					'name',
					'mandate_id',
					'status',
					'method',
					'auth_type',
					'max_amount',
					'expires_on',
					'upi_vpa',
					'creation',
				],
				filterByTeam: true,
				emptyStateMessage: t('No UPI Autopay mandates set up.'),
				columns: [
					{
						label: t('UPI ID'),
						fieldname: 'upi_vpa',
						format(value) {
							return value || '-';
						},
					},
					{
						label: t('Status'),
						fieldname: 'status',
						type: 'Component',
						component({ row }) {
							return h(Badge, { label: row.status });
						},
					},
					{
						label: t('Max Amount'),
						fieldname: 'max_amount',
						format(value) {
							return `₹${value?.toLocaleString('en-IN') || 0}`;
						},
					},
					{
						label: t('Expires On'),
						fieldname: 'expires_on',
						type: 'Date',
					},
					{
						label: '',
						fieldname: 'creation',
						type: 'Timestamp',
						align: 'right',
					},
				],
				rowActions: ({ listResource, row }) => {
					return [
						{
							label: t('Cancel'),
							onClick: () => {
								confirmDialog({
									title: t('Cancel UPI Autopay'),
									message: t(
										'Are you sure you want to cancel this UPI Autopay mandate?',
									),
									onSuccess: ({ hide }) => {
										this.$resources.cancelMandate
											.submit({
												mandate_name: row.name,
											})
											.then(() => {
												listResource.reload();
												hide();
											});
									},
								});
							},
							condition: () =>
								row.status === 'Active' || row.status === 'Pending',
						},
					];
				},
				orderBy: 'creation desc',
				primaryAction: ({ listResource }) => {
					const hasActiveMandate = listResource.data?.some(
						(mandate) => mandate.status === 'Active',
					);
					if (!hasActiveMandate) {
						return {
							label: t('Setup Autopay'),
							slots: {
								prefix: icon('plus'),
							},
							onClick: () => {
								if (!this.billingDetailsSummary) {
									this.showBillingDetailsDialog = true;
									return;
								}
								this.showSetupDialog = true;
							},
						};
					}
				},
			};
		},
	},
	methods: {
		handleInitiate(amount) {
			this.tempAmount = amount;
			this.showSetupDialog = false;
			this.loadingToast = toast.loading(t('Opening payment window...'));
			this.$nextTick(() => {
				this.razorpayProcessing = true;
			});
		},
		onAutopaySuccess() {
			this.razorpayProcessing = false;
			this.showSetupDialog = false;
			this.$refs.mandateList?.reloadListView();
			this.$team.reload();
		},
		onAutopayCancel() {
			this.razorpayProcessing = false;
			this.$refs.mandateList?.reloadListView();
		},
		dismissLoadingToast() {
			toast.dismiss(this.loadingToast);
			this.loadingToast = null;
		},
	},
};
</script>
