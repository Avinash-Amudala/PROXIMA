import { Target, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

export default function DecisionSimulation({ results }) {
  const chartData = results.map(r => ({
    metric: r.proxy_metric,
    win_rate: r.win_rate * 100,
    false_positive: r.false_positive_rate * 100,
    false_negative: r.false_negative_rate * 100,
    regret: r.avg_regret
  }))

  const bestProxy = results[0]
  const oracle = results.find(r => r.proxy_metric.includes('Oracle'))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card bg-purple-500/10 border-purple-500/30">
        <div className="flex items-center space-x-3 mb-3">
          <Target className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-bold text-white">Decision Simulation</h2>
        </div>
        <p className="text-slate-300 text-sm">
          Simulates shipping decisions based on each proxy metric and evaluates performance 
          against true long-term outcomes.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <p className="text-sm text-slate-400">Best Win Rate</p>
          </div>
          <p className="text-2xl font-bold text-white">{(bestProxy.win_rate * 100).toFixed(1)}%</p>
          <p className="text-xs text-slate-400 mt-1">{bestProxy.proxy_metric}</p>
        </div>

        <div className="card">
          <div className="flex items-center space-x-2 mb-2">
            <Target className="w-5 h-5 text-blue-400" />
            <p className="text-sm text-slate-400">Correct Ships</p>
          </div>
          <p className="text-2xl font-bold text-white">{bestProxy.correct_ships}</p>
          <p className="text-xs text-slate-400 mt-1">of {bestProxy.total_shipped} shipped</p>
        </div>

        <div className="card">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingDown className="w-5 h-5 text-red-400" />
            <p className="text-sm text-slate-400">Incorrect Ships</p>
          </div>
          <p className="text-2xl font-bold text-white">{bestProxy.incorrect_ships}</p>
          <p className="text-xs text-slate-400 mt-1">false positives</p>
        </div>

        <div className="card">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-5 h-5 text-orange-400" />
            <p className="text-sm text-slate-400">Missed Opportunities</p>
          </div>
          <p className="text-2xl font-bold text-white">{bestProxy.missed_opportunities}</p>
          <p className="text-xs text-slate-400 mt-1">false negatives</p>
        </div>
      </div>

      {/* Win Rate Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Win Rate Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="metric" stroke="#9ca3af" angle={-45} textAnchor="end" height={100} />
            <YAxis stroke="#9ca3af" label={{ value: 'Win Rate (%)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Bar dataKey="win_rate" name="Win Rate (%)" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Error Rates Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Error Rates</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="metric" stroke="#9ca3af" angle={-45} textAnchor="end" height={100} />
            <YAxis stroke="#9ca3af" label={{ value: 'Rate (%)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Legend />
            <Bar dataKey="false_positive" name="False Positive (%)" fill="#ef4444" />
            <Bar dataKey="false_negative" name="False Negative (%)" fill="#f59e0b" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Results Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Detailed Decision Results</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Proxy Metric</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Win Rate</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Avg Regret</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Correct</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Incorrect</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Missed</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">FP Rate</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">FN Rate</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr 
                  key={result.proxy_metric} 
                  className={`border-b border-slate-700/50 hover:bg-slate-700/30 ${
                    result.proxy_metric.includes('Oracle') ? 'bg-blue-500/10' : ''
                  }`}
                >
                  <td className="py-3 px-4">
                    <span className={`font-medium ${
                      result.proxy_metric.includes('Oracle') ? 'text-blue-400' : 'text-white'
                    }`}>
                      {result.proxy_metric}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`font-semibold ${
                      result.win_rate >= 0.7 ? 'text-green-400' : 
                      result.win_rate >= 0.5 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {(result.win_rate * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-slate-300">{result.avg_regret.toFixed(4)}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-green-400">{result.correct_ships}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-red-400">{result.incorrect_ships}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-orange-400">{result.missed_opportunities}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-slate-300">{(result.false_positive_rate * 100).toFixed(1)}%</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-slate-300">{(result.false_negative_rate * 100).toFixed(1)}%</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Insights */}
      <div className="card bg-blue-500/10 border-blue-500/30">
        <h3 className="text-lg font-semibold text-blue-400 mb-3">Decision Insights</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li className="flex items-start space-x-2">
            <span className="text-green-400 mt-0.5">✓</span>
            <span>
              <strong className="text-white">{bestProxy.proxy_metric}</strong> achieves the best win rate 
              of {(bestProxy.win_rate * 100).toFixed(1)}%, correctly predicting {bestProxy.correct_ships} out 
              of {bestProxy.total_shipped} shipping decisions.
            </span>
          </li>
          {oracle && (
            <li className="flex items-start space-x-2">
              <span className="text-blue-400 mt-0.5">ℹ</span>
              <span>
                Oracle (using true long-term metric) achieves {(oracle.win_rate * 100).toFixed(1)}% win rate, 
                representing the theoretical maximum.
              </span>
            </li>
          )}
          <li className="flex items-start space-x-2">
            <span className="text-yellow-400 mt-0.5">⚠</span>
            <span>
              Average regret of {bestProxy.avg_regret.toFixed(4)} indicates the opportunity cost of using 
              the proxy instead of waiting for true long-term metrics.
            </span>
          </li>
        </ul>
      </div>
    </div>
  )
}

