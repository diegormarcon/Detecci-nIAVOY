import React from 'react'

function StatsCard({ title, value, color }) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    red: 'bg-red-500'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`${colorClasses[color]} w-12 h-12 rounded-lg flex items-center justify-center text-white text-2xl font-bold mr-4`}>
          {value}
        </div>
        <div>
          <h3 className="text-gray-600 text-sm font-medium">{title}</h3>
        </div>
      </div>
    </div>
  )
}

export default StatsCard

