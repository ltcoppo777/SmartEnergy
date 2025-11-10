import React from 'react'
import { motion } from 'framer-motion'
import PreferencesForm from '../components/PreferencesForm'

const Settings = () => {
  return (
    <div className="min-h-screen p-4 md:p-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl mx-auto"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-2">
            Settings
          </h1>
          <p className="text-lg text-gray-600">
            Manage your preferences and optimize your energy schedule
          </p>
        </div>

        {/* Settings Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <PreferencesForm />
        </motion.div>
      </motion.div>
    </div>
  )
}

export default Settings
