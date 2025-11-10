import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { saveAppliances, getAppliances, getLivePrices } from '../utils/api'

const APPLIANCE_DEFAULTS = {
  "Washing Machine": 0.30,
  "Dryer": 2.50,
  "Dishwasher": 1.50,
  "Microwave": 0.20,
  "Oven": 2.30,
  "Toaster": 0.05,
  "Coffee Maker": 0.30,
  "Television": 0.10,
  "Computer": 0.10,
  "Air Conditioner": 3.50,
  "Heater": 1.50,
  "Vacuum Cleaner": 0.75,
  "Iron": 1.10,
  "Lighting": 0.02
}

const ApplianceInput = ({ onAppliancesSaved }) => {
  const [appliances, setAppliances] = useState([])
  const [form, setForm] = useState({
    appliance_name: '',
    duration_hours: 1
  })
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [prices, setPrices] = useState(null)

  useEffect(() => {
    loadAppliances()
    fetchPrices()
  }, [])

  const loadAppliances = async () => {
    try {
      setLoading(true)
      const response = await getAppliances()
      setAppliances(response.data || [])
    } catch (error) {
      console.error('Error loading appliances:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPrices = async () => {
    try {
      const response = await getLivePrices()
      setPrices(response.data)
    } catch (error) {
      console.error('Error fetching prices:', error)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({
      ...prev,
      [name]: name === 'appliance_name' ? value : parseFloat(value) || value
    }))
  }

  const handleAddAppliance = () => {
    if (!form.appliance_name || !form.duration_hours || form.duration_hours <= 0) {
      setMessage({ type: 'error', text: 'Please select an appliance and duration' })
      return
    }

    const currentHour = new Date().getHours()
    const power_kw = APPLIANCE_DEFAULTS[form.appliance_name]

    const newAppliance = {
      appliance_name: form.appliance_name,
      power_kw: power_kw,
      start_time: currentHour,
      duration_hours: form.duration_hours
    }

    setAppliances(prev => [...prev, newAppliance])
    setForm({
      appliance_name: '',
      duration_hours: 1
    })
    setMessage({ type: 'success', text: 'Appliance added!' })
    setTimeout(() => setMessage({ type: '', text: '' }), 2000)
  }

  const handleRemoveAppliance = (index) => {
    setAppliances(prev => prev.filter((_, i) => i !== index))
  }

  const handleSaveAppliances = async () => {
    if (appliances.length === 0) {
      setMessage({ type: 'error', text: 'Please add at least one appliance' })
      return
    }

    setSaving(true)
    setMessage({ type: '', text: '' })
    try {
      await saveAppliances(appliances)
      setMessage({ type: 'success', text: 'Appliances saved successfully! Analysis updated above.' })
      if (onAppliancesSaved) {
        onAppliancesSaved()
      }
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      console.error('Error saving appliances:', error)
      setMessage({ type: 'error', text: 'Failed to save appliances' })
    } finally {
      setSaving(false)
    }
  }



  if (loading) {
    return (
      <motion.div className="bg-white rounded-2xl p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
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
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Appliance Usage Input</h2>

      {message.text && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mb-4 p-3 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {message.text}
        </motion.div>
      )}

      <div className="space-y-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Appliance
            </label>
            <select
              name="appliance_name"
              value={form.appliance_name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Select Appliance --</option>
              {Object.keys(APPLIANCE_DEFAULTS).map(name => (
                <option key={name} value={name}>
                  {name} ({APPLIANCE_DEFAULTS[name]}kW)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duration (hours)
            </label>
            <input
              type="number"
              name="duration_hours"
              value={form.duration_hours}
              onChange={handleInputChange}
              placeholder="e.g., 2"
              step="0.5"
              min="0.5"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleAddAppliance}
          className="w-full bg-blue-500 text-white py-2 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
        >
          Add Appliance
        </motion.button>
      </div>

      {appliances.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">Added Appliances</h3>
          <div className="space-y-2">
            {appliances.map((appliance, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex-1">
                  <p className="font-semibold text-gray-700">{appliance.appliance_name}</p>
                  <p className="text-sm text-gray-600">
                    {appliance.power_kw} kW × {appliance.duration_hours}h at {appliance.start_time}:00
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleRemoveAppliance(index)}
                  className="ml-4 px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                >
                  Remove
                </motion.button>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleSaveAppliances}
        disabled={saving || appliances.length === 0}
        className="w-full bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {saving ? 'Saving...' : `Save ${appliances.length} Appliance${appliances.length !== 1 ? 's' : ''}`}
      </motion.button>
    </motion.div>
  )
}

export default ApplianceInput
