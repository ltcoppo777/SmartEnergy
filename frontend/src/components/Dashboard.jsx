import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { getAnalysis } from '../utils/api'

const StatCard = ({ title, value, subtitle, icon, color }) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className={`bg-white rounded-2xl p-6 shadow-lg border-l-4 ${color}`}
  >
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      </div>
      <div className="text-3xl">{icon}</div>
    </div>
  </motion.div>
)

const Dashboard = ({ refreshTrigger }) => {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalysis()
  }, [])

  useEffect(() => {
    if (refreshTrigger) {
      fetchAnalysis()
    }
  }, [refreshTrigger])

  const fetchAnalysis = async () => {
    try {
      const response = await getAnalysis()
      setAnalysis(response.data)
    } catch (error) {
      console.error('Error fetching analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Energy Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Power"
          value={`${analysis?.summary?.total_power_kw || 0} kW`}
          subtitle="Connected appliances"
          icon="⚡"
          color="border-energy-blue"
        />
        
        <StatCard
          title="Daily Usage"
          value={`${analysis?.summary?.estimated_daily_usage_kwh || 0} kWh`}
          subtitle="Estimated consumption"
          icon="📊"
          color="border-energy-green"
        />
        
        <StatCard
          title="Daily Cost"
          value={`$${analysis?.summary?.estimated_daily_cost?.toFixed(2) || 0}`}
          subtitle="At current rates"
          icon="💰"
          color="border-energy-orange"
        />
        
        <StatCard
          title="Avg Price"
          value={`$${analysis?.summary?.average_price_per_kwh?.toFixed(4) || 0}`}
          subtitle="Per kWh"
          icon="🏷️"
          color="border-energy-red"
        />
      </div>

      {/* Appliance Breakdown */}
      {analysis?.appliance_breakdown && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Appliance Breakdown</h3>
          <div className="space-y-3">
            {analysis.appliance_breakdown.map((appliance, index) => (
              <motion.div
                key={appliance.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              >
                <span className="font-medium text-gray-700">{appliance.name}</span>
                <div className="text-right">
                  <span className="text-sm text-gray-600">
                    {appliance.power} kW × {appliance.duration}h
                  </span>
                  <span className="block text-sm font-semibold text-energy-orange">
                    ${appliance.estimated_cost.toFixed(3)}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard