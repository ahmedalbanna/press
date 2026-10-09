<script setup>
import OnboardingRightSidebarHeader from '@/onboarding/onboardingRightContainer/OnboardingRightSidebarHeader.vue'
import { t } from '../../utils/language'

const resources = [
	{
		title: t('Benefits of becoming a partner'),
		link: 'https://docs.frappe.io/partner-guide/why-partner',
	},
	{
		title: t('Partner program guide'),
		link: 'https://docs.frappe.io/partner-guide/guide-for-new-partners',
	},
	{
		title: t('Certifications guide'),
		link: 'https://docs.frappe.io/school/partner-certification',
	},
	{
		title: t('Getting started with AlbannaTech'),
		link: 'https://frappe.io/cloud',
	},
	{
		title: t('Partnership tiers guide'),
		link: 'https://frappe.io/partners/plans',
	},
]
</script>

<template>
	<div class="rounded-lg border border-outline-gray-1 bg-surface-white p-4">
		<OnboardingRightSidebarHeader />
	</div>
	<div
		class="flex h-full flex-col overflow-hidden rounded-lg border border-outline-gray-1 bg-surface-white"
	>
		<!-- Title: Resources -->
		<div class="px-4 py-3">
			<p class="text-p-sm font-medium text-ink-gray-5">{{ t('Resources') }}</p>
		</div>

		<div class="px-1.5">
			<div
				v-for="(resource, index) in resources"
				:key="resource.title"
				class="border-b border-outline-gray-1 px-4 py-3 transition-colors hover:bg-surface-gray-1"
				:class="{ 'border-b-0': index === resources.length - 1 }"
			>
				<a
					:href="resource.link"
					target="_blank"
					class="block text-p-sm leading-5 text-ink-gray-8"
				>
					{{ resource.title }}
				</a>
			</div>
		</div>

		<div class="mt-auto border-t border-outline-gray-1 px-4 py-3">
			<p class="text-p-sm leading-5 text-ink-gray-6">
				{{ t('Questions? Contact') }}
				<a
					href="mailto:sales@frappe.io"
					class="font-medium text-ink-gray-8 underline"
				>
					sales@frappe.io
				</a>
			</p>
		</div>
	</div>
</template>
