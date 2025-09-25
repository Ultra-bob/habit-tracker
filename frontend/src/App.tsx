import { useState, useEffect } from 'react'
import './App.css'

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
        <button onClick={increment}>
          count is {count}
        </button>
      </div>
    </>
  )
}

export default App
