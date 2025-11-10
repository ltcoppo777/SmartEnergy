import React from 'react'

const HourToggleBar = ({ 
  selectedHours = [], 
  onToggle, 
  label = 'Hours',
  activeColor = 'bg-blue-500',
  inactiveColor = 'bg-gray-200'
}) => {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-xs text-gray-500">
          ({selectedHours.length}/24)
        </span>
      </div>
      <div className="flex flex-wrap gap-1">
        {Array.from({ length: 24 }, (_, i) => (
          <button
            key={i}
            onClick={() => onToggle(i)}
            className={`px-2 py-1 text-xs font-medium rounded transition-all ${
              selectedHours.includes(i)
                ? `${activeColor} text-white`
                : `${inactiveColor} text-gray-700 hover:opacity-80`
            }`}
            title={`${i}:00`}
          >
            {i}
          </button>
        ))}
      </div>
      {selectedHours.length > 0 && (
        <p className="text-xs text-gray-600">
          Selected: {selectedHours.sort((a, b) => a - b).join(', ')}
        </p>
      )}
    </div>
  )
}

export default HourToggleBar
