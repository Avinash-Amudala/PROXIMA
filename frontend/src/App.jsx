import { useState, useEffect } from 'react'
import { Activity, AlertTriangle, TrendingUp, Target, BarChart3 } from 'lucide-react'
import { api } from './api/client'
import DataGenerator from './components/DataGenerator'
import ProxyScores from './components/ProxyScores'
import FragilityAnalysis from './components/FragilityAnalysis'
import DecisionSimulation from './components/DecisionSimulation'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('generate')
  const [dataLoaded, setDataLoaded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    try {
      const health = await api.healthCheck()
      setDataLoaded(health.data_loaded)
    } catch (error) {
      console.error('Health check failed:', error)
    }
  }

  const handleDataGenerated = async () => {
    setDataLoaded(true)
    setLoading(true)
    try {
      const fullAnalysis = await api.getFullAnalysis()
      setAnalysis(fullAnalysis)
      setActiveTab('scores')
    } catch (error) {
      console.error('Failed to load analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'generate', label: 'Generate Data', icon: Activity },
    { id: 'scores', label: 'Proxy Scores', icon: TrendingUp, disabled: !dataLoaded },
    { id: 'fragility', label: 'Fragility', icon: AlertTriangle, disabled: !dataLoaded },
    { id: 'decisions', label: 'Decisions', icon: Target, disabled: !dataLoaded },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <BarChart3 className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">PROXIMA</h1>
                <p className="text-sm text-slate-400">Proxy Metric Intelligence</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                dataLoaded 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                  : 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
              }`}>
                {dataLoaded ? '● Data Loaded' : '○ No Data'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="flex space-x-2 border-b border-slate-700">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => !tab.disabled && setActiveTab(tab.id)}
                disabled={tab.disabled}
                className={`flex items-center space-x-2 px-4 py-3 font-medium text-sm transition-all ${
                  activeTab === tab.id
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : tab.disabled
                    ? 'text-slate-600 cursor-not-allowed'
                    : 'text-slate-400 hover:text-slate-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          </div>
        ) : (
          <>
            {activeTab === 'generate' && (
              <DataGenerator onDataGenerated={handleDataGenerated} />
            )}
            {activeTab === 'scores' && analysis && (
              <ProxyScores scores={analysis.proxy_scores} summary={analysis.data_summary} />
            )}
            {activeTab === 'fragility' && analysis && (
              <FragilityAnalysis 
                segments={analysis.fragile_segments} 
                topMetric={analysis.data_summary.top_fragile_metric}
              />
            )}
            {activeTab === 'decisions' && analysis && (
              <DecisionSimulation results={analysis.decision_results} />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-700 bg-slate-800/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-slate-400">
            PROXIMA v0.1.0 - Proxy Metric Intelligence for Online Experiments
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App

