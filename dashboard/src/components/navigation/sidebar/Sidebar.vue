<script setup lang="ts">
import { Button, Dropdown } from 'frappe-ui'
import { computed, defineAsyncComponent, provide, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { session } from '@/data/session'
import { getTeam } from '@/data/team'
import { mobileNav, partnerRegistrationModalOpen } from '@/data/ui'
import { isMobile } from '@/utils/device'
import { setTheme } from '@/utils/useTheme'
import { setLanguage, getLanguage, t } from '@/utils/language'
import LucideBookText from '~icons/lucide/book-text'
import LucideChevronDown from '~icons/lucide/chevron-down'
import LucideGlobe from '~icons/lucide/globe'
import LucideSupport from '~icons/lucide/life-buoy'
import LucideMessageSquareCode from '~icons/lucide/message-square-code'
import LucideMoon from '~icons/lucide/moon'
import AttentionWidget from './AttentionWidget.vue'
import DarkModeLabel from './DarkModeLabel.vue'
import Item from './Item.vue'
import ItemGroup from './ItemGroup.vue'
import NavList from './NavList.vue'

const $team = getTeam()
const $session = session
const router = useRouter()

const showTeamSwitcher = ref(false)
const collapsed = ref(localStorage.collapsed === 'true')

const activePartner = computed(() =>
	Boolean(
		$team?.doc?.erpnext_partner && $team?.doc?.partner_status === 'Active',
	),
)
// Once an onboarding record exists (or they are an active partner) the
// "Partnership" item appears in the sidebar instead — see NavList.vue.
const canBecomePartner = computed(
	() => !activePartner.value && !$team?.doc?.has_partner_onboarding,
)

const collapsedCss = computed(() =>
	collapsed.value
		? 'md:w-0 md:overflow-hidden md:opacity-0 whitespace-nowrap'
		: 'md:opacity-100  whitespace-nowrap',
)

const collapsePanel = () => {
	localStorage.collapsed = collapsed.value = !collapsed.value
}

provide('collapsed', collapsed)
provide('collapsedCss', collapsedCss)

const SwitchTeamDialog2 = defineAsyncComponent(
	() => import('../../SwitchTeamDialog.vue'),
)

const support = () => {
	window.location.assign('mailto:support@albannatech.com')
}
const docs = () => {
	window.location.assign('mailto:support@albannatech.com')
}

const feedback = () => {
	window.location.assign('mailto:support@albannatech.com')
}

watch(router.currentRoute, () => {
	if (isMobile() && mobileNav.value) mobileNav.value = false
})

const userDropdownOptions = computed(() => [
	{
		label: t('Change Team'),
		icon: 'command',
		condition: () =>
			$team?.doc?.valid_teams?.length > 1 || $team?.doc?.is_desk_user,
		onClick: () => (showTeamSwitcher.value = true),
	},

	{
		label: t('Theme'),
		icon: LucideMoon,
		submenu: [
			{ label: t('Light Mode'), icon: 'sun', onClick: () => setTheme('light') },
			// dropdown component as per this frappe-ui version doesnt support suffix slot
			// so make the icon itself icon+label+beta badge
			{ icon: DarkModeLabel, onClick: () => setTheme('dark') },
		],
	},

	{
		label: t('Language'),
		icon: LucideGlobe,
		submenu: [
			{ label: t('English'), icon: 'check', onClick: () => setLanguage('en') },
			{ label: 'العربية', icon: 'check', onClick: () => setLanguage('ar') },
		],
	},

	{
		label: t('Become a Partner'),
		icon: LucideGlobe,
		condition: () => canBecomePartner.value,
		onClick: () => (partnerRegistrationModalOpen.value = true),
	},

	{ label: t('Logout'), icon: 'log-out', onClick: $session.logout.submit },
])

const helpDropdownOptions = computed(() => [
	{ label: t('Docs'), icon: LucideBookText, onClick: docs },
	{ label: t('Get Support'), icon: LucideSupport, onClick: support },
	{ label: t('Share Feedback'), icon: LucideMessageSquareCode, onClick: feedback },
])
</script>

<template>
	<aside
		class="relative flex md:min-h-screen p-2 gap-1 flex-col border-r transition-[width]
    bg-[#0F172A] overflow-x-hidden"
		:class='collapsed ? " md:w-12" : "w-full md:w-[256px]"'
	>
		<div
			class="flex gap-2 items-center border-y md:border-0 p-2 md:p-0 -m-2 md:m-0 h-[44px] md:h-auto"
		>
			<img src="/albannatech-logo-light.svg" alt="AlbannaTech" class="h-6 w-auto md:hidden mr-auto" />

			<Dropdown :options="userDropdownOptions">
				<template v-slot="{ open }">
					<button
						class="flex gap-2 w-fit md:w-full p-1.5 items-center rounded md:mb-1 text-white bg-white/10 md:bg-transparent   hover:bg-white/10"
						:class="[open ? 'md:bg-white/10 shadow-sm' : ''
              , collapsed? 'md:p-0': 'md:p-1'] "
					>
						<img src="/albannatech-logo-light.svg" alt="AlbannaTech" class="h-8 w-auto hidden md:flex shrink-0" />
						<LucideUser class="size-3.5 -mr-1.5 md:hidden text-gray-300" />

						<div
							class="flex flex-col gap-0.5 ml-1 min-w-0 md:m-0"
							:class="collapsedCss"
						>
						<div class="text-base font-medium hidden md:flex text-white">
							AlbannaTech
						</div>

						<div class="text-sm text-left text-gray-300 truncate">
							{{ $team?.get.loading ? $t('Loading...') : $team?.doc?.user }}
						</div>
						</div>

					<LucideChevronDown
						class="md:ml-auto size-4 shrink-0 text-gray-300"
						:class="collapsedCss"
					/>
					</button>
				</template>
			</Dropdown>

			<button
				class="p-2 md:hidden bg-white/10 rounded"
				@click="mobileNav = !mobileNav"
			>
				<lucide-x v-if="mobileNav" class="size-3" />
				<lucide-menu v-else class="size-3" />
			</button>
		</div>

		<nav
			class="flex-col flex-1 gap-1 md:flex py-3 md:p-0 md:mt-1"
			:class="[mobileNav ? 'flex border-b' : 'hidden']"
		>
			<NavList>
				<template v-slot="{ list }">
					<template v-for="(item, _) in list" :key="item.name">
						<ItemGroup v-if="item.children" v-bind="item" />
						<component
							v-else-if="item.customComponent"
							:is="item.customComponent"
							:disabled="item.disabled"
						/>
						<Item v-else v-bind="item" />
					</template>
				</template>
			</NavList>

			<span class="mt-auto" />

			<AttentionWidget v-if="!collapsed" />

			<div
				:class='collapsed ? "flex-col" : "flex-row"'
				class="flex gap-1 justify-between items-center"
			>
				<Dropdown :options="helpDropdownOptions">
					<Button variant="ghost" class="text-gray-300">
						<template #prefix v-if="!collapsed">
							<LucideCircleQuestionMark class="size-4" />
						</template>

						<LucideCircleQuestionMark v-if="collapsed" class="size-4" />

						<template v-if="!collapsed">{{ $t('Help') }}</template>
					</Button>
				</Dropdown>

				<Button
					variant="ghost"
					class="hidden md:flex text-gray-300"
					:class='collapsed ? "mb-2" : ""'
					@click="collapsePanel"
				>
					<template #icon>
						<LucidePanelLeft
							class="size-4 transition-transform duration-500"
							:class='collapsed ? "rotate-180" : ""'
						/>
					</template>
				</Button>
			</div>
		</nav>

		<!-- TODO: update component name after dashboard-beta merges -->
		<SwitchTeamDialog2
			v-model="showTeamSwitcher"
			:key="String(showTeamSwitcher)"
		/>
	</aside>
</template>