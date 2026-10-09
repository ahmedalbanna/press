<template>
	<Dialog
		v-model="open"
		:options="{
			title: 'Access Request',
			actions: [
				{
					label: 'Cancel',
					variant: 'outline',
					onClick: () => (open = false),
				},
				{
					label: 'Request',
					variant: 'solid',
					onClick: () => request.submit(),
				},
			],
		}"
	>
		<template #body-content>
			<div class="space-y-4 text-base">
				<p>{{ t('Are you sure you want to request access to this resource?') }}</p>
				<div class="space-y-2">
					<p><span class="font-medium">{{ t('Type:') }}</span> {{ props.doctype }}</p>
					<p><span class="font-medium">{{ t('Resource:') }}</span> {{ props.docname }}</p>
				</div>
				<Textarea
					size="sm"
					:placeholder="t('Why do you need access?')"
					v-model="reason"
				/>
				<div
					v-if="
						Object.values(permissionsMeta).find(
							(permission) => permission.enabled,
						)
					"
					class="space-y-2"
				>
					<p class="font-medium">{{ t('Permissions:') }}</p>
					<div class="grid grid-cols-2 gap-2">
						<template v-for="(permission, key) in permissionsMeta" :key="key">
							<Checkbox
								v-if="permission.enabled"
								:model-value="permissionsState[key]"
								:label="permission.label"
								@update:model-value="
									(value: boolean) => {
										permissionsState[key] = value;
									}
								"
							/>
						</template>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup lang="ts">
import { createResource } from 'frappe-ui';
import { computed, reactive, ref } from 'vue';
import { toast } from 'vue-sonner';
import { Checkbox, Textarea } from 'frappe-ui';
import { t } from '../utils/language';

const props = defineProps<{
	doctype: string;
	docname: string;
}>();

const open = ref(true);
const reason = ref('');

const permissionsState = reactive({
	login_as_administrator: false,
	site_domains: false,
	site_release_group: false,
	bench_ssh: false,
});

const permissionsMeta = computed(() => ({
	login_as_administrator: {
		label: t('Login as Administrator'),
		enabled: props.doctype === 'Site',
	},
	site_domains: {
		label: t('Domains'),
		enabled: props.doctype === 'Site',
	},
	site_release_group: {
		label: t('Release Group'),
		enabled: props.doctype === 'Site',
	},
	bench_ssh: {
		label: t('SSH Access'),
		enabled:
			props.doctype === 'Release Group' || permissionsState.site_release_group,
	},
}));

const request = createResource({
	url: 'press.api.client.insert',
	makeParams: () => {
		const permission = Object.keys(permissionsMeta.value).reduce(
			(acc, permission) => {
				// @ts-ignore
				acc[permission] = permissionsState[permission];
				return acc;
			},
			{} as Record<string, boolean>,
		);

		return {
			doc: {
				doctype: 'Support Access',
				reason: reason.value,
				resources: [
					{
						document_type: props.doctype,
						document_name: props.docname,
					},
				],
				...permission,
			},
		};
	},
	onSuccess: () => {
		open.value = false;
		toast.success('Access request submitted');
	},
	onError: () => toast.error('There was an error submitting your request'),
});
</script>
