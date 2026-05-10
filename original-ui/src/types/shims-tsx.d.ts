import type { VNode } from 'vue'
import type Vue from 'vue'

/* eslint-disable */
declare global {
  namespace JSX {
    interface Element extends VNode {}
    interface ElementClass extends Vue {}
    interface IntrinsicElements {
      [elem: string]: any
    }
  }
}
