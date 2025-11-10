import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { getPreferences, calculateComfort } from '../utils/api'
import HourToggleBar from './HourToggleBar'

const PreferencesForm = () => {
  const [preferences, setPreferences] = useState({
    avoid_hours: [],
    priority_appliances: []
  })
  const [training, setTraining] = useState(false)
  const [trainingProgress, setTrainingProgress] = useState('')
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [comfortLevel, setComfortLevel] = useState(5.0)
  const [advice, setAdvice] = useState('')
  const [adviceType, setAdviceType] = useState('')
  const [calculatingComfort, setCalculatingComfort] = useState(false)
  const debounceTimer = useRef(null)
  const trainingCheckTimer = useRef(null)

  useEffect(() => {
    loadPreferences()
    
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
      if (trainingCheckTimer.current) clearTimeout(trainingCheckTimer.current)
    }
  }, [])

  const loadPreferences = async () => {
    try {
      setLoading(true)
      const response = await getPreferences()
      setPreferences({
        avoid_hours: response.data?.avoid_hours || [],
        priority_appliances: response.data?.priority_appliances || []
      })
      setComfortLevel(response.data?.comfort_level || 5.0)
    } catch (error) {
      console.error('Error loading preferences:', error)
      setMessage({ type: 'error', text: 'Failed to load preferences' })
    } finally {
      setLoading(false)
    }
  }

  const updateComfortLevel = async (avoidHours) => {
    try {
      setCalculatingComfort(true)
      const response = await calculateComfort(avoidHours)
      setComfortLevel(response.data?.comfort_level || 5.0)
      setAdvice(response.data?.advice || '')
    } catch (error) {
      console.error('Error calculating comfort level:', error)
    } finally {
      setCalculatingComfort(false)
    }
  }

  const debouncedComfortCalculation = (avoidHours) => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }
    debounceTimer.current = setTimeout(() => {
      updateComfortLevel(avoidHours)
    }, 500)
  }



  const handleTrainAgent = async () => {
    setTraining(true)
    setTrainingProgress('Initializing...')
    setMessage({ type: '', text: '' })
    setAdvice('')
    setAdviceType('')

    try {
      const mockPrices = Array(24).fill(0).map((_, i) => {
        return Math.sin(i / 24 * Math.PI * 2) * 0.5 + 0.5
      })

      const response = await fetch('http://localhost:8000/api/train-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prices: mockPrices,
          appliances: [
            { name: 'Washing Machine', duration: 2, power: 2000 },
            { name: 'Dryer', duration: 3, power: 5000 },
            { name: 'Dishwasher', duration: 2.5, power: 1800 }
          ],
          avoid_hours: preferences.avoid_hours,
          preferences: {}
        })
      })

      if (!response.ok) {
        throw new Error('Failed to start training')
      }

      setTrainingProgress('Training in progress... This may take a minute')
      setMessage({ type: 'info', text: 'Training RL agent with your preferences...' })

      const checkStatus = async () => {
        try {
          const statusResponse = await fetch('http://localhost:8000/api/training-status')
          const status = await statusResponse.json()

          if (status.is_training) {
            setTrainingProgress(status.progress)
            trainingCheckTimer.current = setTimeout(checkStatus, 2000)
          } else {
            setTraining(false)
            setTrainingProgress('')
            setAdviceType('rl')
            setAdvice('Agent training completed! The optimized schedule respects your avoid and preferred hours while maximizing cost savings.')
            setMessage({ type: 'success', text: 'Agent training completed with RL optimization!' })
            setTimeout(() => setMessage({ type: '', text: '' }), 4000)
          }
        } catch (error) {
          console.error('Error checking training status:', error)
        }
      }

      trainingCheckTimer.current = setTimeout(checkStatus, 2000)
    } catch (error) {
      console.error('Error starting training:', error)
      setMessage({ type: 'error', text: 'Failed to start agent training' })
      setTraining(false)
      setTrainingProgress('')
    }
  }

  const toggleAvoidHour = (hour) => {
    const updatedHours = preferences.avoid_hours.includes(hour)
      ? preferences.avoid_hours.filter(h => h !== hour)
      : [...preferences.avoid_hours, hour]
    
    setPreferences(prev => ({
      ...prev,
      avoid_hours: updatedHours
    }))

    debouncedComfortCalculation(updatedHours)
  }



  if (loading) {
    return (
      <motion.div
        className="bg-white rounded-2xl p-6 shadow-lg"
      >
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-12 bg-gray-200 rounded"></div>
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
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Energy Optimization Preferences</h2>

      {message.text && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mb-4 p-3 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-100 text-green-800'
              : message.type === 'info'
              ? 'bg-blue-100 text-blue-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {message.text}
        </motion.div>
      )}

      <div className="space-y-6">
        {/* Comfort Level */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">📊 Your Comfort Score</h3>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Comfort Level</span>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold text-indigo-600">{comfortLevel.toFixed(1)}</span>
              <span className="text-sm text-gray-600">/10</span>
            </div>
          </div>
          <p className="text-xs text-gray-600">
            {calculatingComfort ? 'Calculating...' : 'Based on your avoid hours and electricity pricing'}
          </p>
        </div>

        {/* Avoid Hours */}
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <HourToggleBar
            selectedHours={preferences.avoid_hours}
            onToggle={toggleAvoidHour}
            label="⏰ Hours to Avoid"
            activeColor="bg-red-500"
          />
        </div>

        {/* Buttons Container */}
        <div className="grid grid-cols-1 gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleTrainAgent}
            disabled={training}
            className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white py-3 rounded-lg font-semibold disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
          >
            {training ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Training...
              </>
            ) : (
              <>🤖 Train Agent</>
            )}
          </motion.button>
        </div>

        {/* Training Progress */}
        {trainingProgress && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-purple-50 border border-purple-200 rounded-lg p-3"
          >
            <p className="text-sm text-purple-700 font-medium">{trainingProgress}</p>
          </motion.div>
        )}

        {/* Optimization Advice Box */}
        {advice && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`rounded-lg p-4 border ${
              adviceType === 'lp'
                ? 'bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200'
                : 'bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200'
            }`}
          >
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="mr-2">
                {adviceType === 'lp' ? '📊 Linear Programming Advice' : '🤖 RL Agent Optimization'}
              </span>
            </h3>
            <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
              {advice}
            </div>
          </motion.div>
        )}

        {/* Quick Presets */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Quick Presets</h4>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: '🌙 Night Sleeper', avoid: [22, 23, 0, 1, 2, 3, 4, 5, 6] },
              { label: '🌅 Early Bird', avoid: [20, 21, 22, 23] },
              { label: '🦉 Night Owl', avoid: [6, 7, 8, 9, 10, 11] },
              { label: '💼 9-to-5', avoid: [0, 1, 2, 3, 4, 5, 6, 7, 21, 22, 23] }
            ].map((preset) => (
              <button
                key={preset.label}
                onClick={() => {
                  setPreferences(prev => ({
                    ...prev,
                    avoid_hours: preset.avoid
                  }))
                  debouncedComfortCalculation(preset.avoid)
                }}
                className="p-2 bg-gray-100 rounded-lg text-sm hover:bg-gray-200 transition-colors"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default PreferencesForm
