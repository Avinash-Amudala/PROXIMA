import { TrendingUp, Award, AlertCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

export default function ProxyScores({ scores, summary }) {
  const getReliabilityColor = (reliability) => {
    if (reliability >= 0.7) return '#10b981' // green
    if (reliability >= 0.5) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  const getReliabilityBadge = (reliability) => {
    if (reliability >= 0.7) return 'badge-success'
    if (reliability >= 0.5) return 'badge-warning'
    return 'badge-danger'
  }

  const chartData = scores.map(score => ({
    metric: score.metric,
    reliability: score.reliability,
    effect_corr: score.effect_corr,
    directional_accuracy: score.directional_accuracy,
    fragility_rate: score.fragility_rate
  }))

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center space-x-3">
            <Award className="w-8 h-8 text-yellow-400" />
            <div>
              <p className="text-sm text-slate-400">Best Proxy</p>
              <p className="text-xl font-bold text-white">{summary.best_proxy}</p>
              <p className="text-sm text-green-400">
                Reliability: {(summary.best_reliability * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-sm text-slate-400">Experiments Analyzed</p>
              <p className="text-xl font-bold text-white">{summary.n_experiments}</p>
              <p className="text-sm text-slate-400">
                {summary.n_users.toLocaleString()} users
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-8 h-8 text-orange-400" />
            <div>
              <p className="text-sm text-slate-400">Failure Cohort</p>
              <p className="text-xl font-bold text-white">
                {(summary.failure_cohort_rate * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-slate-400">
                {summary.n_failure_cohort.toLocaleString()} users
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Reliability Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Proxy Reliability Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis type="number" domain={[0, 1]} stroke="#9ca3af" />
            <YAxis dataKey="metric" type="category" stroke="#9ca3af" width={150} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Bar dataKey="reliability" name="Reliability Score">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getReliabilityColor(entry.reliability)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Scores Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Detailed Proxy Metrics</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Rank</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Metric</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Reliability</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Effect Corr</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Dir. Accuracy</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Fragility Rate</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-300">Experiments</th>
              </tr>
            </thead>
            <tbody>
              {scores.map((score, index) => (
                <tr key={score.metric} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4">
                    <span className="text-slate-400 font-medium">#{index + 1}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-white font-medium">{score.metric}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`badge ${getReliabilityBadge(score.reliability)}`}>
                      {(score.reliability * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-slate-300">{score.effect_corr.toFixed(3)}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-slate-300">{(score.directional_accuracy * 100).toFixed(1)}%</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={score.fragility_rate > 0.3 ? 'text-red-400' : 'text-green-400'}>
                      {(score.fragility_rate * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-slate-400">{score.n_experiments_scored}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recommendations */}
      <div className="card bg-blue-500/10 border-blue-500/30">
        <h3 className="text-lg font-semibold text-blue-400 mb-3">Recommendations</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li className="flex items-start space-x-2">
            <span className="text-green-400 mt-0.5">✓</span>
            <span><strong className="text-white">{scores[0].metric}</strong> is the most reliable proxy with {(scores[0].reliability * 100).toFixed(1)}% reliability score.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-yellow-400 mt-0.5">⚠</span>
            <span>Monitor <strong className="text-white">{scores[scores.length - 1].metric}</strong> carefully - it has the lowest reliability at {(scores[scores.length - 1].reliability * 100).toFixed(1)}%.</span>
          </li>
          {scores.filter(s => s.fragility_rate > 0.3).length > 0 && (
            <li className="flex items-start space-x-2">
              <span className="text-red-400 mt-0.5">!</span>
              <span>{scores.filter(s => s.fragility_rate > 0.3).length} metric(s) show high fragility (>30% sign flip rate) - check segment-level analysis.</span>
            </li>
          )}
        </ul>
      </div>
    </div>
  )
}

