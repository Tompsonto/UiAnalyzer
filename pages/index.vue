<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-800">ClarityCheck</h1>
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium">
          + New Analysis
        </button>
      </div>
    </div>

    <!-- Analysis Input -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex gap-4">
        <input 
          v-model="websiteUrl"
          type="url" 
          placeholder="Enter website URL (e.g., https://example.com)" 
          class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :disabled="isAnalyzing"
        >
        <button 
          @click="analyzeWebsite"
          :disabled="isAnalyzing || !websiteUrl"
          class="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium whitespace-nowrap disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ isAnalyzing ? 'Analyzing...' : 'Analyze Now' }}
        </button>
      </div>
      
      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-700">{{ errorMessage }}</p>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="isAnalyzing" class="bg-white border-b border-gray-200 px-6 py-8">
      <div class="max-w-2xl mx-auto">
        <!-- Main Progress Bar -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-lg font-semibold text-gray-800">Analyzing {{ websiteUrl }}</h3>
            <span class="text-sm text-gray-600">{{ Math.round(analysisProgress) }}%</span>
          </div>
          <div class="bg-gray-200 rounded-full h-3">
            <div 
              class="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-300" 
              :style="`width: ${analysisProgress}%`"
            ></div>
          </div>
        </div>

        <!-- Analysis Steps -->
        <div class="space-y-4">
          <div 
            v-for="(step, index) in analysisSteps" 
            :key="step.id"
            class="flex items-center p-4 rounded-lg"
            :class="{
              'bg-blue-50 border border-blue-200': step.status === 'active',
              'bg-green-50 border border-green-200': step.status === 'completed',
              'bg-gray-50 border border-gray-200': step.status === 'pending'
            }"
          >
            <!-- Step Icon -->
            <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mr-4">
              <div v-if="step.status === 'completed'" class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <div v-else-if="step.status === 'active'" class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                <div class="w-2 h-2 bg-white rounded-full animate-ping"></div>
              </div>
              <div v-else class="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
                <span class="text-xs text-gray-600">{{ index + 1 }}</span>
              </div>
            </div>

            <!-- Step Content -->
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <h4 class="font-medium" :class="{
                  'text-blue-800': step.status === 'active',
                  'text-green-800': step.status === 'completed',
                  'text-gray-600': step.status === 'pending'
                }">
                  {{ step.title }}
                </h4>
                <span v-if="step.status === 'active'" class="text-sm text-blue-600 font-medium">
                  {{ step.duration }}
                </span>
              </div>
              <p class="text-sm mt-1" :class="{
                'text-blue-700': step.status === 'active',
                'text-green-700': step.status === 'completed',
                'text-gray-500': step.status === 'pending'
              }">
                {{ step.description }}
              </p>
              <div v-if="step.status === 'active' && step.subSteps" class="mt-2 pl-4 border-l-2 border-blue-200">
                <p class="text-xs text-blue-600">{{ step.subSteps[currentSubStep] }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Estimated Time -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            <span class="inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2"></span>
            Estimated time remaining: {{ estimatedTimeRemaining }}
          </p>
        </div>
      </div>
    </div>
    <!-- Main Content: 50/50 Split -->
    <div v-if="analysisResult" class="flex min-h-screen">
      <!-- Left Column: 50% width with tabs -->
      <div class="w-1/2 bg-white border-r border-gray-200">
        <!-- Tab Navigation -->
        <div class="border-b border-gray-200 bg-gray-50">
          <nav class="flex">
            <button 
              @click="activeTab = 'visuals'" 
              :class="{
                'bg-white border-b-2 border-blue-500 text-blue-600': activeTab === 'visuals',
                'text-gray-500 hover:text-gray-700': activeTab !== 'visuals'
              }"
              class="px-6 py-4 text-sm font-medium"
            >
              👁️ Visuals
            </button>
            <button 
              @click="activeTab = 'seo'" 
              :class="{
                'bg-white border-b-2 border-blue-500 text-blue-600': activeTab === 'seo',
                'text-gray-500 hover:text-gray-700': activeTab !== 'seo'
              }"
              class="px-6 py-4 text-sm font-medium"
            >
              📝 SEO
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Visuals Tab -->
          <div v-if="activeTab === 'visuals'" class="space-y-6">
            <!-- Intelligent Grouped Issues - Visual Issues -->
            <div v-if="analysisResult.grouped_issues && analysisResult.grouped_issues.length > 0">
              <h3 class="text-lg font-semibold text-gray-800 mb-4">Visual Issues by Section</h3>
              <div class="space-y-4">
                <div 
                  v-for="group in getVisualGroups(analysisResult.grouped_issues)" 
                  :key="group.parent_selector" 
                  class="bg-gray-50 rounded-lg p-5 border border-gray-200"
                >
                  <!-- Group Header -->
                  <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2">
                        <h4 class="text-lg font-semibold text-gray-800">{{ group.parent_description }}</h4>
                        <span :class="{
                          'bg-red-100 text-red-800': group.severity === 'high',
                          'bg-yellow-100 text-yellow-800': group.severity === 'medium',
                          'bg-blue-100 text-blue-800': group.severity === 'low'
                        }" class="px-3 py-1 rounded-full text-sm font-medium">
                          {{ group.severity.toUpperCase() }}
                        </span>
                        <span class="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
                          {{ group.issue_count }} issues
                        </span>
                      </div>
                      <p class="text-gray-600 text-sm mb-2">{{ group.summary_message }}</p>
                      <p class="text-xs text-gray-500">{{ group.content_summary }}</p>
                    </div>
                  </div>
                  
                  <!-- Container Suggestions -->
                  <div v-if="group.grouped_suggestions && group.grouped_suggestions.length > 0" class="mb-4">
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h6 class="font-semibold text-blue-800 mb-2">💡 Container-Level Fixes</h6>
                      <ul class="space-y-1">
                        <li v-for="suggestion in group.grouped_suggestions" :key="suggestion" class="text-sm text-blue-700 flex items-start">
                          <span class="text-blue-400 mr-2">•</span>
                          {{ suggestion }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  
                  <!-- Detailed Issues (Expandable) -->
                  <details class="bg-white rounded-lg border border-gray-200">
                    <summary class="px-4 py-3 cursor-pointer hover:bg-gray-50 font-medium text-gray-700">
                      View {{ getVisualIssuesFromGroup(group).length }} detailed issues
                    </summary>
                    <div class="px-4 pb-4 space-y-3">
                      <div 
                        v-for="detail in getVisualIssuesFromGroup(group)" 
                        :key="`${detail.element}-${detail.source}`" 
                        class="bg-gray-50 p-3 rounded border-l-4" 
                        :class="{
                          'border-l-red-400': detail.severity === 'high',
                          'border-l-yellow-400': detail.severity === 'medium',
                          'border-l-blue-400': detail.severity === 'low'
                        }"
                      >
                        <div class="flex items-start justify-between mb-2">
                          <div class="flex items-center gap-2">
                            <span :class="{
                              'bg-red-100 text-red-700': detail.severity === 'high',
                              'bg-yellow-100 text-yellow-700': detail.severity === 'medium',
                              'bg-blue-100 text-blue-700': detail.severity === 'low'
                            }" class="px-2 py-1 rounded text-xs font-medium">
                              {{ detail.severity.toUpperCase() }}
                            </span>
                            <span :class="{
                              'bg-purple-100 text-purple-700': detail.source === 'accessibility',
                              'bg-blue-100 text-blue-700': detail.source === 'visual',
                              'bg-orange-100 text-orange-700': detail.source === 'cta'
                            }" class="px-2 py-1 rounded text-xs font-medium">
                              {{ detail.source.toUpperCase() }}
                            </span>
                          </div>
                        </div>
                        <p class="font-medium text-gray-800 text-sm mb-1">{{ detail.message }}</p>
                        <p class="text-xs text-gray-600 mb-2">{{ detail.element }}</p>
                        <p class="text-xs text-gray-700 bg-white p-2 rounded border">💡 {{ detail.suggestion }}</p>
                      </div>
                    </div>
                  </details>
                </div>
              </div>
            </div>

            <!-- No Issues Message -->
            <div v-if="!analysisResult.grouped_issues || getVisualGroups(analysisResult.grouped_issues).length === 0" class="text-center py-8">
              <span class="text-blue-600 text-4xl">✅</span>
              <p class="text-blue-700 font-medium mt-2">No visual issues found!</p>
              <p class="text-blue-600 text-sm">Your visual design is working well</p>
            </div>
          </div>

          <!-- SEO Tab -->
          <div v-if="activeTab === 'seo'" class="space-y-6">
            <!-- Intelligent Grouped Issues - SEO Issues -->
            <div v-if="analysisResult.grouped_issues && analysisResult.grouped_issues.length > 0">
              <h3 class="text-lg font-semibold text-gray-800 mb-4">SEO Issues by Section</h3>
              <div class="space-y-4">
                <div 
                  v-for="group in getSEOGroups(analysisResult.grouped_issues)" 
                  :key="group.parent_selector" 
                  class="bg-gray-50 rounded-lg p-5 border border-gray-200"
                >
                  <!-- Group Header -->
                  <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2">
                        <h4 class="text-lg font-semibold text-gray-800">{{ group.parent_description }}</h4>
                        <span :class="{
                          'bg-red-100 text-red-800': group.severity === 'high',
                          'bg-yellow-100 text-yellow-800': group.severity === 'medium',
                          'bg-blue-100 text-blue-800': group.severity === 'low'
                        }" class="px-3 py-1 rounded-full text-sm font-medium">
                          {{ group.severity.toUpperCase() }}
                        </span>
                        <span class="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs font-medium">
                          {{ getSEOIssuesFromGroup(group).length }} issues
                        </span>
                      </div>
                      <p class="text-gray-600 text-sm mb-2">{{ group.summary_message }}</p>
                      <p class="text-xs text-gray-500">{{ group.content_summary }}</p>
                    </div>
                  </div>
                  
                  <!-- Container Suggestions -->
                  <div v-if="group.grouped_suggestions && group.grouped_suggestions.length > 0" class="mb-4">
                    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h6 class="font-semibold text-green-800 mb-2">💡 Container-Level Fixes</h6>
                      <ul class="space-y-1">
                        <li v-for="suggestion in group.grouped_suggestions" :key="suggestion" class="text-sm text-green-700 flex items-start">
                          <span class="text-green-400 mr-2">•</span>
                          {{ suggestion }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  
                  <!-- Detailed Issues (Expandable) -->
                  <details class="bg-white rounded-lg border border-gray-200">
                    <summary class="px-4 py-3 cursor-pointer hover:bg-gray-50 font-medium text-gray-700">
                      View {{ getSEOIssuesFromGroup(group).length }} detailed issues
                    </summary>
                    <div class="px-4 pb-4 space-y-3">
                      <div 
                        v-for="detail in getSEOIssuesFromGroup(group)" 
                        :key="`${detail.element}-${detail.source}`" 
                        class="bg-gray-50 p-3 rounded border-l-4 border-l-green-400"
                      >
                        <div class="flex items-start justify-between mb-2">
                          <div class="flex items-center gap-2">
                            <span :class="{
                              'bg-red-100 text-red-700': detail.severity === 'high',
                              'bg-yellow-100 text-yellow-700': detail.severity === 'medium',
                              'bg-blue-100 text-blue-700': detail.severity === 'low'
                            }" class="px-2 py-1 rounded text-xs font-medium">
                              {{ detail.severity.toUpperCase() }}
                            </span>
                            <span class="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-medium">
                              {{ detail.source.toUpperCase() }}
                            </span>
                          </div>
                        </div>
                        <p class="font-medium text-gray-800 text-sm mb-1">{{ detail.message }}</p>
                        <p class="text-xs text-gray-600 mb-2">{{ detail.element }}</p>
                        <p class="text-xs text-gray-700 bg-white p-2 rounded border">💡 {{ detail.suggestion }}</p>
                      </div>
                    </div>
                  </details>
                </div>
              </div>
            </div>

            <!-- No Issues Message -->
            <div v-if="!analysisResult.grouped_issues || getSEOGroups(analysisResult.grouped_issues).length === 0" class="text-center py-8">
              <span class="text-green-600 text-4xl">✅</span>
              <p class="text-green-700 font-medium mt-2">No content issues found!</p>
              <p class="text-green-600 text-sm">Your content and SEO are optimized</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: 50% width with full-height scrollable screenshot -->
      <div class="w-1/2 bg-gray-100 p-4">
        <div v-if="analysisResult.screenshot_url" class="w-full bg-white rounded-lg shadow-lg">
          <div class="p-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">📸 Website Screenshot</h3>
            <div class="border rounded-lg">
              <img 
                :src="analysisResult.screenshot_url" 
                :alt="`Screenshot of ${analysisResult.url_analyzed}`"
                class="w-full h-auto"
                loading="lazy"
                @load="console.log('Screenshot loaded successfully')"
                @error="console.log('Screenshot failed to load', $event)"
              />
            </div>
          </div>
        </div>
        <div v-else class="w-full h-full flex items-center justify-center text-center text-gray-500 bg-white rounded-lg shadow-lg">
          <div>
            <div class="text-6xl mb-4">📸</div>
            <p class="text-lg font-medium">Screenshot unavailable</p>
            <p class="text-sm">The website screenshot could not be captured</p>
            <p class="text-xs text-gray-400 mt-2">Debug: {{ analysisResult ? 'Analysis result exists' : 'No analysis result' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Reactive state
const websiteUrl = ref('')
const isAnalyzing = ref(false)
const analysisResult = ref(null)
const errorMessage = ref('')
const activeTab = ref('visuals')

// Loading state
const analysisProgress = ref(0)
const currentSubStep = ref(0)
const estimatedTimeRemaining = ref('15 seconds')

// Analysis steps
const analysisSteps = ref([
  {
    id: 'setup',
    title: 'Setting up analysis',
    description: 'Initializing browser and preparing for website capture',
    status: 'pending',
    duration: '~2s',
    subSteps: [
      'Starting Chrome browser...',
      'Configuring viewport settings...',
      'Setting up accessibility scanner...'
    ]
  },
  {
    id: 'render',
    title: 'Rendering website',
    description: 'Loading the website and capturing full-page screenshot',
    status: 'pending',
    duration: '~4s',
    subSteps: [
      'Navigating to website...',
      'Waiting for page to load...',
      'Capturing full-page screenshot...',
      'Extracting DOM structure...'
    ]
  },
  {
    id: 'visual',
    title: 'Visual analysis',
    description: 'Analyzing typography, contrast, layout, and visual elements',
    status: 'pending',
    duration: '~3s',
    subSteps: [
      'Checking color contrast ratios...',
      'Analyzing typography hierarchy...',
      'Measuring tap target sizes...',
      'Detecting element overlaps...'
    ]
  },
  {
    id: 'accessibility',
    title: 'Accessibility testing',
    description: 'Running automated accessibility checks with axe-core',
    status: 'pending',
    duration: '~2s',
    subSteps: [
      'Injecting axe-core scanner...',
      'Running accessibility audit...',
      'Checking WCAG compliance...',
      'Analyzing keyboard navigation...'
    ]
  },
  {
    id: 'cta',
    title: 'CTA analysis',
    description: 'Identifying and analyzing call-to-action elements',
    status: 'pending',
    duration: '~2s',
    subSteps: [
      'Detecting CTA elements...',
      'Analyzing button visibility...',
      'Checking placement optimization...',
      'Scoring CTA effectiveness...'
    ]
  },
  {
    id: 'grouping',
    title: 'Issue grouping',
    description: 'Organizing issues by DOM elements for easier fixes',
    status: 'pending',
    duration: '~2s',
    subSteps: [
      'Analyzing DOM hierarchy...',
      'Grouping related issues...',
      'Generating fix suggestions...',
      'Finalizing report...'
    ]
  }
])

// Progress simulation
let progressInterval = null
let subStepInterval = null

const simulateProgress = () => {
  let currentStep = 0
  let stepProgress = 0
  
  progressInterval = setInterval(() => {
    if (currentStep < analysisSteps.value.length) {
      const step = analysisSteps.value[currentStep]
      
      // Mark current step as active
      if (step.status === 'pending') {
        step.status = 'active'
        startSubStepRotation(currentStep)
      }
      
      // Update progress
      stepProgress += 2
      const baseProgress = (currentStep / analysisSteps.value.length) * 100
      const currentStepProgress = (stepProgress / 100) * (100 / analysisSteps.value.length)
      analysisProgress.value = Math.min(baseProgress + currentStepProgress, 100)
      
      // Move to next step
      if (stepProgress >= 100) {
        step.status = 'completed'
        stopSubStepRotation()
        currentStep++
        stepProgress = 0
        
        // Update estimated time
        const remainingSteps = analysisSteps.value.length - currentStep
        const avgTimePerStep = 2.5
        const remainingTime = Math.max(remainingSteps * avgTimePerStep, 0)
        estimatedTimeRemaining.value = remainingTime > 0 ? `${Math.round(remainingTime)} seconds` : 'Almost done...'
      }
    } else {
      // Analysis complete
      clearInterval(progressInterval)
      analysisProgress.value = 100
      estimatedTimeRemaining.value = 'Complete!'
    }
  }, 200) // Update every 200ms
}

const startSubStepRotation = (stepIndex) => {
  const step = analysisSteps.value[stepIndex]
  if (!step.subSteps) return
  
  currentSubStep.value = 0
  subStepInterval = setInterval(() => {
    currentSubStep.value = (currentSubStep.value + 1) % step.subSteps.length
  }, 800) // Change substep every 800ms
}

const stopSubStepRotation = () => {
  if (subStepInterval) {
    clearInterval(subStepInterval)
    subStepInterval = null
  }
}

const resetAnalysisState = () => {
  analysisProgress.value = 0
  currentSubStep.value = 0
  estimatedTimeRemaining.value = '15 seconds'
  analysisSteps.value.forEach(step => {
    step.status = 'pending'
  })
  
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
  if (subStepInterval) {
    clearInterval(subStepInterval) 
    subStepInterval = null
  }
}

// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000'

// Analysis function
const analyzeWebsite = async () => {
  if (!websiteUrl.value) {
    errorMessage.value = 'Please enter a valid website URL'
    return
  }

  // Clear previous results and reset state
  analysisResult.value = null
  errorMessage.value = ''
  isAnalyzing.value = true
  resetAnalysisState()
  
  // Start progress simulation
  simulateProgress()

  try {
    console.log('Analyzing website:', websiteUrl.value)
    console.log('API URL:', `${API_BASE_URL}/api/v1/analyze/quick`)
    
    const response = await $fetch(`${API_BASE_URL}/api/v1/analyze/quick`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: websiteUrl.value
      }),
      timeout: 120000, // 2 minutes timeout
      retry: false
    })

    console.log('Analysis completed successfully:', response)
    console.log('Grouped issues received:', response.grouped_issues)
    console.log('Grouped issues count:', response.grouped_issues?.length || 0)
    console.log('Screenshot URL:', response.screenshot_url)

    // Stop progress simulation immediately
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
    if (subStepInterval) {
      clearInterval(subStepInterval)
      subStepInterval = null
    }

    // Complete all steps and set progress to 100%
    analysisSteps.value.forEach(step => {
      step.status = 'completed'
    })
    analysisProgress.value = 100
    estimatedTimeRemaining.value = 'Complete!'
    
    // Small delay to show completion before hiding loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Set results and hide loading
    analysisResult.value = response
    isAnalyzing.value = false
    
    console.log('Analysis UI state updated - should now show results')
    
  } catch (error) {
    console.error('Analysis error:', error)
    
    // Stop progress simulation on error
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
    if (subStepInterval) {
      clearInterval(subStepInterval)
      subStepInterval = null
    }
    
    // Mark all steps as failed/incomplete and hide loading
    analysisSteps.value.forEach(step => {
      if (step.status === 'active') {
        step.status = 'pending'
      }
    })
    analysisProgress.value = 0
    isAnalyzing.value = false
    
    // Show detailed error message
    if (error.data && error.data.detail) {
      errorMessage.value = `Analysis failed: ${error.data.detail}`
    } else if (error.response && error.response._data && error.response._data.detail) {
      errorMessage.value = `Analysis failed: ${error.response._data.detail}`
    } else if (error.message) {
      errorMessage.value = `Network error: ${error.message}`
    } else {
      errorMessage.value = 'Failed to analyze website. Please check your connection and try again.'
    }
    
    console.log('Error handling complete - loading should be hidden')
  }
}

// Helper methods for filtering grouped issues
const getVisualGroups = (groupedIssues) => {
  return groupedIssues.filter(group => 
    group.details && group.details.some(detail => 
      ['visual', 'accessibility', 'cta'].includes(detail.source)
    )
  )
}

const getSEOGroups = (groupedIssues) => {
  return groupedIssues.filter(group => 
    group.details && group.details.some(detail => 
      ['text'].includes(detail.source)
    )
  )
}

const getVisualIssuesFromGroup = (group) => {
  return group.details.filter(detail => 
    ['visual', 'accessibility', 'cta'].includes(detail.source)
  )
}

const getSEOIssuesFromGroup = (group) => {
  return group.details.filter(detail => 
    ['text'].includes(detail.source)
  )
}

// Auto-focus URL input on mount
onMounted(() => {
  console.log('ClarityCheck dashboard loaded')
})
</script>