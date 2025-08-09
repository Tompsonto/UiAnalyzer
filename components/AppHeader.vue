<template>
  <header class="bg-white border-b border-gray-200 px-8 h-[70px] flex items-center sticky top-0 z-50 shadow-sm">
    <div class="flex justify-between items-center w-full max-w-7xl mx-auto">
      <div class="logo flex items-center space-x-2">
        <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <span class="text-white text-sm font-bold">✓</span>
        </div>
        <h2 class="m-0 text-gray-900 font-bold text-xl">ClarityCheck</h2>
      </div>
      <nav class="hidden md:block">
        <ul class="flex list-none m-0 p-0 space-x-8">
          <li><a href="/" class="no-underline text-gray-700 font-medium hover:text-blue-600 transition-colors duration-200">Dashboard</a></li>
          <li><a href="/analyze" class="no-underline text-gray-700 font-medium hover:text-blue-600 transition-colors duration-200">Analyze</a></li>
          <li><a href="/history" class="no-underline text-gray-700 font-medium hover:text-blue-600 transition-colors duration-200">History</a></li>
          <li><a href="/pricing" class="no-underline text-gray-700 font-medium hover:text-blue-600 transition-colors duration-200">Pricing</a></li>
        </ul>
      </nav>
      <div class="user-actions flex items-center space-x-4">
        <div class="hidden md:flex text-sm text-gray-600">
          <span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">3/3 Free analyses</span>
        </div>
        <button class="bg-blue-600 text-white border-none px-4 py-2 rounded-md font-medium cursor-pointer hover:bg-blue-700 transition-colors duration-200">
          Upgrade
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>

</script>