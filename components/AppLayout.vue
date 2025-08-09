<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />
    <main class="mt-[70px] p-8 min-h-[calc(100vh-70px)]">
      <div class="mb-8">
        <slot name="header"></slot>
      </div>
      <div class="bg-white rounded-lg p-8 shadow-sm min-h-96">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script setup>
import AppHeader from './AppHeader.vue'
</script>