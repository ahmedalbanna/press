<template>
	<Dialog
		:options="{
			title: t('Add Firewall Rule'),
			size: 'lg',
			icon: {
				name: 'shield',
				appearance: 'info',
			},
			actions: [
				{
					label: t('Submit'),
					variant: 'solid',
					onClick: onSubmit,
				},
			],
		}"
		:model-value="modelValue"
		@update:model-value="$emit('update:modelValue', $event)"
		@close="onClose"
	>
		<template #body-content>
			<div class="space-y-4">
				<FormControl
					v-model="values.source"
					:label="t('Source')"
					placeholder="1.2.3.4"
					type="text"
					size="sm"
					variant="subtle"
				/>
				<FormControl
					v-model="values.port"
					:label="t('Port')"
					type="text"
					size="sm"
					variant="subtle"
				/>
				<FormControl
					v-model="values.protocol"
					:label="t('Protocol')"
					type="select"
					:options="[
						{
							label: t('TCP'),
							value: 'TCP',
						},
						{
							label: t('UDP'),
							value: 'UDP',
						},
					]"
					size="sm"
					variant="subtle"
				/>
				<FormControl
					v-model="values.action"
					:label="t('Action')"
					type="select"
					:options="[
						{
							label: t('Deny'),
							value: 'Deny',
						},
						{
							label: t('Allow'),
							value: 'Allow',
						},
					]"
					size="sm"
					variant="subtle"
				/>
			</div>
		</template>
	</Dialog>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { FormControl } from 'frappe-ui';

defineProps<{
	modelValue: boolean;
}>();

const emit = defineEmits<{
	(event: 'update:modelValue', open: boolean): void;
	(
		event: 'submit',
		values: {
			source: string;
			port: string;
			protocol: string;
			action: string;
		},
	): void;
}>();

const values = reactive({
	source: '',
	port: '',
	protocol: 'TCP',
	action: 'Deny',
});

const onClose = () => {
	values.source = '';
	values.port = '';
	values.protocol = 'TCP';
	values.action = 'Deny';
	emit('update:modelValue', false);
};

const onSubmit = () => {
	emit('submit', values);
	onClose();
};
</script>
