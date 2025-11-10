import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { getLivePrices } from '../utils/api'

const LivePriceCard = () => {
  const [currentPrice, setCurrentPrice] = useState(null)
  const [avgPrice, setAvgPrice] = useState(null)
  const [minPrice, setMinPrice] = useState(null)
  const [maxPrice, setMaxPrice] = useState(null)
  const [trend, setTrend] = useState('stable')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCurrentPrice()
    const interval = setInterval(fetchCurrentPrice, 300000) // Update every 5 minutes
    return () => clearInterval(interval)
  }, [])

  const fetchCurrentPrice = async () => {
    try {
      setLoading(true)
      const response = await getLivePrices()
      const data = response.data
      
      if (data.prices && data.prices.length > 0) {
        const latest = data.prices[data.prices.length - 1]
        const previous = data.prices.length > 1 ? data.prices[data.prices.length - 2] : latest
        
        setCurrentPrice(latest)
        setAvgPrice(data.avg_price)
        setMinPrice(data.min_price)
        setMaxPrice(data.max_price)
        setTrend(latest > previous ? 'up' : latest < previous ? 'down' : 'stable')
      }
    } catch (error) {
      console.error('Error fetching current price:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-energy-red'
      case 'down': return 'text-energy-green'
      default: return 'text-gray-600'
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗️'
      case 'down': return '↘️'
      default: return '→'
    }
  }

  if (loading && !currentPrice) {
    return (
      <motion.div
        className="bg-gradient-to-br from-blue-500 to-green-500 rounded-2xl p-6 text-white shadow-lg"
      >
        <div className="animate-pulse">
          <div className="h-4 bg-white/20 rounded w-1/3 mb-4"></div>
          <div className="h-12 bg-white/20 rounded mb-4"></div>
          <div className="space-y-2">
            <div className="h-3 bg-white/20 rounded"></div>
            <div className="h-3 bg-white/20 rounded"></div>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-gradient-to-br from-blue-500 to-green-500 rounded-2xl p-6 text-white shadow-lg"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Live Electricity Price</h3>
        <div className={`text-sm font-medium ${getTrendColor()}`}>
          {getTrendIcon()} {trend}
        </div>
      </div>
      
      <div className="text-center mb-4">
        <div className="text-4xl font-bold mb-1">
          ${currentPrice ? currentPrice.toFixed(4) : '0.0000'}
        </div>
        <p className="text-blue-100 text-sm">per kWh</p>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-4 bg-white/10 rounded-lg p-3">
        <div className="text-center">
          <p className="text-xs text-blue-100">Min</p>
          <p className="font-semibold">${minPrice ? minPrice.toFixed(4) : '0.0000'}</p>
        </div>
        <div className="text-center border-l border-r border-white/20">
          <p className="text-xs text-blue-100">Avg</p>
          <p className="font-semibold">${avgPrice ? avgPrice.toFixed(4) : '0.0000'}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-blue-100">Max</p>
          <p className="font-semibold">${maxPrice ? maxPrice.toFixed(4) : '0.0000'}</p>
        </div>
      </div>

      <div className="mt-3 text-xs text-blue-100 space-y-1">
        <p>🕒 Updates every 5 minutes</p>
        <p>📊 Source: ComEd Real-time Pricing (Database Backed)</p>
      </div>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={fetchCurrentPrice}
        disabled={loading}
        className="w-full mt-4 bg-white text-blue-600 py-2 rounded-lg font-semibold hover:bg-blue-50 transition-colors disabled:opacity-50"
      >
        {loading ? 'Refreshing...' : 'Refresh Price'}
      </motion.button>
    </motion.div>
  )
}

export default LivePriceCard