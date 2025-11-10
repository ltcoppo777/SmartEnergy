import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const PriceHistory = () => {
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPriceHistory()
  }, [])

  const fetchPriceHistory = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/price-history`)
      const data = response.data
      
      if (data.history && data.history.length > 0) {
        setHistory(data.history)
        setStats({
          min: data.min_price,
          max: data.max_price,
          avg: data.avg_price
        })
      }
    } catch (error) {
      console.error('Error fetching price history:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <motion.div className="bg-white rounded-2xl p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl p-6 shadow-lg"
    >
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Price History</h2>

      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white">
            <p className="text-sm font-medium text-green-100">Min Price</p>
            <p className="text-2xl font-bold">${stats.min.toFixed(4)}</p>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white">
            <p className="text-sm font-medium text-blue-100">Avg Price</p>
            <p className="text-2xl font-bold">${stats.avg.toFixed(4)}</p>
          </div>
          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-4 text-white">
            <p className="text-sm font-medium text-red-100">Max Price</p>
            <p className="text-2xl font-bold">${stats.max.toFixed(4)}</p>
          </div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 px-4 font-semibold text-gray-700">Time</th>
              <th className="text-right py-2 px-4 font-semibold text-gray-700">Price ($/kWh)</th>
              <th className="text-center py-2 px-4 font-semibold text-gray-700">Relative</th>
            </tr>
          </thead>
          <tbody>
            {history.slice(0, 24).map((price, index) => {
              const percentage =
                stats && stats.max > stats.min
                  ? ((price.price - stats.min) / (stats.max - stats.min)) * 100
                  : 50

              const bgColor =
                percentage < 33
                  ? 'bg-green-100'
                  : percentage > 66
                  ? 'bg-red-100'
                  : 'bg-yellow-100'

              return (
                <motion.tr
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className={`border-b border-gray-100 hover:${bgColor}`}
                >
                  <td className="py-2 px-4 text-gray-600">{price.time}</td>
                  <td className="py-2 px-4 text-right font-semibold text-gray-800">
                    ${price.price.toFixed(4)}
                  </td>
                  <td className="py-2 px-4 text-center">
                    <div className="flex justify-center">
                      <div className="relative w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${
                            percentage < 33
                              ? 'bg-green-500'
                              : percentage > 66
                              ? 'bg-red-500'
                              : 'bg-yellow-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                </motion.tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={fetchPriceHistory}
        className="w-full mt-4 bg-blue-500 text-white py-2 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
      >
        Refresh History
      </motion.button>
    </motion.div>
  )
}

export default PriceHistory
