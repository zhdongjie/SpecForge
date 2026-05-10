<script lang="ts" setup>
import appConfig from '@/appConfig'

defineOptions({
  name: 'AuthorizeHeader'
})

// props
defineProps({
  title: {
    type: String as PropType<string>,
    required: true
  },
  subtitle: {
    type: String as PropType<string>,
    required: true
  }
})
</script>

<template>
  <!-- logo -->
  <v-card-title class="d-flex align-center justify-center">
    <v-img alt="logo" class="mr-3" max-width="56" :src="appConfig.logo"></v-img>
    <h2 class="text-h4">
      {{ appConfig.name }}
    </h2>
  </v-card-title>

  <!-- title -->
  <v-card-text>
    <p class="text-h5 font-weight-regular">
      {{ title }}
    </p>
    <p class="my-2">
      {{ subtitle }}
    </p>
  </v-card-text>
</template>
