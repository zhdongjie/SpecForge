export type BusinessRow = {
  id: string;
  status?: string;
  [key: string]: unknown;
};
export interface BusinessField {
  name: string;
  label: string;
  type: string;
  reference?: string;
  default?: unknown;
  values?: string[];
  required?: boolean;
  unique?: boolean;
  min?: number;
}
export interface ResourceReference {
  field: string;
  active_state: string;
  terminal_states: string[];
  capacity_field?: string;
  quantity_field?: string;
}
export interface BusinessConfig {
  name: string;
  label: string;
  access: string;
  crud: string[];
  fields: BusinessField[];
  page: { list: string[]; form: string[] };
  availability?: { field: string; available_field: string; label: string }[];
  workflow?: {
    initial: string;
    states: string[];
    state_labels?: Record<string, string>;
    exclusive_reference?: ResourceReference;
    capacity_reference?: ResourceReference;
    transitions: {
      name: string;
      label: string;
      from: string;
      to: string;
      forbid_self?: boolean;
      exclusive?: boolean;
    }[];
  };
}
