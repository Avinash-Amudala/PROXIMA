import { useState } from 'react'
import { Play, Settings } from 'lucide-react'
import { api } from '../api/client'

export default function DataGenerator({ onDataGenerated }) {
  const [params, setParams] = useState({
    n_users: 250000,
    n_experiments: 50,
    seed: 7
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.generateData(params)
      setResult(response)
      onDataGenerated()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate data')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center space-x-3 mb-6">
          <Settings className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-bold text-white">Generate Synthetic Data</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Number of Users
            </label>
            <input
              type="number"
              value={params.n_users}
              onChange={(e) => setParams({ ...params, n_users: parseInt(e.target.value) })}
              className="input w-full"
              min="1000"
              max="1000000"
            />
            <p className="text-xs text-slate-500 mt-1">Range: 1,000 - 1,000,000</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Number of Experiments
            </label>
            <input
              type="number"
              value={params.n_experiments}
              onChange={(e) => setParams({ ...params, n_experiments: parseInt(e.target.value) })}
              className="input w-full"
              min="5"
              max="200"
            />
            <p className="text-xs text-slate-500 mt-1">Range: 5 - 200</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Random Seed
            </label>
            <input
              type="number"
              value={params.seed}
              onChange={(e) => setParams({ ...params, seed: parseInt(e.target.value) })}
              className="input w-full"
              min="0"
            />
            <p className="text-xs text-slate-500 mt-1">For reproducibility</p>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="btn-primary w-full md:w-auto flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Generate Data & Run Analysis</span>
            </>
          )}
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
      </div>

      {result && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Generation Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-700/30 rounded-lg p-4">
              <p className="text-sm text-slate-400">Total Users</p>
              <p className="text-2xl font-bold text-white mt-1">
                {result.summary.n_users.toLocaleString()}
              </p>
            </div>
            <div className="bg-slate-700/30 rounded-lg p-4">
              <p className="text-sm text-slate-400">Experiments</p>
              <p className="text-2xl font-bold text-white mt-1">
                {result.summary.n_experiments}
              </p>
            </div>
            <div className="bg-slate-700/30 rounded-lg p-4">
              <p className="text-sm text-slate-400">Failure Cohort</p>
              <p className="text-2xl font-bold text-white mt-1">
                {result.summary.n_failure_cohort.toLocaleString()}
              </p>
            </div>
            <div className="bg-slate-700/30 rounded-lg p-4">
              <p className="text-sm text-slate-400">Failure Rate</p>
              <p className="text-2xl font-bold text-white mt-1">
                {(result.summary.failure_cohort_rate * 100).toFixed(1)}%
              </p>
            </div>
          </div>
          <div className="mt-4 p-3 bg-green-500/20 border border-green-500/30 rounded-lg">
            <p className="text-green-400 text-sm">
              ✓ {result.message}. Proceed to the next tabs to view analysis results.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

