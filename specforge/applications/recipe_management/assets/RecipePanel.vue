<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useDisplay } from "vuetify";
import { IconSearch, IconReload, IconPlus, IconX } from "@tabler/icons-vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import { setBackendErrors } from "@/utils/errorApply";
import request from "@/plugins/axios";
import { useFileUpload } from "@/composables/useFileUpload";
const { uploading, uploadFiles } = useFileUpload();
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
const { xs } = useDisplay();
const form = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null);
const fieldErrors = ref<Record<string, string>>({});
const deleting = ref<Recipe | null>(null);
const required = (value: unknown) =>
  !!String(value ?? "").trim() || "请填写此项";
const length = (max: number) => (value: unknown) =>
  String(value ?? "").length <= max || `最多 ${max} 个字符`;
const integer = (min: number, max: number) => (value: unknown) =>
  (value !== "" &&
    value !== null &&
    Number.isInteger(Number(value)) &&
    Number(value) >= min &&
    Number(value) <= max) ||
  `请输入 ${min}–${max} 的整数`;
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
  fieldErrors.value = {};
  editing.value = true;
}
function closeEditor() {
  if (busy.value || uploading.value) return;
  editing.value = false;
  error.value = "";
  fieldErrors.value = {};
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
    fieldErrors.value = {};
    editing.value = true;
  } catch (e) {
    error.value = (e as Error).message;
  }
}
async function uploadCover(value: File | File[] | null) {
  if (busy.value || uploading.value) return;
  error.value = "";
  try {
    await uploadFiles(value, {
      maxFiles: 1, existingCount: 0, maxBytes: 5 * 1024 * 1024,
      acceptedTypes: ["image/png", "image/jpeg"],
      upload: async (file) => {
        const form = new FormData(); form.append("file", file);
        return (await request.post<FormData, { url: string }>("/v1/recipes/cover", form)).data;
      },
      onUploaded: (result) => { draft.value.cover_url = result.url; },
    });
  } catch (e) {
    error.value = (e as Error).message || "封面上传失败";
  }
}

async function save() {
  if (uploading.value || busy.value) return;
  fieldErrors.value = {};
  if (!(await form.value?.validate())?.valid) {
    error.value = "请检查标红字段后再保存";
    return;
  }
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
    setBackendErrors<Record<string, unknown>>(
      e as Parameters<typeof setBackendErrors>[0],
      (field, message) => {
        fieldErrors.value[String(field)] = Array.isArray(message)
          ? message.join("，")
          : String(message || "");
      },
    );
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
  if (busy.value) return;
  busy.value = true;
  try {
    await request.delete("/v1/recipes/" + row.id, { revision: row.revision });
    deleting.value = null;
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
  <v-card class="pa-4" data-testid="recipe-panel">
    <v-card-title tag="h1" class="text-subtitle-1">食谱厨房</v-card-title>
    <v-card-text>
      <v-form class="recipe-fields" @submit.prevent="search">
        <v-row align="center">
          <v-col cols="12" sm="4"
            ><v-text-field
              v-model="keyword"
              label="搜索菜名或简介"
              variant="outlined"
              density="compact"
              base-color="input-border"
              hide-details
              clearable
          /></v-col>
          <v-col cols="12" sm="4"
            ><v-select
              v-model="category"
              label="全部分类"
              :items="categories"
              item-title="name"
              item-value="id"
              variant="outlined"
              density="compact"
              base-color="input-border"
              clearable
              hide-details
          /></v-col>
          <v-col cols="12" sm="4" class="d-flex ga-2">
            <v-btn
              type="submit"
              color="primary"
              variant="tonal"
              size="small"
              height="40"
              :loading="busy"
              ><IconSearch :size="18" class="mr-1" />搜索</v-btn
            >
            <v-btn
              color="info"
              variant="tonal"
              size="small"
              height="40"
              :disabled="busy"
              @click="
                keyword = '';
                category = null;
                search();
              "
              ><IconReload :size="18" class="mr-1" />重置</v-btn
            >
          </v-col>
        </v-row>
      </v-form>
      <div class="d-flex flex-wrap align-center ga-2 my-4">
        <v-btn
          :variant="view === 'published' ? 'tonal' : 'text'"
          color="primary"
          size="small"
          height="30"
          @click="changeView('published')"
          >发现菜谱</v-btn
        >
        <v-btn
          v-if="allowed('favorite')"
          :variant="view === 'favorites' ? 'tonal' : 'text'"
          color="primary"
          size="small"
          height="30"
          @click="changeView('favorites')"
          >我的收藏</v-btn
        >
        <v-btn
          v-if="allowed('publish')"
          :variant="view === 'mine' ? 'tonal' : 'text'"
          color="primary"
          size="small"
          height="30"
          @click="changeView('mine')"
          >我的发布</v-btn
        >
        <v-btn
          v-if="allowed('review')"
          :variant="view === 'review' ? 'tonal' : 'text'"
          color="primary"
          size="small"
          height="30"
          @click="changeView('review')"
          >待审核</v-btn
        >
        <v-spacer />
        <v-btn
          v-if="allowed('publish')"
          color="secondary"
          size="small"
          height="30"
          :disabled="busy"
          @click="create"
          ><IconPlus :size="14" class="mr-1" />发布菜谱</v-btn
        >
        <v-btn
          icon
          size="x-small"
          variant="text"
          aria-label="刷新菜谱"
          :disabled="busy"
          @click="load"
          ><IconReload :size="18"
        /></v-btn>
      </div>
      <v-alert
        v-if="error && !editing && !reviewing"
        type="error"
        variant="tonal"
        class="mb-4"
        >{{ error }}</v-alert
      >
      <v-progress-linear
        v-if="busy"
        indeterminate
        color="primary"
        class="mb-4"
      />
      <v-row>
        <v-col v-for="row in rows" :key="row.id" cols="12" sm="6" lg="4">
          <v-card
            tag="article"
            height="100%"
            class="border"
            :data-testid="'recipe-' + row.id"
          >
            <v-img
              v-if="row.cover_url"
              :src="row.cover_url"
              height="170"
              cover
              alt="菜谱封面"
              referrerpolicy="no-referrer"
            />
            <div
              v-else
              class="d-flex align-center justify-center bg-background text-medium-emphasis"
              style="height: 170px"
            >
              <span class="text-body-2">暂无封面</span>
            </div>
            <v-card-text>
              <div class="d-flex flex-wrap ga-2 mb-3">
                <v-chip color="primary" size="small" variant="tonal">{{
                  row.category_name
                }}</v-chip
                ><v-chip
                  v-if="view !== 'published' && view !== 'favorites'"
                  size="small"
                  :color="
                    row.publication_state === 'REJECTED' ? 'error' : 'info'
                  "
                  variant="tonal"
                  >{{ states[row.publication_state] }}</v-chip
                >
              </div>
              <h2 class="text-subtitle-1 text-wrap">{{ row.title }}</h2>
              <p class="text-body-2 text-medium-emphasis my-3 recipe-summary">
                {{ row.summary || "暂无简介" }}
              </p>
              <p class="text-caption text-medium-emphasis">
                {{ row.author_name }} · {{ row.servings }} 人份 · 准备
                {{ row.prep_minutes }} 分钟
              </p>
              <p
                v-if="row.publication_state === 'REJECTED'"
                class="text-error text-body-2 mt-3"
              >
                驳回原因：{{ row.review_reason }}
              </p>
            </v-card-text>
            <v-card-actions class="flex-wrap ga-1 px-4 pb-4">
              <v-btn
                size="small"
                variant="text"
                color="primary"
                @click="openRecipe(row.id)"
                >查看做法</v-btn
              >
              <v-btn
                v-if="
                  allowed('favorite') && row.publication_state === 'PUBLISHED'
                "
                size="small"
                variant="text"
                color="secondary"
                :disabled="busy"
                @click="toggleFavorite(row)"
                >{{ row.favorite ? "取消收藏" : "收藏" }}</v-btn
              >
              <template v-if="row.mine && allowed('publish')">
                <v-btn
                  v-if="row.publication_state !== 'PENDING'"
                  size="small"
                  variant="text"
                  color="warning"
                  :disabled="busy"
                  @click="edit(row)"
                  >编辑</v-btn
                >
                <v-btn
                  v-if="['DRAFT', 'REJECTED'].includes(row.publication_state)"
                  size="small"
                  variant="tonal"
                  color="secondary"
                  :disabled="busy"
                  @click="transition(row, 'submit')"
                  >提交审核</v-btn
                >
                <v-btn
                  v-if="row.publication_state !== 'PENDING'"
                  size="small"
                  variant="text"
                  color="error"
                  :disabled="busy"
                  @click="deleting = row"
                  >删除</v-btn
                >
              </template>
              <template
                v-if="
                  allowed('review') &&
                  !row.mine &&
                  row.publication_state === 'PENDING'
                "
              >
                <v-btn
                  size="small"
                  color="success"
                  variant="tonal"
                  :disabled="busy"
                  @click="transition(row, 'approve')"
                  >通过</v-btn
                >
                <v-btn
                  size="small"
                  color="error"
                  variant="text"
                  :disabled="busy"
                  @click="
                    reviewing = row;
                    reviewReason = '';
                    error = '';
                  "
                  >驳回</v-btn
                >
              </template>
              <span
                v-if="
                  allowed('review') &&
                  row.mine &&
                  row.publication_state === 'PENDING'
                "
                class="text-caption"
                >自己的菜谱需由其他管理员审核</span
              >
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <div
        v-if="!rows.length && !busy"
        class="text-center text-medium-emphasis py-12"
      >
        {{
          keyword || category
            ? "没有符合条件的菜谱，请调整搜索条件。"
            : view === "favorites"
              ? "暂无收藏，可到发现菜谱中收藏喜欢的菜谱。"
              : view === "review"
                ? "暂无待审核菜谱。"
                : view === "mine"
                  ? "暂无发布记录，可点击发布菜谱创建草稿。"
                  : "暂无已发布菜谱。"
        }}
      </div>
      <v-pagination
        v-model="page"
        :length="Math.max(1, Math.ceil(total / 12))"
        density="compact"
        class="mt-4"
        @update:model-value="load"
      />
    </v-card-text>
    <v-dialog
      v-model="editing"
      max-width="800"
      :fullscreen="xs"
      persistent
      scrollable
    >
      <v-card>
        <v-toolbar color="secondary" density="compact"
          ><v-toolbar-title class="text-subtitle-1">{{
            editId ? "编辑菜谱" : "发布菜谱"
          }}</v-toolbar-title
          ><template #append
            ><v-btn
              icon
              size="x-small"
              class="mr-4"
              aria-label="关闭编辑"
              :disabled="busy || uploading"
              @click="closeEditor"
              ><IconX :size="16" /></v-btn></template
        ></v-toolbar>
        <v-card-text>
          <v-container>
            <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{
              error
            }}</v-alert>
            <v-alert type="info" variant="tonal" class="mb-6"
              >保存后为草稿。提交审核通过后公开；修改已发布菜谱会先撤回展示，需重新审核。</v-alert
            >
            <v-form
              id="recipe-form"
              class="recipe-fields"
              ref="form"
              validate-on="blur"
              @submit.prevent="save"
            >
              <v-row>
                <v-col cols="12" sm="6" class="py-0"
                  ><v-text-field
                    v-model="draft.title"
                    label="菜名"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    maxlength="80"
                    :rules="[required, length(80)]"
                    :error-messages="fieldErrors.title"
                /></v-col>
                <v-col cols="12" sm="6" class="py-0"
                  ><v-select
                    v-model="draft.category_id"
                    label="分类"
                    :items="categories"
                    item-title="name"
                    item-value="id"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    :rules="[required]"
                    :error-messages="fieldErrors.category_id"
                /></v-col>
                <v-col cols="12" class="py-0"
                  ><v-textarea
                    v-model="draft.summary"
                    label="简介"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    maxlength="255"
                    rows="2"
                    :rules="[length(255)]"
                    :error-messages="fieldErrors.summary"
                /></v-col>
                <v-col cols="12" sm="6" class="py-0"
                  ><v-text-field
                    v-model.number="draft.servings"
                    label="份数"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    type="number"
                    min="1"
                    max="100"
                    :rules="[integer(1, 100)]"
                    :error-messages="fieldErrors.servings"
                /></v-col>
                <v-col cols="12" sm="6" class="py-0"
                  ><v-text-field
                    v-model.number="draft.prep_minutes"
                    label="准备时间（分钟）"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    type="number"
                    min="0"
                    max="1440"
                    :rules="[integer(0, 1440)]"
                    :error-messages="fieldErrors.prep_minutes"
                /></v-col>
                <v-col cols="12" class="py-0"
                  ><v-text-field
                    v-model="draft.cover_url"
                    label="封面图片地址（可选）"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    maxlength="255"
                    :rules="[length(255)]"
                    :error-messages="fieldErrors.cover_url"
                /></v-col>
                <v-col cols="12" class="py-0"
                  ><v-file-input
                    aria-label="上传封面"
                    label="上传封面"
                    accept="image/png,image/jpeg"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    hint="PNG/JPEG，最多 5MB"
                    persistent-hint
                    :disabled="busy || uploading"
                    :loading="uploading"
                    @update:model-value="uploadCover"
                /></v-col>
                <v-col v-if="draft.cover_url" cols="12"
                  ><v-img
                    :src="draft.cover_url"
                    data-testid="cover-preview"
                    height="160"
                    alt="封面预览"
                    referrerpolicy="no-referrer"
                  /><v-btn
                    color="error"
                    variant="text"
                    size="small"
                    :disabled="uploading"
                    @click="draft.cover_url = ''"
                    >移除封面</v-btn
                  ></v-col
                >
              </v-row>
              <h3 class="text-subtitle-1 mt-6 mb-4">食材清单</h3>
              <v-row
                v-for="(item, index) in draft.ingredients"
                :key="index"
                align="start"
              >
                <v-col cols="12" sm="5" class="py-0"
                  ><v-text-field
                    v-model="item.name"
                    :label="'食材名称 ' + (index + 1)"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    maxlength="80"
                    :rules="[required, length(80)]"
                    :error-messages="
                      fieldErrors['ingredients[' + index + '].name']
                    "
                /></v-col>
                <v-col cols="12" sm="5" class="py-0"
                  ><v-text-field
                    v-model="item.amount"
                    :label="'食材用量 ' + (index + 1)"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    maxlength="80"
                    :rules="[required, length(80)]"
                    :error-messages="
                      fieldErrors['ingredients[' + index + '].amount']
                    "
                /></v-col>
                <v-col cols="12" sm="2" class="pt-0 pb-4"
                  ><v-btn
                    size="small"
                    variant="text"
                    color="error"
                    height="36"
                    :disabled="draft.ingredients.length === 1"
                    @click="draft.ingredients.splice(index, 1)"
                    >移除食材</v-btn
                  ></v-col
                >
              </v-row>
              <v-btn
                color="secondary"
                variant="tonal"
                size="small"
                height="30"
                :disabled="draft.ingredients.length >= 40"
                @click="draft.ingredients.push({ name: '', amount: '' })"
                ><IconPlus :size="14" class="mr-1" />添加食材</v-btn
              >
              <h3 class="text-subtitle-1 mt-6 mb-4">烹饪步骤</h3>
              <v-row
                v-for="(_, index) in draft.steps"
                :key="index"
                align="start"
              >
                <v-col cols="12" sm="10" class="py-0"
                  ><v-textarea
                    v-model="draft.steps[index]"
                    :label="'步骤 ' + (index + 1)"
                    variant="outlined"
                    density="comfortable"
                    base-color="input-border"
                    maxlength="255"
                    rows="2"
                    :rules="[required, length(255)]"
                    :error-messages="fieldErrors['steps[' + index + ']']"
                /></v-col>
                <v-col cols="12" sm="2" class="pt-0 pb-4"
                  ><v-btn
                    size="small"
                    variant="text"
                    color="error"
                    height="36"
                    :disabled="draft.steps.length === 1"
                    @click="draft.steps.splice(index, 1)"
                    >移除步骤</v-btn
                  ></v-col
                >
              </v-row>
              <v-btn
                color="secondary"
                variant="tonal"
                size="small"
                height="30"
                :disabled="draft.steps.length >= 40"
                @click="draft.steps.push('')"
                ><IconPlus :size="14" class="mr-1" />添加步骤</v-btn
              >
            </v-form>
          </v-container>
        </v-card-text>
        <v-card-actions class="px-6 py-4"
          ><v-spacer /><v-btn
            variant="tonal"
            size="small"
            height="36"
            width="80"
            :disabled="busy || uploading"
            @click="closeEditor"
            >取消</v-btn
          ><v-btn
            type="submit"
            form="recipe-form"
            color="secondary"
            variant="flat"
            size="small"
            height="36"
            :loading="busy || uploading"
            >保存草稿</v-btn
          ></v-card-actions
        >
      </v-card>
    </v-dialog>
    <v-dialog
      :model-value="detail !== null"
      max-width="800"
      :fullscreen="xs"
      scrollable
      @update:model-value="detail = null"
    >
      <v-card v-if="detail">
        <v-toolbar color="secondary" density="compact"
          ><v-toolbar-title class="text-subtitle-1">{{
            detail.title
          }}</v-toolbar-title
          ><template #append
            ><v-btn
              icon
              size="x-small"
              class="mr-4"
              aria-label="关闭详情"
              @click="detail = null"
              ><IconX :size="16" /></v-btn></template
        ></v-toolbar>
        <v-card-text class="pa-6">
          <v-img
            v-if="detail.cover_url"
            :src="detail.cover_url"
            height="200"
            alt="菜谱封面"
            class="mb-4"
            referrerpolicy="no-referrer"
          />
          <p class="text-body-2 recipe-summary">{{ detail.summary }}</p>
          <p class="text-caption text-medium-emphasis my-4">
            {{ detail.servings }} 人份 · 准备 {{ detail.prep_minutes }} 分钟
          </p>
          <h3 class="text-subtitle-1">食材</h3>
          <ul class="recipe-detail-list text-body-2">
            <li v-for="(item, index) in detail.ingredients" :key="index">
              {{ item.name }} — {{ item.amount }}
            </li>
          </ul>
          <h3 class="text-subtitle-1">做法</h3>
          <ol class="recipe-detail-list text-body-2">
            <li v-for="(step, index) in detail.steps" :key="index">
              {{ step }}
            </li>
          </ol>
        </v-card-text>
        <v-card-actions class="px-6 py-4"
          ><v-spacer /><v-btn
            variant="tonal"
            size="small"
            height="36"
            width="80"
            @click="detail = null"
            >关闭</v-btn
          ></v-card-actions
        >
      </v-card>
    </v-dialog>
    <v-dialog
      :model-value="reviewing !== null"
      max-width="500"
      :fullscreen="xs"
      @update:model-value="reviewing = null"
    >
      <v-card
        ><v-toolbar color="secondary" density="compact"
          ><v-toolbar-title class="text-subtitle-1">驳回菜谱</v-toolbar-title
          ><template #append
            ><v-btn
              icon
              size="x-small"
              class="mr-4"
              aria-label="关闭审核"
              :disabled="busy"
              @click="reviewing = null"
              ><IconX :size="16" /></v-btn></template
        ></v-toolbar>
        <v-card-text class="pa-6"
          ><v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{
            error
          }}</v-alert
          ><v-textarea
            v-model="reviewReason"
            label="驳回原因"
            variant="outlined"
            density="comfortable"
            base-color="input-border"
            maxlength="255"
            :rules="[required, length(255)]"
        /></v-card-text>
        <v-card-actions class="px-6 py-4"
          ><v-spacer /><v-btn
            variant="tonal"
            size="small"
            height="36"
            width="80"
            :disabled="busy"
            @click="reviewing = null"
            >取消</v-btn
          ><v-btn
            color="error"
            variant="flat"
            size="small"
            height="36"
            :disabled="!reviewReason.trim() || busy"
            :loading="busy"
            @click="reviewing && transition(reviewing, 'reject', reviewReason)"
            >确认驳回</v-btn
          ></v-card-actions
        >
      </v-card>
    </v-dialog>
    <ConfirmDialog
      :model-value="deleting !== null"
      title="删除菜谱"
      message="删除菜谱后将不再公开展示，确定删除？"
      confirm-button-text="确认删除"
      cancel-button-text="取消"
      @update:model-value="deleting = null"
      @confirm="deleting && remove(deleting)"
    />
  </v-card>
</template>
<style scoped>
.recipe-summary {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.recipe-detail-list {
  padding-left: 24px;
  margin: 16px 0 24px;
  line-height: 2;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
/* Border tokens are deliberately muted; idle labels still need readable text contrast. */
.recipe-fields
  :deep(.v-field:not(.v-field--error):not(.v-field--focused) .v-field-label) {
  color: rgb(var(--v-theme-on-surface));
}
</style>
