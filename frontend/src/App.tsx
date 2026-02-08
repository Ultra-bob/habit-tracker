import { useState, useEffect } from 'react'

function App() {
  const [count, setCount] = useState<number | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/counter')
      .then(res => res.json())
      .then(data => {
        setCount(data.counter)
      })
  }, [])

  const increment = () => {
    fetch('http://localhost:8000/increment', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        setCount(data.counter)
      })
  }

  return (
    <>
      <div className="card">
        <button onClick={increment} className="p-4 rounded-lg m-4 bg-blue-800 text-white hover:bg-blue-600">
          count is {count}
        </button>
      </div>
    </>
  )
}

export default App
