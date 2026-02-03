import { AlertTriangle, MapPin, Smartphone, Users } from 'lucide-react'

export default function FragilityAnalysis({ segments, topMetric }) {
  const getFragilityLevel = (rate) => {
    if (rate >= 0.5) return { label: 'Critical', color: 'text-red-400', bg: 'bg-red-500/20', border: 'border-red-500/30' }
    if (rate >= 0.3) return { label: 'High', color: 'text-orange-400', bg: 'bg-orange-500/20', border: 'border-orange-500/30' }
    if (rate >= 0.15) return { label: 'Medium', color: 'text-yellow-400', bg: 'bg-yellow-500/20', border: 'border-yellow-500/30' }
    return { label: 'Low', color: 'text-green-400', bg: 'bg-green-500/20', border: 'border-green-500/30' }
  }

  const getSegmentIcon = (segment) => {
    if (segment.region) return <MapPin className="w-4 h-4" />
    if (segment.device) return <Smartphone className="w-4 h-4" />
    if (segment.tenure) return <Users className="w-4 h-4" />
    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card bg-orange-500/10 border-orange-500/30">
        <div className="flex items-center space-x-3 mb-3">
          <AlertTriangle className="w-6 h-6 text-orange-400" />
          <h2 className="text-xl font-bold text-white">Fragility Analysis</h2>
        </div>
        <p className="text-slate-300 text-sm">
          Segments where <strong className="text-white">{topMetric}</strong> proxy shows sign flips 
          (proxy suggests opposite direction from true long-term effect).
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <p className="text-sm text-slate-400">Total Segments Analyzed</p>
          <p className="text-3xl font-bold text-white mt-2">{segments.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-400">Critical Segments</p>
          <p className="text-3xl font-bold text-red-400 mt-2">
            {segments.filter(s => s.flip_rate >= 0.5).length}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-400">High Risk Segments</p>
          <p className="text-3xl font-bold text-orange-400 mt-2">
            {segments.filter(s => s.flip_rate >= 0.3 && s.flip_rate < 0.5).length}
          </p>
        </div>
      </div>

      {/* Fragile Segments List */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Most Fragile Segments</h3>
        <div className="space-y-3">
          {segments.map((segment, index) => {
            const fragility = getFragilityLevel(segment.flip_rate)
            return (
              <div 
                key={index}
                className={`p-4 rounded-lg border ${fragility.bg} ${fragility.border}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg font-semibold text-white">
                        #{index + 1}
                      </span>
                      <div className="flex items-center space-x-2 text-sm">
                        {segment.region && (
                          <span className="flex items-center space-x-1 bg-slate-700/50 px-2 py-1 rounded">
                            <MapPin className="w-3 h-3" />
                            <span className="text-slate-300">{segment.region}</span>
                          </span>
                        )}
                        {segment.device && (
                          <span className="flex items-center space-x-1 bg-slate-700/50 px-2 py-1 rounded">
                            <Smartphone className="w-3 h-3" />
                            <span className="text-slate-300">{segment.device}</span>
                          </span>
                        )}
                        {segment.tenure && (
                          <span className="flex items-center space-x-1 bg-slate-700/50 px-2 py-1 rounded">
                            <Users className="w-3 h-3" />
                            <span className="text-slate-300">{segment.tenure}</span>
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 mt-3">
                      <div>
                        <p className="text-xs text-slate-400">Flip Rate</p>
                        <p className={`text-lg font-bold ${fragility.color}`}>
                          {(segment.flip_rate * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Experiment Cells</p>
                        <p className="text-lg font-semibold text-white">
                          {segment.n_cells}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Avg Cell Size</p>
                        <p className="text-lg font-semibold text-white">
                          {Math.round(segment.avg_cell_n).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className={`ml-4 px-3 py-1 rounded-full text-xs font-medium ${fragility.bg} ${fragility.color} border ${fragility.border}`}>
                    {fragility.label}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Warning Box */}
      {segments.filter(s => s.flip_rate >= 0.5).length > 0 && (
        <div className="card bg-red-500/10 border-red-500/30">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5" />
            <div>
              <h4 className="text-red-400 font-semibold mb-2">Critical Warning</h4>
              <p className="text-sm text-slate-300">
                {segments.filter(s => s.flip_rate >= 0.5).length} segment(s) show critical fragility 
                (≥50% sign flip rate). Using <strong className="text-white">{topMetric}</strong> as a 
                proxy for these segments may lead to incorrect decisions. Consider:
              </p>
              <ul className="mt-2 space-y-1 text-sm text-slate-300 ml-4">
                <li>• Using segment-specific proxies</li>
                <li>• Waiting for long-term metrics before shipping</li>
                <li>• Running longer experiments for these cohorts</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Insights */}
      <div className="card bg-blue-500/10 border-blue-500/30">
        <h3 className="text-lg font-semibold text-blue-400 mb-3">Key Insights</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 mt-0.5">→</span>
            <span>
              Fragility indicates segments where the proxy metric disagrees with the true long-term effect direction.
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 mt-0.5">→</span>
            <span>
              High flip rates suggest Simpson's paradox or proxy gaming in specific cohorts.
            </span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-400 mt-0.5">→</span>
            <span>
              Consider these segments when making shipping decisions based on early metrics.
            </span>
          </li>
        </ul>
      </div>
    </div>
  )
}

