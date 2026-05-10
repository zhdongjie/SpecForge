<script setup lang="ts">
import { IconApps, IconInbox, IconUserCog } from '@tabler/icons-vue'
import appConfig from '@/appConfig'

defineOptions({
  name: 'AppBarUserMenu'
})

// composables
const authorizeStore = useAuthorizeStore()
const userStore = useUserStore()
const { avatar, username, roles } = storeToRefs(userStore)

// states
const isOpenUserMenu = ref(false)
const icons = {
  userCog: IconUserCog,
  inbox: IconInbox,
  apps: IconApps
}

// methods
const logoutUser = async () => {
  await authorizeStore.logout()
}
</script>

<template>
  <v-menu
    v-model="isOpenUserMenu"
    :close-on-content-click="false"
    location="bottom end"
  >
    <template #activator="{ props }">
      <v-badge
        class="app-bar-tools app-bar-user-menu"
        color="success"
        :dot="true"
        offset-x="0"
        offset-y="24"
        overlap
      >
        <v-avatar v-bind="props" class="cursor-pointer" size="36">
          <v-img :src="avatar || appConfig.avatar" />
        </v-avatar>
      </v-badge>
    </template>
    <v-list
      class="py-4"
      color="primary"
      density="compact"
      :nav="true"
      width="220"
    >
      <v-list-item>
        <template #prepend>
          <v-badge
            class="mr-2"
            color="success"
            :dot="true"
            offset-x="2"
            offset-y="34"
            overlap
          >
            <v-avatar size="48">
              <v-img :src="avatar || appConfig.avatar" />
            </v-avatar>
          </v-badge>
        </template>
        <template #title>
          <div class="text-h6 my-1">
            {{ username }}
          </div>
        </template>

        <template #subtitle>
          <v-list-item-title class="text-caption">
            {{ roles.join(',') }}
          </v-list-item-title>
        </template>
      </v-list-item>

      <v-divider class="my-2" />

      <v-list-item :link="true" @click="isOpenUserMenu = false">
        <template #prepend>
          <v-icon :icon="icons.userCog" size="small"></v-icon>
        </template>
        <template #title>
          <v-list-item-title class="text-caption">My Profile</v-list-item-title>
        </template>
      </v-list-item>

      <!-- email -->
      <v-list-item :link="true">
        <template #prepend>
          <v-icon :icon="icons.inbox" size="small"></v-icon>
        </template>
        <template #title>
          <v-list-item-title class="text-caption">My Inbox</v-list-item-title>
        </template>
      </v-list-item>

      <!-- chat -->
      <v-list-item :link="true">
        <template #prepend>
          <v-icon :icon="icons.apps" size="small"></v-icon>
        </template>
        <template #title>
          <v-list-item-title class="text-caption">My Tasks</v-list-item-title>
        </template>
        <template #append>
          <v-list-item-action>
            <v-badge color="primary" content="2" :inline="true" />
          </v-list-item-action>
        </template>
      </v-list-item>

      <!-- logout -->
      <v-list-item>
        <v-btn
          :block="true"
          class="mt-1"
          color="secondary"
          height="36"
          @click="logoutUser()"
        >
          Logout
        </v-btn>
      </v-list-item>
    </v-list>
  </v-menu>
</template>
