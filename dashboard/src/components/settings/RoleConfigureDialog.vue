<template>
	<Dialog
		v-if="role"
		:options="{ title: `${role.title}`, size: 'xl' }"
		v-model="show"
	>
		<template v-slot:body-content>
		<FTabs
			:tabs="[
				{
					label: t('Members'),
					value: 'members',
				},
				{
					label: t('Settings'),
					value: 'settings',
				},
			]"
			v-model="tabIndex"
		>
				<template #tab-item="{ tab }">
					<div
						class="flex cursor-pointer items-center gap-1.5 py-3 text-base text-ink-gray-6 duration-300 ease-in-out hover:border-outline-gray-3 hover:text-ink-gray-9 focus:outline-none focus:transition-none [&>div]:pl-0"
					>
						<span>{{ tab.label }}</span>
					</div>
				</template>
				<template #tab-panel="{ tab }">
					<div v-if="tab.value === 'members'" class="text-base">
						<div class="my-4 flex gap-2">
							<div class="flex-1">
								<FormControl
									type="combobox"
									:options="autoCompleteList"
									:modelValue="member?.value"
									@update:modelValue="
										member = autoCompleteList.find(
											(option) => option.value === $event,
										)
									"
									:placeholder="t('Select a member to add')"
								/>
							</div>
							<Button
								variant="solid"
								:label="t('Add Member')"
								:disabled="!member?.value"
								:loading="$resources.role.addUser?.loading"
								@click="() => addUser(member.value)"
							/>
						</div>
						<div class="rounded border px-3">
							<div class="mt-2 text-ink-gray-6">{{ t('Members') }}</div>
							<div
								v-if="roleUsers.length === 0"
								class="p-6 text-center text-ink-gray-5"
							>
								<span>{{ t('No members added to this role.') }}</span>
							</div>
							<div v-else class="flex flex-col divide-y">
								<div
									v-for="user in roleUsers"
									class="flex justify-between py-3"
								>
									<UserWithAvatarCell
										:avatarImage="user.user_image"
										:fullName="user.full_name"
										:email="user.user"
										:key="user.user"
									/>
									<Button variant="ghost" @click="() => removeUser(user.user)">
										<template #icon>
											<lucide-x class="h-4 w-4 text-ink-gray-6" />
										</template>
									</Button>
								</div>
							</div>
						</div>
					</div>
					<div v-else-if="tab.value === 'settings'" class="mt-4 text-base">
						<div class="space-y-3">
							<div class="rounded border p-4">
								<Switch
									class="ml-2"
									v-model="adminAccess"
									:label="t('Admin Access')"
									:description="t('Grants team owner like access to the members. Includes access to all pages and settings.')"
								/>
							</div>
							<div class="space-y-1 rounded border p-4">
								<h2 class="mb-2 ml-2 font-semibold">{{ t('Page Access') }}</h2>
								<Switch
									v-model="allowBilling"
									:label="t('Allow Billing Access')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowApps"
									:label="t('Allow Apps Access')"
									:disabled="adminAccess"
								/>
								<Switch
									v-if="$team.doc.erpnext_partner"
									v-model="allowPartner"
									:label="t('Allow Partner Access')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowSiteCreation"
									:label="t('Allow Site Creation')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowBenchCreation"
									:label="t('Allow Bench Creation')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowServerCreation"
									:label="t('Allow Server Creation')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowWebhookConfiguration"
									:label="t('Allow Webhook Configuration')"
									:disabled="adminAccess"
								/>
							</div>
							<div v-if="allowPartner" class="space-y-1 rounded border p-4">
								<h2 class="mb-2 ml-2 font-semibold">{{ t('Partner Permissions') }}</h2>
								<Switch
									v-model="allowDashboard"
									:label="t('Allow Dashboard Access')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowLeads"
									:label="t('Allow Leads Access')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowCustomer"
									:label="t('Allow Customer Access')"
									:disabled="adminAccess"
								/>
								<Switch
									v-model="allowContribution"
									:label="t('Allow Contribution Access')"
									:disabled="adminAccess"
								/>
							</div>
						</div>
					</div>
				</template>
			</FTabs>
		</template>
	</Dialog>
</template>

<script>
import { Switch, Tabs } from 'frappe-ui';
import { toast } from 'vue-sonner';
import UserWithAvatarCell from '../UserWithAvatarCell.vue';
import { getToastErrorMessage } from '../../utils/toast';
import { t, tr } from '../../utils/language';

export default {
	props: {
		roleId: { type: String, required: true },
	},
	components: {
		UserWithAvatarCell,
		FTabs: Tabs,
		Switch,
	},
	data() {
		return {
			member: {},
			show: true,
			tabIndex: 0,
		};
	},
	resources: {
		role() {
			return {
				type: 'document',
				doctype: 'Press Role',
				name: this.roleId,
				whitelistedMethods: {
					addUser: 'add_user',
					removeUser: 'remove_user',
					bulkDelete: 'delete_permissions',
				},
			};
		},
	},
	computed: {
		role() {
			return this.$resources.role.doc;
		},
		roleUsers() {
			return this.role?.users || [];
		},
		autoCompleteList() {
			const isNotGroupMember = (u) =>
				!this.roleUsers.map(({ user }) => user).includes(u);
			return this.$team.doc.team_members
				?.filter(({ user }) => isNotGroupMember(user))
				.map(({ user }) => ({ label: user, value: user }));
		},
		adminAccess: {
			get() {
				return !!this.role?.admin_access;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						admin_access: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowBilling: {
			get() {
				return !!this.role?.allow_billing;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_billing: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowApps: {
			get() {
				return !!this.role?.allow_apps;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_apps: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowPartner: {
			get() {
				return !!this.role?.allow_partner;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_partner: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowSiteCreation: {
			get() {
				return !!this.role?.allow_site_creation;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_site_creation: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowBenchCreation: {
			get() {
				return !!this.role?.allow_bench_creation;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_bench_creation: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowServerCreation: {
			get() {
				return !!this.role?.allow_server_creation;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_server_creation: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowWebhookConfiguration: {
			get() {
				return !!this.role?.allow_webhook_configuration;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_webhook_configuration: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowDashboard: {
			get() {
				return !!this.role?.allow_dashboard;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_dashboard: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowLeads: {
			get() {
				return !!this.role?.allow_leads;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_leads: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowCustomer: {
			get() {
				return !!this.role?.allow_customer;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_customer: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
		allowContribution: {
			get() {
				return !!this.role?.allow_contribution;
			},
			set(value) {
				this.$resources.role.setValue.submit(
					{
						allow_contribution: value,
					},
					{ onSuccess: this.$session.roles.reload },
				);
			},
		},
	},
	methods: {
		t,
		addUser(user) {
			return toast.promise(this.$resources.role.addUser.submit({ user }), {
				loading: tr('Adding {user} to {role}', { user, role: this.role.title }),
				success: () => {
					this.member = {};
					return tr('{user} added to {role}', { user, role: this.role.title });
				},
				error: (e) => getToastErrorMessage(e),
			});
		},
		removeUser(user) {
			return toast.promise(this.$resources.role.removeUser.submit({ user }), {
				loading: tr('Removing {user} from {role}', { user, role: this.role.title }),
				success: () => tr('{user} removed from {role}', { user, role: this.role.title }),
				error: (e) => getToastErrorMessage(e),
			});
		},
	},
};
</script>
