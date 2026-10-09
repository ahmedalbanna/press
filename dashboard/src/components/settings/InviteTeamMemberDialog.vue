<template>
	<Dialog
		:options="{
			title: t('Invite User'),
			actions: [
				{
					label: t('Invite Member'),
					variant: 'solid',
					onClick: inviteMember,
				},
			],
		}"
		v-model="show"
	>
		<template #body-content>
			<div class="space-y-4">
				<FormControl :label="t('Email')" v-model="email" />
				<Combobox
					v-model="selectedRole"
					:label="t('Role') + ' *'"
					required
					:options="roleOptions"
					:placeholder="t('Select a role')"
					open-on-focus
				/>
			</div>
		</template>
	</Dialog>
</template>

<script>
import { Combobox } from 'frappe-ui'
import { toast } from 'vue-sonner'
import router from '../../router'
import { DashboardError } from '../../utils/error'
import { getToastErrorMessage } from '../../utils/toast'
import { t } from '../../utils/language'

export default {
	components: { Combobox },
	emits: ['success'],
	data() {
		return {
			email: '',
			show: true,
			selectedRole: 'Admin',
		}
	},
	resources: {
		roles() {
			return {
				type: 'list',
				doctype: 'Press Role',
				fields: ['name', 'title'],
				initialData: [],
				auto: true,
			}
		},
	},
	computed: {
		roleOptions() {
			let roleItems = [{ label: 'Admin', value: 'Admin' }]
			if (this.$resources.roles.data) {
				for (let role of this.$resources.roles.data) {
					roleItems.push({ label: role.title, value: role.name })
				}
			}
			return [
				{
					group: t('Roles'),
					hideLabel: true,
					options: roleItems,
				},
				{
					group: t('Actions'),
					hideLabel: true,
					options: [
						{
							type: 'custom',
							key: 'create_role',
							label: t('Create Role'),
							condition: () => true,
							onClick: () => {
								router.push({
									name: 'SettingsPermissionRoles',
									query: { createRole: 'true' },
								})
							},
						},
					],
				},
			]
		},
	},
	methods: {
		t,
		inviteMember() {
			toast.promise(
				this.$team.inviteTeamMember.submit(
					{
						email: this.email,
						...(this.selectedRole !== 'Admin' && {
							roles: [this.selectedRole],
						}),
					},
					{
						validate: () => {
							if (!this.email) {
								throw new DashboardError(t('Email is required'))
							}
						},
					},
				),
				{
					loading: t('Sending Invite...'),
					success: () => {
						this.show = false
						this.$emit('success')
						return t('Invite Sent!')
					},
					error: (e) => getToastErrorMessage(e),
				},
			)
		},
	},
}
</script>
