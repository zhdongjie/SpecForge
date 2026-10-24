<script setup lang="ts">
import { ref, onMounted } from "vue";
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
async function load() {
  try {
    data.value = (
      await request.get<unknown, Stats>("/v1/recipes/statistics")
    ).data;
  } catch (e) {
    error.value = (e as Error).message;
  }
}
onMounted(load);
</script>
<template>
  <main class="stats">
    <div class="stats-heading">
      <div>
        <h1>食谱统计</h1>
        <p>查看内容发布与收藏概况</p>
      </div>
      <v-btn @click="load">刷新统计</v-btn>
    </div>
    <v-alert v-if="error" type="error">{{ error }}</v-alert
    ><template v-if="data"
      ><div class="stats-grid">
        <v-card
          v-for="item in [
            { label: '用户数', value: data.users },
            { label: '已发布菜谱', value: data.published },
            { label: '待审核菜谱', value: data.pending },
            { label: '有效收藏', value: data.favorites },
          ]"
          :key="item.label"
          :title="item.label"
          ><v-card-text class="stats-value">{{
            item.value
          }}</v-card-text></v-card
        >
      </div>
      <v-card title="已发布菜谱分类分布" class="mt-6"
        ><v-card-text
          ><div
            v-for="item in data.categories"
            :key="item.name"
            class="stats-row"
          >
            <span>{{ item.name }}</span
            ><v-progress-linear
              :model-value="
                data.published
                  ? (Number(item.count) / Number(data.published)) * 100
                  : 0
              "
              height="10"
              rounded
              color="primary"
            /><strong>{{ item.count }}</strong>
          </div></v-card-text
        ></v-card
      ></template
    >
  </main>
</template>
<style scoped>
.stats {
  max-width: 1100px;
  margin: 20px auto;
  padding: 8px;
}
.stats-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}
.stats-heading p {
  opacity: 0.6;
  margin-top: 8px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}
.stats-value {
  font-size: 36px;
  font-weight: 600;
}
.stats-row {
  display: grid;
  grid-template-columns: 80px 1fr 40px;
  gap: 20px;
  align-items: center;
  margin: 20px 0;
}
@media (max-width: 700px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
