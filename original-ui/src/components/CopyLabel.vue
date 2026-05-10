<script setup lang="ts">
import type { PropType } from 'vue'
import { useClipboard } from '@vueuse/core'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

defineOptions({
  name: 'CopyLabel'
})

const { isSupported, copy } = useClipboard()

// props
defineProps({
  text: {
    type: String as PropType<string>,
    required: true
  }
})

// composables
const { t } = useI18n()

// states
const tooltip = ref('$original.common.copy')
const heartBeat = ref(false)

// methods
const copyText = (text: string) => {
  if (!isSupported.value) return

  copy(text)

  heartBeat.value = true
  tooltip.value = '$original.common.copied'

  setTimeout(() => {
    heartBeat.value = false
    tooltip.value = '$original.common.copy'
  }, 1000)
}
</script>

<template>
  <v-tooltip :disabled="!isSupported" location="bottom">
    <template #activator="{ props }">
      <span
        class="d-inline-block"
        :class="{
          'heart-beat': heartBeat === true && isSupported,
          'copy-text': isSupported,
          'cursor-pointer': isSupported
        }"
        v-bind="props"
        @click="copyText(text)"
      >
        {{ text }}
      </span>
    </template>
    <span class="text-caption">{{ t(tooltip) }}</span>
  </v-tooltip>
</template>

<style scoped lang="scss">
.copy-text {
  border-bottom: 1px dashed;
}
</style>
