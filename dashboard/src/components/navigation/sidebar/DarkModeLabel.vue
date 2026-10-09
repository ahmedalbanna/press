<script setup lang="ts">
import { Badge } from 'frappe-ui';
import LucideCheck from '~icons/lucide/check';
import LucideMoon from '~icons/lucide/moon';
import { themeName } from '@/utils/useTheme';
</script>

<template>
  <div class='flex items-center gap-2 w-full text-ink-gray-7'>
    <LucideMoon class='size-4 text-ink-gray-6' />
    <span>{{ t('Dark Mode') }}</span>
    <LucideCheck v-if="themeName === 'dark'" class='size-4 shrink-0 text-green-600' />
    <Badge label="beta" theme="orange" class="ml-auto" />
  </div>
</template>
