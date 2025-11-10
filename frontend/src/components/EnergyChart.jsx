import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'
import { getLivePrices } from '../utils/api'

const EnergyChart = () => {
  const [priceData, setPriceData] = useState([])
  const [timeRange, setTimeRange] = useState('24h')

  useEffect(() => {
    fetchPriceData()
  }, [timeRange])

  const fetchPriceData = async () => {
    try {
      const response = await getLivePrices()
      const prices = response.data.prices.map((price, index) => ({
        time: response.data.times[index],
        price: price,
        hour: index
      }))
      setPriceData(prices)
    } catch (error) {
      console.error('Error fetching price data:', error)
      // Fallback sample data
      const sampleData = Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        price: 0.05 + Math.random() * 0.1,
        hour: i
      }))
      setPriceData(sampleData)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl p-6 shadow-lg"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Energy Prices</h2>
        <div className="flex space-x-2">
          {['24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={priceData}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              interval={3}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `$${value.toFixed(3)}`}
            />
            <Tooltip 
              formatter={(value) => [`$${Number(value).toFixed(4)}`, 'Price']}
              labelFormatter={(label) => `Time: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#0ea5e9"
              fill="url(#colorPrice)"
              strokeWidth={2}
            />
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
              </linearGradient>
            </defs>
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-sm text-gray-600">Min Price</p>
          <p className="text-lg font-semibold text-energy-green">
            ${Math.min(...priceData.map(d => d.price)).toFixed(4)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Avg Price</p>
          <p className="text-lg font-semibold text-gray-700">
            ${(priceData.reduce((a, b) => a + b.price, 0) / priceData.length || 0).toFixed(4)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Max Price</p>
          <p className="text-lg font-semibold text-energy-red">
            ${Math.max(...priceData.map(d => d.price)).toFixed(4)}
          </p>
        </div>
      </div>
    </motion.div>
  )
}

export default EnergyChart