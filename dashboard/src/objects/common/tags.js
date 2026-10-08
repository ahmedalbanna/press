import { h, defineAsyncComponent } from 'vue';
import { confirmDialog, icon, renderDialog } from '../../utils/components';
import { toast } from 'vue-sonner';
import { getToastErrorMessage } from '../../utils/toast';
import { t, tr } from '../../utils/language';

export function tagTab(doctype) {
	return {
		label: t('Tags'),
		icon: icon('tag'),
		condition: (record) => {
			return (
				doctype != 'Server' ||
				(doctype == 'Server' && record.doc?.status !== 'Archived')
			);
		},
		route: 'tags',
		type: 'list',
		list: {
			doctype: 'Resource Tag',
			filters: (documentResource) => {
				return {
					parent: documentResource.name,
					parenttype: documentResource.doctype,
				};
			},
			orderBy: 'creation desc',
			columns: [
				{
					label: t('Tag'),
					fieldname: 'tag_name',
				},
			],
			primaryAction({ listResource: tags, documentResource }) {
				return {
					label: t('Add Tag'),
					slots: {
						prefix: icon('plus'),
					},
					onClick() {
						let AddTagDialog = defineAsyncComponent(
							() => import('../../components/AddTagDialog.vue'),
						);
						renderDialog(
							h(AddTagDialog, {
								doctype: documentResource.doctype,
								docname: documentResource.name,
								onAdded() {
									tags.reload();
								},
							}),
						);
					},
				};
			},
			rowActions({ row, listResource: tags, documentResource }) {
				return [
					{
						label: t('Remove'),
						onClick() {
							if (documentResource.removeTag.loading) return;
							confirmDialog({
								title: t('Remove Tag'),
								message: tr('Are you sure you want to remove the tag <b>{tag}</b>?', {
									tag: row.tag_name,
								}),
								onSuccess({ hide }) {
									documentResource.removeTag.submit(
										{
											tag: row.tag_name,
										},
										{
											onSuccess() {
												tags.reload();
												hide();
											},
										},
									);
									toast.promise(documentResource.removeTag.promise, {
										loading: 'Removing tag...',
										success: () => `Tag ${row.tag_name} removed`,
										error: (e) =>
											getToastErrorMessage(e, 'Failed to remove tag'),
									});
								},
							});
						},
					},
				];
			},
		},
	};
}
