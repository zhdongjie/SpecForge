<script setup lang="ts">
defineOptions({
  name: 'CustomizerLayout'
})

// props
const props = defineProps({
  title: {
    type: String as PropType<string>,
    required: true
  }
})
</script>

<template>
  <div class="customizer-layout">
    <div class="text-body-1 my-4">
      {{ props.title }}
    </div>
    <slot />
  </div>
</template>
