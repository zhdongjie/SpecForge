<script lang="ts" setup>
import { useVModel } from '@vueuse/core'

defineOptions({
  name: 'ConfirmDialog'
})

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  confirmButtonText: {
    type: String,
    default: ''
  },
  cancelButtonText: {
    type: String,
    default: ''
  },
  confirmButtonColor: {
    type: String,
    default: 'error'
  },
  maxWidth: {
    type: [String, Number],
    default: 480
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const dialogModel = useVModel(props, 'modelValue', emit)

const closeDialog = () => {
  dialogModel.value = false
  emit('cancel')
}

const confirmAction = () => {
  emit('confirm')
}
</script>

<template>
  <v-dialog v-model="dialogModel" :max-width="maxWidth">
    <v-card class="pa-2" prepend-icon="$warning" :title="title">
      <!-- content -->
      <v-card-text class="text-body-2">
        {{ message }}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>

        <!-- cancel button -->
        <v-btn
          height="32"
          size="small"
          variant="flat"
          width="80"
          @click="closeDialog"
        >
          {{ cancelButtonText }}
        </v-btn>

        <!-- confirm button -->
        <v-btn
          :color="confirmButtonColor"
          height="32"
          size="small"
          variant="flat"
          width="80"
          @click="confirmAction"
        >
          {{ confirmButtonText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
