<script setup lang="ts">
import { Dialog } from 'frappe-ui'
import { computed, onMounted, ref } from 'vue'
import releaseGroup from '../../objects/group'
import { getDocResource } from '../../utils/resource'
import ObjectList from '../ObjectList.vue'
import { t } from '../../utils/language'

const props = defineProps<{ bench: string; releaseGroup: string }>()

const show = ref(true)
const group = getDocResource({
	doctype: 'Release Group',
	name: props.releaseGroup,
	whitelistedMethods: releaseGroup.whitelistedMethods,
})

onMounted(() => group.getAppVersions.submit({ bench: props.bench }))

const listOptions = computed(() => ({
	columns: [
		{ label: t('App'), fieldname: 'app' },
		{
			label: t('Repo'),
			fieldname: 'repository',
			format: (value: string, row: any) =>
				`${row.repository_owner}/${row.repository}`,
			link: (value: string, row: any) => row.repository_url,
		},
		{ label: t('Branch'), fieldname: 'branch', type: 'Badge' },
		{
			label: t('Commit'),
			fieldname: 'hash',
			type: 'Badge',
			format: (value: string) => value.slice(0, 7),
			link: (value: string, row: any) =>
				`https://github.com/${row.repository_owner}/${row.repository}/commit/${value}`,
		},
		{ label: t('Tag'), fieldname: 'tag', type: 'Badge' },
	],
	data: () => group.getAppVersions.data,
}))
</script>

<template>
	<Dialog v-model="show" :options="{ title: `Apps in ${bench}`, size: '6xl' }">
		<template #body-content>
			<ObjectList :options="listOptions" />
		</template>
	</Dialog>
</template>
