import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

const Navigation = () => {
  const navigate = useNavigate()
  const [isSettingsHovered, setIsSettingsHovered] = useState(false)

  const handleLogout = () => {
    localStorage.clear()
    navigate('/')
    window.location.reload()
  }

  return (
    <motion.nav
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white shadow-lg sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-green-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">⚡</span>
            </div>
            <span className="text-lg font-bold text-gray-800 group-hover:text-blue-600 transition-colors">
              SmartEnergy
            </span>
          </Link>

          {/* Nav Items */}
          <div className="flex items-center gap-6">
            {/* Dashboard */}
            <Link to="/">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 rounded-lg text-gray-700 hover:bg-blue-100 hover:text-blue-600 transition-colors font-medium cursor-pointer"
              >
                Dashboard
              </motion.div>
            </Link>

            {/* AI Chatbot */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/chatbot')}
              className="px-4 py-2 rounded-lg text-gray-700 hover:bg-purple-100 hover:text-purple-600 transition-colors font-medium cursor-pointer"
            >
              AI Chatbot
            </motion.div>

            {/* Settings with Icon */}
            <motion.div
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onHoverStart={() => setIsSettingsHovered(true)}
              onHoverEnd={() => setIsSettingsHovered(false)}
              className="relative"
            >
              <Link to="/settings">
                <div className="p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                  <motion.div
                    animate={{ rotate: isSettingsHovered ? 30 : 0 }}
                    transition={{ duration: 0.3 }}
                    className="text-2xl"
                  >
                    ⚙️
                  </motion.div>
                </div>
              </Link>
            </motion.div>

            {/* Logout */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg bg-red-100 text-red-600 hover:bg-red-200 transition-colors font-medium"
            >
              Logout
            </motion.button>
          </div>
        </div>
      </div>
    </motion.nav>
  )
}

export default Navigation
