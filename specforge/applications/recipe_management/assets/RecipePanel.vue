<script setup lang="ts">
import { ref, onMounted } from "vue";
import request from "@/plugins/axios";
import { useAuthorities } from "@/composables/useAuthorities";
type Ingredient = { name: string; amount: string };
type Recipe = {
  id: string;
  title: string;
  summary: string;
  category_id: string;
  category_name?: string;
  author_name?: string;
  publication_state: string;
  review_reason?: string;
  revision: number;
  servings: number;
  prep_minutes: number;
  cover_url: string;
  mine: boolean;
  favorite: boolean;
  ingredients: Ingredient[];
  steps: string[];
};
type Category = { id: string; name: string };
const { can } = useAuthorities();
const allowed = (action: string) => can("business:recipes:" + action);
const view = ref("published"),
  keyword = ref(""),
  category = ref<string | null>(null),
  page = ref(1),
  total = ref(0);
const rows = ref<Recipe[]>([]),
  categories = ref<Category[]>([]),
  busy = ref(false),
  error = ref("");
const editing = ref(false),
  detail = ref<Recipe | null>(null),
  reviewing = ref<Recipe | null>(null),
  reviewReason = ref("");
const states: Record<string, string> = {
  DRAFT: "草稿",
  PENDING: "待审核",
  PUBLISHED: "已发布",
  REJECTED: "已驳回",
};
const blank = () => ({
  title: "",
  summary: "",
  category_id: "",
  servings: 1,
  prep_minutes: 0,
  cover_url: "",
  ingredients: [{ name: "", amount: "" }],
  steps: [""],
});
const draft = ref(blank()),
  editId = ref<string | null>(null),
  editRevision = ref<number | null>(null);
async function load() {
  busy.value = true;
  error.value = "";
  try {
    const response = await request.get<
      unknown,
      { items: Recipe[]; total: number }
    >("/v1/recipes/page", {
      view: view.value,
      keyword: keyword.value,
      categoryId: category.value || undefined,
      currentPage: page.value,
      pageSize: 12,
    });
    rows.value = response.data.items;
    total.value = Number(response.data.total);
  } catch (e) {
    error.value = (e as Error).message || "加载失败";
  } finally {
    busy.value = false;
  }
}
async function changeView(value: string) {
  view.value = value;
  page.value = 1;
  await load();
}
async function search() {
  page.value = 1;
  await load();
}
async function openRecipe(id: string) {
  try {
    detail.value = (
      await request.get<unknown, Recipe>("/v1/recipes/" + id)
    ).data;
  } catch (e) {
    error.value = (e as Error).message;
  }
}
function create() {
  draft.value = blank();
  draft.value.category_id = categories.value[0]?.id || "";
  editId.value = null;
  editRevision.value = null;
  error.value = "";
  editing.value = true;
}
async function edit(row: Recipe) {
  try {
    const value = (await request.get<unknown, Recipe>("/v1/recipes/" + row.id))
      .data;
    draft.value = {
      title: value.title,
      summary: value.summary || "",
      category_id: value.category_id,
      servings: value.servings,
      prep_minutes: value.prep_minutes,
      cover_url: value.cover_url || "",
      ingredients: value.ingredients.map((i) => ({ ...i })),
      steps: [...value.steps],
    };
    editId.value = value.id;
    editRevision.value = value.revision;
    error.value = "";
    editing.value = true;
  } catch (e) {
    error.value = (e as Error).message;
  }
}
async function save() {
  busy.value = true;
  error.value = "";
  try {
    if (editId.value)
      await request.put("/v1/recipes/" + editId.value, {
        ...draft.value,
        revision: editRevision.value,
      });
    else await request.post("/v1/recipes", draft.value);
    editing.value = false;
    await changeView("mine");
  } catch (e) {
    error.value = (e as Error).message || "保存失败";
  } finally {
    busy.value = false;
  }
}
async function transition(row: Recipe, action: string, reason?: string) {
  busy.value = true;
  error.value = "";
  try {
    await request.post("/v1/recipes/" + row.id + "/actions/" + action, {
      revision: row.revision,
      ...(reason ? { reason } : {}),
    });
    reviewing.value = null;
    detail.value = null;
    await load();
  } catch (e) {
    error.value = (e as Error).message || "操作失败";
  } finally {
    busy.value = false;
  }
}
async function toggleFavorite(row: Recipe) {
  busy.value = true;
  try {
    if (row.favorite)
      await request.delete("/v1/recipes/" + row.id + "/favorite");
    else await request.post("/v1/recipes/" + row.id + "/favorite");
    if (detail.value?.id === row.id) detail.value.favorite = !row.favorite;
    await load();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
async function remove(row: Recipe) {
  if (!window.confirm("删除菜谱后将不再公开展示，确定删除？")) return;
  busy.value = true;
  try {
    await request.delete("/v1/recipes/" + row.id, { revision: row.revision });
    await load();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
onMounted(async () => {
  try {
    categories.value = (
      await request.get<unknown, Category[]>("/v1/recipes/categories")
    ).data;
    await load();
  } catch (e) {
    error.value = (e as Error).message;
  }
});
</script>
<template>
  <main class="recipe-shell">
    <header class="recipe-header">
      <div>
        <div class="recipe-eyebrow">把日常，做成好味道</div>
        <h1>食谱厨房</h1>
        <p>发现喜欢的菜谱，记录自己的拿手好菜。</p>
      </div>
      <v-btn
        v-if="allowed('publish')"
        color="primary"
        size="large"
        :disabled="busy"
        @click="create"
        >发布菜谱</v-btn
      >
    </header>
    <nav class="recipe-tabs">
      <v-btn
        :variant="view === 'published' ? 'tonal' : 'text'"
        @click="changeView('published')"
        >发现菜谱</v-btn
      ><v-btn
        v-if="allowed('favorite')"
        :variant="view === 'favorites' ? 'tonal' : 'text'"
        @click="changeView('favorites')"
        >我的收藏</v-btn
      ><v-btn
        v-if="allowed('publish')"
        :variant="view === 'mine' ? 'tonal' : 'text'"
        @click="changeView('mine')"
        >我的发布</v-btn
      ><v-btn
        v-if="allowed('review')"
        :variant="view === 'review' ? 'tonal' : 'text'"
        @click="changeView('review')"
        >待审核</v-btn
      >
    </nav>
    <div class="recipe-search">
      <v-text-field
        v-model="keyword"
        label="搜索菜名或简介"
        hide-details
        clearable
        @keyup.enter="search"
      /><v-select
        v-model="category"
        label="全部分类"
        :items="categories"
        item-title="name"
        item-value="id"
        clearable
        hide-details
      /><v-btn :loading="busy" @click="search">搜索</v-btn>
    </div>
    <v-alert v-if="error && !editing && !reviewing" type="error" class="mb-4">{{
      error
    }}</v-alert>
    <v-progress-linear v-if="busy" indeterminate />
    <div class="recipe-grid">
      <article
        v-for="row in rows"
        :key="row.id"
        class="recipe-card"
        :data-testid="'recipe-' + row.id"
      >
        <div class="recipe-cover">
          <img
            v-if="row.cover_url"
            :src="row.cover_url"
            alt="菜谱封面"
            loading="lazy"
            referrerpolicy="no-referrer"
          />
          <div v-else class="recipe-cover-empty">
            <span>好味道，从这里开始</span>
          </div>
          <v-chip class="recipe-category" size="small">{{
            row.category_name
          }}</v-chip>
        </div>
        <div class="recipe-card-body">
          <div class="recipe-card-title">
            <h2>{{ row.title }}</h2>
            <v-chip
              v-if="view !== 'published' && view !== 'favorites'"
              size="small"
              >{{ states[row.publication_state] }}</v-chip
            >
          </div>
          <p class="recipe-summary">
            {{ row.summary || "简单食材，也能做出好味道。" }}
          </p>
          <div class="recipe-meta">
            {{ row.author_name }} · {{ row.servings }} 人份 · 准备
            {{ row.prep_minutes }} 分钟
          </div>
          <p
            v-if="row.publication_state === 'REJECTED'"
            class="recipe-rejection"
          >
            驳回原因：{{ row.review_reason }}
          </p>
          <div class="recipe-actions">
            <v-btn size="small" variant="text" @click="openRecipe(row.id)"
              >查看做法</v-btn
            ><v-btn
              v-if="
                allowed('favorite') && row.publication_state === 'PUBLISHED'
              "
              size="small"
              variant="text"
              :disabled="busy"
              @click="toggleFavorite(row)"
              >{{ row.favorite ? "取消收藏" : "收藏" }}</v-btn
            ><template v-if="row.mine && allowed('publish')"
              ><v-btn
                v-if="row.publication_state !== 'PENDING'"
                size="small"
                :disabled="busy"
                @click="edit(row)"
                >编辑</v-btn
              ><v-btn
                v-if="['DRAFT', 'REJECTED'].includes(row.publication_state)"
                size="small"
                :disabled="busy"
                @click="transition(row, 'submit')"
                >提交审核</v-btn
              ><v-btn
                v-if="row.publication_state !== 'PENDING'"
                size="small"
                variant="text"
                :disabled="busy"
                @click="remove(row)"
                >删除</v-btn
              ></template
            ><template
              v-if="
                allowed('review') &&
                !row.mine &&
                row.publication_state === 'PENDING'
              "
              ><v-btn
                size="small"
                color="primary"
                :disabled="busy"
                @click="transition(row, 'approve')"
                >通过</v-btn
              ><v-btn
                size="small"
                :disabled="busy"
                @click="
                  reviewing = row;
                  reviewReason = '';
                  error = '';
                "
                >驳回</v-btn
              ></template
            ><span
              v-if="
                allowed('review') &&
                row.mine &&
                row.publication_state === 'PENDING'
              "
              class="text-caption"
              >自己的菜谱需由其他管理员审核</span
            >
          </div>
        </div>
      </article>
    </div>
    <div v-if="!rows.length && !busy" class="recipe-empty">
      这里还没有菜谱，换个条件试试，或记录第一道好菜。
    </div>
    <v-pagination
      v-model="page"
      :length="Math.max(1, Math.ceil(total / 12))"
      @update:model-value="load"
    />
    <v-dialog v-model="editing" max-width="860" persistent
      ><v-card :title="editId ? '编辑菜谱' : '发布菜谱'"
        ><v-card-text
          ><v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert
          ><v-alert type="info" variant="tonal" class="mb-4"
            >保存后为草稿。提交审核通过后公开；修改已发布菜谱会先撤回展示，需重新审核。</v-alert
          ><v-text-field
            v-model="draft.title"
            label="菜名"
            maxlength="80"
          /><v-textarea
            v-model="draft.summary"
            label="简介"
            maxlength="255"
            rows="2"
          /><v-select
            v-model="draft.category_id"
            label="分类"
            :items="categories"
            item-title="name"
            item-value="id"
          />
          <div class="recipe-two">
            <v-text-field
              v-model.number="draft.servings"
              label="份数"
              type="number"
              min="1"
              max="100"
            /><v-text-field
              v-model.number="draft.prep_minutes"
              label="准备时间（分钟）"
              type="number"
              min="0"
              max="1440"
            />
          </div>
          <v-text-field
            v-model="draft.cover_url"
            label="封面图片地址（可选，HTTPS）"
            maxlength="255"
          />
          <h3>食材清单</h3>
          <div
            v-for="(item, index) in draft.ingredients"
            :key="index"
            class="recipe-ingredient"
          >
            <v-text-field
              v-model="item.name"
              :label="'食材名称 ' + (index + 1)"
              maxlength="80"
            /><v-text-field
              v-model="item.amount"
              :label="'食材用量 ' + (index + 1)"
              maxlength="80"
            /><v-btn
              :disabled="draft.ingredients.length === 1"
              @click="draft.ingredients.splice(index, 1)"
              >移除食材</v-btn
            >
          </div>
          <v-btn
            :disabled="draft.ingredients.length >= 40"
            @click="draft.ingredients.push({ name: '', amount: '' })"
            >添加食材</v-btn
          >
          <h3 class="mt-5">烹饪步骤</h3>
          <div
            v-for="(_, index) in draft.steps"
            :key="index"
            class="recipe-step"
          >
            <v-textarea
              v-model="draft.steps[index]"
              :label="'步骤 ' + (index + 1)"
              maxlength="255"
              rows="2"
            /><v-btn
              :disabled="draft.steps.length === 1"
              @click="draft.steps.splice(index, 1)"
              >移除步骤</v-btn
            >
          </div>
          <v-btn
            :disabled="draft.steps.length >= 40"
            @click="draft.steps.push('')"
            >添加步骤</v-btn
          ></v-card-text
        ><v-card-actions
          ><v-spacer /><v-btn :disabled="busy" @click="editing = false"
            >取消</v-btn
          ><v-btn color="primary" :loading="busy" @click="save"
            >保存草稿</v-btn
          ></v-card-actions
        ></v-card
      ></v-dialog
    >
    <v-dialog
      :model-value="detail !== null"
      max-width="800"
      @update:model-value="detail = null"
      ><v-card v-if="detail" :title="detail.title"
        ><v-card-text
          ><p>{{ detail.summary }}</p>
          <p class="my-3">
            {{ detail.servings }} 人份 · 准备 {{ detail.prep_minutes }} 分钟
          </p>
          <h3>食材</h3>
          <ul class="recipe-detail-list">
            <li v-for="(item, index) in detail.ingredients" :key="index">
              {{ item.name }} — {{ item.amount }}
            </li>
          </ul>
          <h3>做法</h3>
          <ol class="recipe-detail-list">
            <li v-for="(step, index) in detail.steps" :key="index">
              {{ step }}
            </li>
          </ol></v-card-text
        ><v-card-actions
          ><v-spacer /><v-btn @click="detail = null"
            >关闭</v-btn
          ></v-card-actions
        ></v-card
      ></v-dialog
    >
    <v-dialog
      :model-value="reviewing !== null"
      max-width="500"
      @update:model-value="reviewing = null"
      ><v-card title="驳回菜谱"
        ><v-card-text
          ><v-alert v-if="error" type="error">{{ error }}</v-alert
          ><v-textarea
            v-model="reviewReason"
            label="驳回原因"
            maxlength="255" /></v-card-text
        ><v-card-actions
          ><v-btn @click="reviewing = null">取消</v-btn
          ><v-btn
            :disabled="!reviewReason.trim() || busy"
            @click="reviewing && transition(reviewing, 'reject', reviewReason)"
            >确认驳回</v-btn
          ></v-card-actions
        ></v-card
      ></v-dialog
    >
  </main>
</template>
<style scoped>
.recipe-shell {
  max-width: 1280px;
  margin: 0 auto;
  padding: 12px 8px 32px;
}
.recipe-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin: 10px 0 28px;
}
.recipe-eyebrow {
  font-size: 12px;
  letter-spacing: 3px;
  color: #bf7454;
  margin-bottom: 10px;
}
.recipe-header h1 {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 2px;
}
.recipe-header p {
  opacity: 0.65;
  margin-top: 8px;
}
.recipe-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.recipe-search {
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
}
.recipe-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px;
}
.recipe-card {
  border: 1px solid rgba(150, 140, 120, 0.18);
  border-radius: 16px;
  overflow: hidden;
  background: rgba(150, 140, 120, 0.035);
}
.recipe-cover {
  height: 170px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(120deg, #ede4d4, #d9e5d6);
}
.recipe-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.recipe-cover-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #61745a;
  font-size: 15px;
  letter-spacing: 2px;
}
.recipe-category {
  position: absolute;
  bottom: 12px;
  left: 14px;
  background: #fff !important;
  color: #374237 !important;
}
.recipe-card-body {
  padding: 20px;
}
.recipe-card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.recipe-card h2 {
  font-size: 20px;
}
.recipe-summary {
  opacity: 0.7;
  line-height: 1.7;
  margin: 10px 0;
  min-height: 54px;
  overflow-wrap: anywhere;
}
.recipe-meta {
  font-size: 12px;
  opacity: 0.6;
}
.recipe-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 16px;
}
.recipe-empty {
  text-align: center;
  padding: 64px 16px;
  opacity: 0.6;
}
.recipe-two,
.recipe-ingredient {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.recipe-ingredient {
  grid-template-columns: 1fr 1fr auto;
  margin-top: 12px;
}
.recipe-step {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}
.recipe-step > :first-child {
  flex: 1;
}
.recipe-detail-list {
  padding-left: 24px;
  margin: 12px 0 24px;
  line-height: 2;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.recipe-rejection {
  color: #c47055;
  font-size: 13px;
  margin-top: 10px;
}
@media (max-width: 1000px) {
  .recipe-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 650px) {
  .recipe-grid {
    grid-template-columns: 1fr;
  }
  .recipe-header {
    align-items: flex-start;
    flex-direction: column;
  }
  .recipe-search {
    grid-template-columns: 1fr;
  }
  .recipe-ingredient,
  .recipe-two {
    grid-template-columns: 1fr;
  }
}
</style>
