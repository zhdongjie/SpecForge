<script setup lang="ts">
import { ref, onMounted } from "vue";
import { IconReload } from "@tabler/icons-vue";
import request from "@/plugins/axios";
type Stats = {
  users: number;
  published: number;
  pending: number;
  favorites: number;
  categories: { name: string; count: number }[];
};
const data = ref<Stats | null>(null),
  error = ref("");
const busy = ref(false);
async function load() {
  busy.value = true;
  error.value = "";
  try {
    data.value = (
      await request.get<unknown, Stats>("/v1/recipes/statistics")
    ).data;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
onMounted(load);
</script>
<template>
  <v-card class="pa-4">
    <v-card-title class="d-flex align-center"
      ><h1 class="text-subtitle-1">食谱统计</h1>
      <v-spacer /><v-btn
        color="primary"
        variant="tonal"
        size="small"
        height="30"
        :loading="busy"
        @click="load"
        ><IconReload :size="18" class="mr-1" />刷新统计</v-btn
      ></v-card-title
    >
    <v-card-text>
      <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{
        error
      }}</v-alert>
      <v-progress-linear
        v-if="busy"
        color="primary"
        indeterminate
        class="mb-4"
      />
      <template v-if="data">
        <v-row
          ><v-col
            v-for="item in [
              { label: '用户数', value: data.users },
              { label: '已发布菜谱', value: data.published },
              { label: '待审核菜谱', value: data.pending },
              { label: '有效收藏', value: data.favorites },
            ]"
            :key="item.label"
            cols="12"
            sm="6"
            lg="3"
            ><v-card class="border"
              ><v-card-text
                ><p class="text-body-2 text-medium-emphasis mb-3">
                  {{ item.label }}
                </p>
                <p class="text-h4">{{ item.value }}</p></v-card-text
              ></v-card
            ></v-col
          ></v-row
        >
        <h2 class="text-subtitle-1 mt-6 mb-4">已发布菜谱分类分布</h2>
        <v-row
          v-for="item in data.categories"
          :key="item.name"
          align="center"
          class="mb-2"
          ><v-col cols="4" sm="2" class="text-body-2">{{ item.name }}</v-col
          ><v-col cols="6" sm="9"
            ><v-progress-linear
              :model-value="
                data.published
                  ? (Number(item.count) / Number(data.published)) * 100
                  : 0
              "
              height="8"
              rounded
              color="primary" /></v-col
          ><v-col cols="2" sm="1" class="text-body-2 text-right">{{
            item.count
          }}</v-col></v-row
        >
        <p
          v-if="!data.categories.length"
          class="text-center text-medium-emphasis py-8"
        >
          暂无已发布菜谱分类数据。
        </p>
      </template>
    </v-card-text>
  </v-card>
</template>
