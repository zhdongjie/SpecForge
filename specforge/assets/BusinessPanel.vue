<script setup lang="ts">
import { ref, computed } from "vue";
import { useDisplay } from "vuetify";
import { IconPlus, IconReload, IconX } from "@tabler/icons-vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import { pageSizeOptions } from "@/constants/options";
import { setBackendErrors } from "@/utils/errorApply";
import request from "@/plugins/axios";
import { useAuthorities } from "@/composables/useAuthorities";
import type {
  BusinessConfig,
  BusinessRow,
  BusinessField,
} from "@/api/business/generated";
const props = defineProps<{ config: BusinessConfig }>();
const { xs } = useDisplay();
// The generic endpoint accepts at most 100; retain the matching template options.
const businessPageSizeOptions = pageSizeOptions.filter(
  (option) => Number(option.value) <= 100,
);
const pageSize = ref(20);
const editor = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(
  null,
);
const fieldErrors = ref<Record<string, string>>({});
const pending = ref<{ row: BusinessRow; name: string; label: string } | null>(
  null,
);
const actionError = ref("");
const headers = computed(() => [
  { title: "ID", key: "id", sortable: false },
  ...props.config.page.list.map((key) => ({
    title: props.config.fields.find((f) => f.name === key)?.label || key,
    key,
    sortable: false,
  })),
  ...(props.config.availability || []).map((a) => ({
    title: a.label,
    key: a.available_field,
    sortable: false,
  })),
  ...(props.config.workflow && !props.config.page.list.includes("status")
    ? [{ title: "状态", key: "status", sortable: false }]
    : []),
  { title: "操作", key: "actions", sortable: false },
]);
const editableFields = computed(() =>
  props.config.fields.filter((f) => props.config.page.form.includes(f.name)),
);
function rules(field: BusinessField) {
  return [
    (value: unknown) => {
      const empty =
        value === null ||
        value === undefined ||
        (typeof value === "string" && !value.trim());
      if (empty) return !field.required || `请填写${field.label}`;
      if (field.type === "integer") {
        if (!Number.isInteger(Number(value))) return "请输入整数";
        if (field.min !== undefined && Number(value) < field.min)
          return `不能小于 ${field.min}`;
      }
      if (field.type === "string" && String(value).length > 255)
        return "最多 255 个字符";
      return true;
    },
  ];
}
const { can } = useAuthorities();
const rows = ref<BusinessRow[]>([]),
  total = ref(0),
  page = ref(1),
  busy = ref(false),
  error = ref(""),
  dialog = ref(false);
const form = ref<Record<string, string | number | boolean | null>>({}),
  editing = ref<string | null>(null),
  details = ref<BusinessRow | null>(null);
const choices = ref<Record<string, BusinessRow[]>>({});
const additionalDetails = computed(() =>
  Object.entries(details.value || {})
    .filter(
      ([key]) =>
        key !== "id" &&
        !props.config.fields.some((f) => f.name === key) &&
        !(key === "status" && props.config.workflow),
    )
    .map(([key, value]) => ({
      key,
      value,
      label:
        props.config.availability?.find((a) => a.available_field === key)
          ?.label ||
        (
          {
            created_time: "创建时间",
            last_modified_time: "修改时间",
          } as Record<string, string>
        )[key] ||
        key,
    })),
);
const base = `/v1/business/${props.config.name}`;
const permit = (action: string) =>
  can(`business:sf_${props.config.name}:${action}`);
let loadVersion = 0;
async function load() {
  const version = ++loadVersion;
  busy.value = true;
  error.value = "";
  try {
    const { data } = await request.get<
      unknown,
      { items: BusinessRow[]; total: number }
    >(`${base}/page`, { currentPage: page.value, pageSize: pageSize.value });
    if (version !== loadVersion) return;
    rows.value = data.items;
    total.value = data.total;
  } catch (e) {
    if (version === loadVersion)
      error.value = (e as Error).message || "加载失败";
  } finally {
    if (version === loadVersion) busy.value = false;
  }
}
async function open(row?: BusinessRow) {
  editing.value = row ? String(row.id) : null;
  form.value = {};
  fieldErrors.value = {};
  error.value = "";
  for (const f of props.config.fields) {
    form.value[f.name] = (
      row
        ? row[f.name]
        : (f.default ??
          (f.type === "boolean" ? false : f.type === "foreign" ? null : ""))
    ) as string | number | boolean | null;
    if (f.type === "foreign" && f.reference !== "system_user") {
      try {
        const { data } = await request.get<unknown, { items: BusinessRow[] }>(
          `/v1/business/${f.reference}/page`,
          { currentPage: 1, pageSize: 100 },
        );
        choices.value[f.name] = data.items;
      } catch {
        choices.value[f.name] = [];
      }
    }
  }
  dialog.value = true;
}
function closeEditor() {
  if (busy.value) return;
  dialog.value = false;
  error.value = "";
  fieldErrors.value = {};
}
async function save() {
  if (busy.value) return;
  fieldErrors.value = {};
  if (!(await editor.value?.validate())?.valid) {
    error.value = "请检查标红字段后再保存";
    return;
  }
  busy.value = true;
  error.value = "";
  try {
    const body: Record<string, unknown> = {};
    for (const f of props.config.fields) {
      let v = form.value[f.name];
      if (v === "") v = null;
      if (v !== null && v !== undefined && f.type === "integer") v = Number(v);
      body[f.name] = v;
    }
    if (editing.value) await request.put(`${base}/${editing.value}`, body);
    else await request.post(base, body);
    dialog.value = false;
    await load();
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
async function action(row: BusinessRow, name: string) {
  if (busy.value) return;
  busy.value = true;
  error.value = "";
  try {
    if (name === "delete") await request.delete(`${base}/${row.id}`);
    else await request.post(`${base}/${row.id}/actions/${name}`);
    pending.value = null;
    await load();
  } catch (e) {
    actionError.value = (e as Error).message || "操作失败";
  } finally {
    busy.value = false;
  }
}
async function detail(row: BusinessRow) {
  try {
    details.value = (
      await request.get<null, BusinessRow>(`${base}/${row.id}`)
    ).data;
  } catch (e) {
    error.value = (e as Error).message;
  }
}
function confirmAction(row: BusinessRow, name: string, label: string) {
  actionError.value = "";
  pending.value = { row, name, label };
}
</script>
<template>
  <v-card class="pa-4" data-testid="business-panel">
    <v-card-title tag="h1" class="text-subtitle-1">{{
      config.label
    }}</v-card-title>
    <v-card-text>
      <v-alert
        v-if="error && !dialog"
        type="error"
        variant="tonal"
        class="mb-4"
        >{{ error }}</v-alert
      >
      <div class="d-flex flex-wrap ga-2 align-center mb-4">
        <v-btn
          v-if="permit('create')"
          color="secondary"
          size="small"
          height="30"
          :disabled="busy"
          @click="open()"
          ><IconPlus :size="14" class="mr-1" />新增{{ config.label }}</v-btn
        >
        <v-spacer /><v-btn
          variant="text"
          size="small"
          height="30"
          :disabled="busy"
          @click="load"
          ><IconReload :size="18" class="mr-1" />刷新</v-btn
        >
      </div>
      <v-data-table-server
        v-model:page="page"
        v-model:items-per-page="pageSize"
        :headers="headers"
        :items="rows"
        :items-length="Number(total)"
        :items-per-page-options="businessPageSizeOptions"
        :mobile="xs"
        :hide-default-header="xs"
        :loading="busy"
        item-value="id"
        items-per-page-text="每页数目："
        page-text="{0}-{1} 共 {2}"
        no-data-text="暂无记录"
        loading-text="正在加载…"
        @update:options="load"
      >
        <template #item.status="{ item }">{{
          config.workflow?.state_labels?.[String(item.status)] || item.status
        }}</template>
        <template
          v-for="a in config.availability || []"
          :key="a.available_field"
          #[`item.${a.available_field}`]="{ item }"
          ><span :data-testid="'availability-' + a.available_field">{{
            item[a.available_field]
          }}</span></template
        >
        <template #item.actions="{ item }">
          <div class="d-flex flex-wrap ga-1">
            <v-btn
              v-if="permit('detail')"
              size="small"
              variant="text"
              color="primary"
              :disabled="busy"
              @click="detail(item)"
              >详情</v-btn
            >
            <v-btn
              v-if="permit('update')"
              size="small"
              variant="text"
              color="warning"
              :disabled="busy"
              @click="open(item)"
              >编辑</v-btn
            >
            <v-btn
              v-if="permit('delete')"
              size="small"
              variant="text"
              color="error"
              :disabled="busy"
              @click="confirmAction(item, 'delete', '删除')"
              >删除</v-btn
            >
            <template v-for="a in config.workflow?.transitions" :key="a.name"
              ><v-btn
                v-if="permit(a.name) && item.status === a.from"
                size="small"
                variant="tonal"
                color="secondary"
                :disabled="busy"
                @click="confirmAction(item, a.name, a.label)"
                >{{ a.label }}</v-btn
              ></template
            >
          </div>
        </template>
      </v-data-table-server>
    </v-card-text>
  </v-card>
  <v-dialog
    v-model="dialog"
    max-width="800"
    :fullscreen="xs"
    persistent
    scrollable
  >
    <v-card>
      <v-toolbar color="secondary" density="compact"
        ><v-toolbar-title class="text-subtitle-1"
          >{{ editing ? "编辑" : "新增" }}{{ config.label }}</v-toolbar-title
        ><template #append
          ><v-btn
            icon
            size="x-small"
            class="mr-4"
            aria-label="关闭编辑"
            :disabled="busy"
            @click="closeEditor"
            ><IconX :size="16" /></v-btn></template
      ></v-toolbar>
      <v-card-text
        ><v-container>
          <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{
            error
          }}</v-alert>
          <v-form
            id="business-form"
            ref="editor"
            class="business-fields"
            validate-on="blur"
            @submit.prevent="save"
          >
            <v-row
              ><v-col
                v-for="f in editableFields"
                :key="f.name"
                cols="12"
                sm="6"
                class="py-0"
              >
                <v-switch
                  v-if="f.type === 'boolean'"
                  :data-testid="'field-' + f.name"
                  v-model="form[f.name]"
                  :label="f.label"
                  color="primary"
                  :error-messages="fieldErrors[f.name]"
                />
                <v-select
                  v-else-if="f.type === 'enum'"
                  :data-testid="'field-' + f.name"
                  :model-value="String(form[f.name] ?? '')"
                  @update:model-value="form[f.name] = $event"
                  :items="f.values"
                  :label="f.label"
                  variant="outlined"
                  density="comfortable"
                  base-color="input-border"
                  :rules="rules(f)"
                  :error-messages="fieldErrors[f.name]"
                />
                <v-select
                  v-else-if="
                    f.type === 'foreign' && f.reference !== 'system_user'
                  "
                  :data-testid="'field-' + f.name"
                  v-model="form[f.name]"
                  :items="choices[f.name] || []"
                  item-value="id"
                  :item-title="
                    (item: BusinessRow) =>
                      String(item.name || item.code || item.id)
                  "
                  :label="f.label"
                  variant="outlined"
                  density="comfortable"
                  base-color="input-border"
                  :rules="rules(f)"
                  :error-messages="fieldErrors[f.name]"
                />
                <v-text-field
                  v-else
                  :data-testid="'field-' + f.name"
                  :model-value="String(form[f.name] ?? '')"
                  @update:model-value="form[f.name] = $event"
                  :label="f.label"
                  :type="
                    f.type === 'datetime'
                      ? 'datetime-local'
                      : f.type === 'integer' || f.type === 'foreign'
                        ? 'number'
                        : 'text'
                  "
                  :min="f.min"
                  :step="f.type === 'integer' ? 1 : undefined"
                  :maxlength="f.type === 'string' ? 255 : undefined"
                  variant="outlined"
                  density="comfortable"
                  base-color="input-border"
                  :rules="rules(f)"
                  :error-messages="fieldErrors[f.name]"
                /> </v-col
            ></v-row>
          </v-form> </v-container
      ></v-card-text>
      <v-card-actions class="px-6 py-4"
        ><v-spacer /><v-btn
          variant="tonal"
          size="small"
          height="36"
          width="80"
          :disabled="busy"
          @click="closeEditor"
          >取消</v-btn
        ><v-btn
          type="submit"
          form="business-form"
          variant="flat"
          color="secondary"
          size="small"
          height="36"
          width="80"
          :loading="busy"
          >保存</v-btn
        ></v-card-actions
      >
    </v-card>
  </v-dialog>
  <v-dialog
    :model-value="details !== null"
    max-width="800"
    :fullscreen="xs"
    scrollable
    @update:model-value="details = null"
  >
    <v-card>
      <v-toolbar color="secondary" density="compact"
        ><v-toolbar-title class="text-subtitle-1"
          >{{ config.label }}详情</v-toolbar-title
        ><template #append
          ><v-btn
            icon
            size="x-small"
            class="mr-4"
            aria-label="关闭详情"
            @click="details = null"
            ><IconX :size="16" /></v-btn></template
      ></v-toolbar>
      <v-card-text class="pa-6"
        ><v-row v-if="details"
          ><v-col cols="12" sm="6"
            ><p class="text-caption text-medium-emphasis">ID</p>
            <p class="text-body-2 text-break">{{ details.id }}</p></v-col
          ><v-col v-for="f in config.fields" :key="f.name" cols="12" sm="6"
            ><p class="text-caption text-medium-emphasis">{{ f.label }}</p>
            <p class="text-body-2 text-break">
              {{ details[f.name] ?? "—" }}
            </p></v-col
          ><v-col v-if="config.workflow" cols="12" sm="6"
            ><p class="text-caption text-medium-emphasis">状态</p>
            <p class="text-body-2">
              {{
                config.workflow.state_labels?.[String(details.status)] ||
                details.status
              }}
            </p></v-col
          ><v-col
            v-for="extra in additionalDetails"
            :key="extra.key"
            cols="12"
            sm="6"
            ><p class="text-caption text-medium-emphasis">{{ extra.label }}</p>
            <p class="text-body-2 text-break">
              {{ extra.value ?? "—" }}
            </p></v-col
          ></v-row
        ></v-card-text
      >
      <v-card-actions class="px-6 py-4"
        ><v-spacer /><v-btn
          variant="tonal"
          size="small"
          height="36"
          width="80"
          @click="details = null"
          >关闭</v-btn
        ></v-card-actions
      >
    </v-card>
  </v-dialog>
  <ConfirmDialog
    :model-value="pending !== null"
    :title="pending ? '确认' + pending.label : ''"
    :message="
      actionError || (pending ? '确认' + pending.label + '这条记录？' : '')
    "
    :confirm-button-text="busy ? '处理中…' : '确认'"
    cancel-button-text="取消"
    :confirm-button-color="pending?.name === 'delete' ? 'error' : 'secondary'"
    @update:model-value="pending = null"
    @confirm="pending && action(pending.row, pending.name)"
  />
</template>
<style scoped>
.business-fields
  :deep(.v-field:not(.v-field--error):not(.v-field--focused) .v-field-label) {
  color: rgb(var(--v-theme-on-surface));
}
</style>
