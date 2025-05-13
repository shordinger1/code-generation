<template>
    <div>
      <div
        v-if="node.isDir"
        @dblclick="toggle"
        style="font-weight:bold;cursor:pointer;"
      >
        📁 {{ node.name }}
      </div>
      <div v-if="node.isDir && node.expanded" style="margin-left:16px;">
        <TreeNode
          v-for="child in node.children"
          :key="child.path"
          :node="child"
          @open="$emit('open', $event)"
        />
      </div>
      <div
        v-else
        @dblclick="$emit('open', node)"
        style="cursor:pointer;"
      >
        📄 {{ node.name }}
      </div>
    </div>
  </template>
  <script setup lang="ts">
  const props = defineProps<{ node: any }>()
  const emit = defineEmits(['open'])
  function toggle() {
    props.node.expanded = !props.node.expanded
  }
  </script>