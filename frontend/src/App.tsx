function App() {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center text-gray-900 dark:text-white mb-8">
          Open Body Tracker
        </h1>
        
        <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
            Welcome
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Your self-hosted platform for longitudinal tracking of anthropometric 
            and physical assessment data.
          </p>
          
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h3 className="font-medium text-blue-800 dark:text-blue-300 mb-2">
              Status: Development
            </h3>
            <p className="text-sm text-blue-700 dark:text-blue-400">
              Frontend scaffold is ready. Backend API endpoints are being developed.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
