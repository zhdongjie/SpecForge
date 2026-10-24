<script setup lang="ts">
import { ref, onMounted } from "vue";
import request from "@/plugins/axios";
import { useAuthorities } from "@/composables/useAuthorities";
import type { BusinessConfig, BusinessRow } from "@/api/business/generated";
const props = defineProps<{ config: BusinessConfig }>();
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
const base = `/v1/business/${props.config.name}`;
const permit = (action: string) =>
  can(`business:sf_${props.config.name}:${action}`);
async function load() {
  busy.value = true;
  error.value = "";
  try {
    const { data } = await request.get<
      unknown,
      { items: BusinessRow[]; total: number }
    >(`${base}/page`, { currentPage: page.value, pageSize: 20 });
    rows.value = data.items;
    total.value = data.total;
  } catch (e) {
    error.value = (e as Error).message || "加载失败";
  } finally {
    busy.value = false;
  }
}
async function open(row?: BusinessRow) {
  editing.value = row ? String(row.id) : null;
  form.value = {};
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
async function save() {
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
    error.value = (e as Error).message || "保存失败";
  } finally {
    busy.value = false;
  }
}
async function action(row: BusinessRow, name: string) {
  if (!window.confirm(name === "delete" ? "确认删除？" : "确认执行此操作？"))
    return;
  busy.value = true;
  error.value = "";
  try {
    if (name === "delete") await request.delete(`${base}/${row.id}`);
    else await request.post(`${base}/${row.id}/actions/${name}`);
    await load();
  } catch (e) {
    error.value = (e as Error).message || "操作失败";
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
onMounted(load);
</script>
<template>
  <v-card :title="config.label"
    ><v-card-text>
      <v-alert v-if="error" type="error" class="mb-3">{{ error }}</v-alert>
      <v-btn v-if="permit('create')" :disabled="busy" @click="open()"
        >新增{{ config.label }}</v-btn
      >
      <v-btn variant="text" :disabled="busy" @click="load">刷新</v-btn>
      <v-table
        ><thead>
          <tr>
            <th>ID</th>
            <th v-for="key in config.page.list" :key="key">
              {{ config.fields.find((f) => f.name === key)?.label }}
            </th>
            <th v-for="a in config.availability" :key="a.available_field">
              {{ a.label }}
            </th>
            <th v-if="config.workflow">状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="String(row.id)">
            <td>{{ row.id }}</td>
            <td v-for="key in config.page.list" :key="key">{{ row[key] }}</td>
            <td
              v-for="a in config.availability"
              :key="a.available_field"
              :data-testid="'availability-' + a.available_field"
            >
              {{ row[a.available_field] }}
            </td>
            <td v-if="config.workflow">
              {{
                config.workflow?.state_labels?.[String(row.status)] ||
                row.status
              }}
            </td>
            <td>
              <v-btn
                v-if="permit('detail')"
                size="small"
                variant="text"
                @click="detail(row)"
                >详情</v-btn
              >
              <v-btn
                v-if="permit('update')"
                size="small"
                :disabled="busy"
                @click="open(row)"
                >编辑</v-btn
              >
              <v-btn
                v-if="permit('delete')"
                size="small"
                :disabled="busy"
                @click="action(row, 'delete')"
                >删除</v-btn
              >
              <template v-for="a in config.workflow?.transitions" :key="a.name"
                ><v-btn
                  v-if="permit(a.name) && row.status === a.from"
                  size="small"
                  :disabled="busy"
                  @click="action(row, a.name)"
                  >{{ a.label }}</v-btn
                ></template
              >
            </td>
          </tr>
        </tbody>
      </v-table>
      <div v-if="!rows.length && !busy">暂无记录</div>
      <v-pagination
        v-model="page"
        :length="Math.max(1, Math.ceil(total / 20))"
        @update:model-value="load"
      /> </v-card-text
  ></v-card>
  <v-dialog v-model="dialog" max-width="600"
    ><v-card :title="config.label"
      ><v-card-text>
        <v-alert v-if="error" type="error">{{ error }}</v-alert>
        <template
          v-for="f in config.fields.filter((x) =>
            config.page.form.includes(x.name),
          )"
          :key="f.name"
        >
          <v-switch
            v-if="f.type === 'boolean'"
            :data-testid="'field-' + f.name"
            v-model="form[f.name]"
            :label="f.label"
          />
          <v-select
            v-else-if="f.type === 'enum'"
            :data-testid="'field-' + f.name"
            :model-value="String(form[f.name] ?? '')"
            @update:model-value="form[f.name] = $event"
            :items="f.values"
            :label="f.label"
          />
          <v-select
            v-else-if="f.type === 'foreign' && f.reference !== 'system_user'"
            :data-testid="'field-' + f.name"
            v-model="form[f.name]"
            :items="choices[f.name] || []"
            item-value="id"
            :item-title="
              (item: BusinessRow) => String(item.name || item.code || item.id)
            "
            :label="f.label"
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
          />
        </template> </v-card-text
      ><v-card-actions
        ><v-btn :disabled="busy" @click="dialog = false">取消</v-btn
        ><v-btn :disabled="busy" @click="save">保存</v-btn></v-card-actions
      ></v-card
    ></v-dialog
  >
  <v-dialog
    :model-value="details !== null"
    max-width="600"
    @update:model-value="details = null"
    ><v-card title="详情"
      ><v-card-text
        ><dl v-if="details">
          <template v-for="(value, key) in details" :key="key"
            ><dt>{{ key }}</dt>
            <dd>{{ value }}</dd></template
          >
        </dl></v-card-text
      ><v-card-actions
        ><v-btn @click="details = null">关闭</v-btn></v-card-actions
      ></v-card
    ></v-dialog
  >
</template>
