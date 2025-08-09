<template>
  <AppLayout>
    <template #header>
      <div class="flex items-center justify-between w-full">
        <h1 class="text-2xl font-bold text-gray-800">Analysis Dashboard</h1>
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium">
          + New Analysis
        </button>
      </div>
    </template>
    
    <div class="max-w-7xl mx-auto">
      <div class="mb-12">
        <h2 class="text-gray-700 mb-4 text-2xl font-semibold">Welcome to ClarityCheck</h2>
        <p class="text-gray-600 text-lg">Analyze your website's visual clarity and text readability. Get actionable insights to improve user experience before launch.</p>
      </div>
      
      <!-- Quick Analysis Input -->
      <div class="bg-white rounded-xl p-8 shadow-sm border border-gray-100 mb-8">
        <h3 class="text-xl font-semibold text-gray-800 mb-4">Quick Website Analysis</h3>
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
        <p class="text-sm text-gray-500 mt-2">
          {{ isAnalyzing ? 'Analysis in progress, please wait...' : 'Analysis takes ~15 seconds. No code injection required.' }}
        </p>
        
        <!-- Error Message -->
        <div v-if="errorMessage" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-700">{{ errorMessage }}</p>
        </div>
      </div>
      
      <!-- Analysis Results -->
      <div v-if="analysisResult" class="bg-white rounded-xl p-8 shadow-sm border border-gray-100 mb-8">
        <h3 class="text-xl font-semibold text-gray-800 mb-6">Analysis Results</h3>
        
        <!-- Overall Score -->
        <div class="text-center mb-6">
          <div class="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full text-white mb-4">
            <span class="text-2xl font-bold">{{ Math.round(analysisResult.overall_score) }}</span>
          </div>
          <h4 class="text-lg font-semibold text-gray-800">Grade: {{ analysisResult.grade }}</h4>
          <p class="text-gray-600 mt-2">{{ analysisResult.summary }}</p>
          
          <div class="flex justify-center items-center gap-4 mt-4 text-sm text-gray-500">
            <span>📊 {{ analysisResult.url_analyzed }}</span>
            <span v-if="analysisResult.analysis_time">⏱️ {{ analysisResult.analysis_time }}s</span>
          </div>
        </div>
        
        <!-- Website Screenshot -->
        <div v-if="analysisResult.screenshot_url" class="mb-8">
          <h4 class="text-lg font-semibold text-gray-800 mb-4 text-center">📸 Website Preview</h4>
          <div class="flex justify-center">
            <div class="border rounded-lg overflow-hidden shadow-lg max-w-2xl">
              <img 
                :src="analysisResult.screenshot_url" 
                :alt="`Screenshot of ${analysisResult.url_analyzed}`"
                class="w-full h-auto max-h-96 object-cover"
                loading="lazy"
              />
              <div class="bg-gray-50 px-4 py-2 text-sm text-gray-600 text-center">
                Screenshot captured during analysis
              </div>
            </div>
          </div>
        </div>
        
        <!-- Score Breakdown -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-blue-50 p-6 rounded-lg">
            <h5 class="font-semibold text-blue-800 mb-2">Visual Score</h5>
            <div class="flex items-center">
              <div class="flex-1 bg-blue-200 rounded-full h-3 mr-4">
                <div class="bg-blue-600 h-3 rounded-full" :style="`width: ${analysisResult.visual_score}%`"></div>
              </div>
              <span class="font-bold text-blue-800">{{ Math.round(analysisResult.visual_score) }}</span>
            </div>
          </div>
          
          <div class="bg-green-50 p-6 rounded-lg">
            <h5 class="font-semibold text-green-800 mb-2">Text & SEO Score</h5>
            <div class="flex items-center">
              <div class="flex-1 bg-green-200 rounded-full h-3 mr-4">
                <div class="bg-green-600 h-3 rounded-full" :style="`width: ${analysisResult.text_score}%`"></div>
              </div>
              <span class="font-bold text-green-800">{{ Math.round(analysisResult.text_score) }}</span>
            </div>
          </div>
          
          <div class="bg-purple-50 p-6 rounded-lg">
            <h5 class="font-semibold text-purple-800 mb-2">Clarity Score ✨</h5>
            <div class="flex items-center">
              <div class="flex-1 bg-purple-200 rounded-full h-3 mr-4">
                <div class="bg-purple-600 h-3 rounded-full" :style="`width: ${analysisResult.clarity_score}%`"></div>
              </div>
              <span class="font-bold text-purple-800">{{ Math.round(analysisResult.clarity_score) }}</span>
            </div>
          </div>
        </div>
        
        <!-- UX Patterns & Conversion Risks -->
        <div v-if="analysisResult.ux_patterns && analysisResult.ux_patterns.length > 0" class="bg-orange-50 border border-orange-200 rounded-lg p-6 mb-8">
          <h5 class="font-semibold text-orange-800 mb-4">🎯 UX Patterns Detected ({{ analysisResult.conversion_risks }} Conversion Risks)</h5>
          <div class="space-y-4">
            <div v-for="pattern in analysisResult.ux_patterns" :key="pattern.pattern" class="bg-white p-4 rounded-lg border">
              <div class="flex items-start justify-between mb-2">
                <h6 class="font-semibold text-gray-800">{{ pattern.title }}</h6>
                <span :class="{
                  'bg-red-100 text-red-800': pattern.severity === 'high',
                  'bg-yellow-100 text-yellow-800': pattern.severity === 'medium',
                  'bg-blue-100 text-blue-800': pattern.severity === 'low'
                }" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ pattern.severity.toUpperCase() }}
                </span>
              </div>
              <p class="text-gray-600 text-sm mb-2">{{ pattern.description }}</p>
              <p class="text-gray-500 text-xs mb-2">💡 <strong>Fix:</strong> {{ pattern.fix }}</p>
              <p class="text-gray-500 text-xs">📊 <strong>Impact:</strong> {{ pattern.impact }}</p>
            </div>
          </div>
        </div>
        
        <!-- Two Column Analysis -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          <!-- Left Column: Visual Analysis -->
          <div class="bg-blue-50 rounded-xl p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">👁️</span>
              </div>
              <div>
                <h4 class="text-xl font-semibold text-blue-800">Visual Analysis</h4>
                <p class="text-blue-600 text-sm">Layout, accessibility, and visual elements</p>
              </div>
            </div>
            
            <!-- Visual Score -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium text-blue-800">Visual Score</span>
                <span class="font-bold text-blue-800 text-lg">{{ Math.round(analysisResult.visual_score) }}/100</span>
              </div>
              <div class="bg-blue-200 rounded-full h-3">
                <div class="bg-blue-600 h-3 rounded-full transition-all duration-500" :style="`width: ${analysisResult.visual_score}%`"></div>
              </div>
            </div>
            
            <!-- Visual Issues -->
            <div v-if="analysisResult.visual_issues && analysisResult.visual_issues.length > 0" class="mb-6">
              <h5 class="font-semibold text-blue-800 mb-3">Visual Issues ({{ analysisResult.visual_issues.length }})</h5>
              <div class="space-y-3">
                <div v-for="issue in analysisResult.visual_issues" :key="issue.element" class="bg-white p-4 rounded-lg border border-blue-200">
                  <div class="flex items-start justify-between mb-2">
                    <span :class="{
                      'bg-red-100 text-red-800': issue.severity === 'high',
                      'bg-yellow-100 text-yellow-800': issue.severity === 'medium',
                      'bg-blue-100 text-blue-800': issue.severity === 'low'
                    }" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ issue.severity.toUpperCase() }}
                    </span>
                  </div>
                  <p class="font-medium text-gray-800 mb-1">{{ issue.message }}</p>
                  <p class="text-sm text-gray-600 mb-2">{{ issue.element }}</p>
                  <p class="text-xs text-blue-700">💡 {{ issue.suggestion }}</p>
                </div>
              </div>
            </div>
            
            <!-- Visual Recommendations -->
            <div v-if="analysisResult.visual_recommendations && analysisResult.visual_recommendations.length > 0">
              <h5 class="font-semibold text-blue-800 mb-3">Visual Recommendations</h5>
              <div class="space-y-3">
                <div v-for="rec in analysisResult.visual_recommendations" :key="rec.action" class="bg-white p-4 rounded-lg border border-blue-200">
                  <div class="flex items-start justify-between mb-2">
                    <span :class="{
                      'bg-red-100 text-red-800': rec.priority === 'Critical' || rec.priority === 'High',
                      'bg-yellow-100 text-yellow-800': rec.priority === 'Medium',
                      'bg-green-100 text-green-800': rec.priority === 'Low'
                    }" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ rec.priority.toUpperCase() }}
                    </span>
                  </div>
                  <p class="font-medium text-gray-800 mb-1">{{ rec.action }}</p>
                  <p class="text-sm text-gray-600">{{ rec.description }}</p>
                </div>
              </div>
            </div>
            
            <div v-if="(!analysisResult.visual_issues || analysisResult.visual_issues.length === 0) && (!analysisResult.visual_recommendations || analysisResult.visual_recommendations.length === 0)" class="text-center py-8">
              <span class="text-blue-600 text-4xl">✅</span>
              <p class="text-blue-700 font-medium mt-2">No visual issues found!</p>
              <p class="text-blue-600 text-sm">Your visual design is working well</p>
            </div>
          </div>
          
          <!-- Right Column: Text & SEO Analysis -->
          <div class="bg-green-50 rounded-xl p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">📝</span>
              </div>
              <div>
                <h4 class="text-xl font-semibold text-green-800">Text & SEO Analysis</h4>
                <p class="text-green-600 text-sm">Content, readability, and search optimization</p>
              </div>
            </div>
            
            <!-- Text Score -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium text-green-800">Text & SEO Score</span>
                <span class="font-bold text-green-800 text-lg">{{ Math.round(analysisResult.text_score) }}/100</span>
              </div>
              <div class="bg-green-200 rounded-full h-3">
                <div class="bg-green-600 h-3 rounded-full transition-all duration-500" :style="`width: ${analysisResult.text_score}%`"></div>
              </div>
            </div>
            
            <!-- Text/SEO Issues -->
            <div v-if="analysisResult.text_seo_issues && analysisResult.text_seo_issues.length > 0" class="mb-6">
              <h5 class="font-semibold text-green-800 mb-3">Content & SEO Issues ({{ analysisResult.text_seo_issues.length }})</h5>
              <div class="space-y-3">
                <div v-for="issue in analysisResult.text_seo_issues" :key="issue.element" class="bg-white p-4 rounded-lg border border-green-200">
                  <div class="flex items-start justify-between mb-2">
                    <span :class="{
                      'bg-red-100 text-red-800': issue.severity === 'high',
                      'bg-yellow-100 text-yellow-800': issue.severity === 'medium',
                      'bg-blue-100 text-blue-800': issue.severity === 'low'
                    }" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ issue.severity.toUpperCase() }}
                    </span>
                  </div>
                  <p class="font-medium text-gray-800 mb-1">{{ issue.message }}</p>
                  <p class="text-sm text-gray-600 mb-2">{{ issue.element }}</p>
                  <p class="text-xs text-green-700">💡 {{ issue.suggestion }}</p>
                </div>
              </div>
            </div>
            
            <!-- Text/SEO Recommendations -->
            <div v-if="analysisResult.text_seo_recommendations && analysisResult.text_seo_recommendations.length > 0">
              <h5 class="font-semibold text-green-800 mb-3">Content & SEO Recommendations</h5>
              <div class="space-y-3">
                <div v-for="rec in analysisResult.text_seo_recommendations" :key="rec.action" class="bg-white p-4 rounded-lg border border-green-200">
                  <div class="flex items-start justify-between mb-2">
                    <span :class="{
                      'bg-red-100 text-red-800': rec.priority === 'Critical' || rec.priority === 'High',
                      'bg-yellow-100 text-yellow-800': rec.priority === 'Medium',
                      'bg-green-100 text-green-800': rec.priority === 'Low'
                    }" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ rec.priority.toUpperCase() }}
                    </span>
                  </div>
                  <p class="font-medium text-gray-800 mb-1">{{ rec.action }}</p>
                  <p class="text-sm text-gray-600">{{ rec.description }}</p>
                </div>
              </div>
            </div>
            
            <div v-if="(!analysisResult.text_seo_issues || analysisResult.text_seo_issues.length === 0) && (!analysisResult.text_seo_recommendations || analysisResult.text_seo_recommendations.length === 0)" class="text-center py-8">
              <span class="text-green-600 text-4xl">✅</span>
              <p class="text-green-700 font-medium mt-2">No content issues found!</p>
              <p class="text-green-600 text-sm">Your content and SEO are optimized</p>
            </div>
          </div>
          
        </div>
      </div>
      
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-8 rounded-xl text-center shadow-lg">
          <h3 class="m-0 mb-2 text-base opacity-90 font-medium">Analyses This Month</h3>
          <p class="text-4xl font-bold m-0 mb-2">3</p>
          <p class="text-sm opacity-80">of 3 free</p>
        </div>
        <div class="bg-gradient-to-br from-emerald-500 to-teal-600 text-white p-8 rounded-xl text-center shadow-lg">
          <h3 class="m-0 mb-2 text-base opacity-90 font-medium">Average Clarity Score</h3>
          <p class="text-4xl font-bold m-0 mb-2">74</p>
          <p class="text-sm opacity-80">across all sites</p>
        </div>
        <div class="bg-gradient-to-br from-orange-500 to-pink-600 text-white p-8 rounded-xl text-center shadow-lg">
          <h3 class="m-0 mb-2 text-base opacity-90 font-medium">Issues Fixed</h3>
          <p class="text-4xl font-bold m-0 mb-2">127</p>
          <p class="text-sm opacity-80">this month</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent analyses -->
        <div class="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Recent Analyses</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span class="text-blue-600 font-semibold">68</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">example.com</p>
                  <p class="text-sm text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div class="text-right">
                <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">Needs Work</span>
              </div>
            </div>
            <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <span class="text-green-600 font-semibold">89</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">mystore.com</p>
                  <p class="text-sm text-gray-500">1 day ago</p>
                </div>
              </div>
              <div class="text-right">
                <span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">Excellent</span>
              </div>
            </div>
            <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                  <span class="text-red-600 font-semibold">42</span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">oldsite.net</p>
                  <p class="text-sm text-gray-500">3 days ago</p>
                </div>
              </div>
              <div class="text-right">
                <span class="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">Poor</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Analysis tools -->
        <div class="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Analysis Tools</h3>
          <div class="grid grid-cols-1 gap-3">
            <button class="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 transition-colors text-left">
              <div class="font-medium mb-1">Visual Clarity Analysis</div>
              <div class="text-sm opacity-90">Check contrast, layout, and CTA visibility</div>
            </button>
            <button class="bg-green-600 text-white p-4 rounded-lg hover:bg-green-700 transition-colors text-left">
              <div class="font-medium mb-1">Text Readability Check</div>
              <div class="text-sm opacity-90">Analyze language complexity and structure</div>
            </button>
            <button class="bg-purple-600 text-white p-4 rounded-lg hover:bg-purple-700 transition-colors text-left">
              <div class="font-medium mb-1">Full UX Report</div>
              <div class="text-sm opacity-90">Complete analysis with PDF export</div>
            </button>
          </div>
          
          <div class="mt-4 p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Usage (Free Plan)</span>
              <span class="text-sm text-gray-500">3/3</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-blue-600 h-2 rounded-full" style="width: 100%"></div>
            </div>
            <p class="text-xs text-gray-500 mt-2">Upgrade to Pro for unlimited analyses</p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '~/components/AppLayout.vue'

// Reactive state
const websiteUrl = ref('')
const isAnalyzing = ref(false)
const analysisResult = ref(null)
const errorMessage = ref('')

// API configuration
const API_BASE_URL = 'http://localhost:8000'

// Analysis function
const analyzeWebsite = async () => {
  if (!websiteUrl.value) {
    errorMessage.value = 'Please enter a valid website URL'
    return
  }

  // Clear previous results
  analysisResult.value = null
  errorMessage.value = ''
  isAnalyzing.value = true

  try {
    console.log('Analyzing website:', websiteUrl.value)
    
    const response = await $fetch(`${API_BASE_URL}/api/v1/analyze/quick`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: websiteUrl.value
      })
    })

    analysisResult.value = response
    console.log('Analysis result:', response)
    
  } catch (error) {
    console.error('Analysis error:', error)
    
    if (error.data) {
      errorMessage.value = `Analysis failed: ${error.data.detail || error.data.message || 'Unknown error'}`
    } else if (error.message) {
      errorMessage.value = `Network error: ${error.message}`
    } else {
      errorMessage.value = 'Failed to analyze website. Please check your connection and try again.'
    }
  } finally {
    isAnalyzing.value = false
  }
}

// Auto-focus URL input on mount
onMounted(() => {
  console.log('ClarityCheck dashboard loaded')
})
</script>