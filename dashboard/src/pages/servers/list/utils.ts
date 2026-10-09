import { createDocumentResource } from 'frappe-ui'
import { t, tr } from '../../../utils/language'
import { toast } from 'vue-sonner'
import { confirmDialog } from '@/utils/components'
import router from '@/router'

export function dropBench(bench: any) {
  const releaseGroup = createDocumentResource({
    doctype: 'Release Group',
    name: bench.name,
  })

	confirmDialog({
		title: t('Drop Bench'),
		message: tr('Are you sure you want to drop the bench <b>{bench}</b>?', { bench: bench.title }),
		fields: [
			{
				label: t('Please type the bench name to confirm'),
				fieldname: 'confirmBenchName',
			},
		],
		primaryAction: {
			label: t('Drop'),
			theme: 'red',
			onClick: ({ hide, values }) => {
				if (releaseGroup.delete.loading) return
				if (values.confirmBenchName !== bench.title) {
					throw new Error('Bench name does not match')
				}
				toast.promise(
					releaseGroup.delete.submit(null, {
						onSuccess: () => {
							hide()
						},
					}),
					{
						loading: t('Dropping bench...'),
						success: t('Bench dropped successfully'),
						error: (error) =>
							error.messages?.length
								? error.messages.join('\n')
								: t('Failed to drop bench'),
					},
				)
			},
		},
	})
}

export const onDropServer = (server: any) => {
	const serverFullRes = createDocumentResource({
		doctype: 'Server',
		name: server.name,
		whitelistedMethods: {
			dropServer: 'drop_server',
		},
	})

	confirmDialog({
		title: t('Drop Server'),
		message: server.is_unified_server
			? `<div class="prose text-base">${t('Are you sure you want to drop your unified server?')}<br><br>${t('The following server will be dropped')}<ul><li>${server.title} (<b>${server.name}</b>)</li></ul><br>${t('This action cannot be undone.')}</div>`
			: `<div class="prose text-base">${t('Are you sure you want to drop your servers?')}<br><br>${t('Following servers will be dropped')}<ul><li>${server.title} (<b>${server.name}</b>)</li><li>${server.database_server}</li></ul><br>${t('This action cannot be undone.')}</div>`,
		fields: [
			{
				label: t("Please type either server's name or title to confirm"),
				fieldname: 'confirmServerName',
			},
		],
		primaryAction: {
			label: t('Drop Server'),
			theme: 'red',
		},
		onSuccess({ hide, values }) {
			if (serverFullRes.dropServer.loading) return
			const confirmed = values.confirmServerName
			if (
				confirmed !== server.name &&
				confirmed !== server.database_server &&
				confirmed.trim() !== server.title.trim()
			) {
				throw new Error('Server name does not match')
			}
			toast.promise(serverFullRes.dropServer.submit().then(hide), {
				loading: t('Dropping...'),
				success: () => {
					router.push({ name: 'Server List' })
					return t('Server dropped')
				},
				error: (error) =>
					error.messages?.length
						? error.messages.join('\n')
						: t('Failed to drop servers'),
			})
		},
	})
}
