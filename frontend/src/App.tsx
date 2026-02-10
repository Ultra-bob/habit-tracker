import { useState, useEffect } from 'react'

function App() {
  const [habits, setHabits] = useState([])

  useEffect(() => {
    fetch('http://localhost:8000/habits')
      .then(response => response.json())
      .then(data => setHabits(data))
      .catch(error => console.error('Error fetching habits:', error))
  }, [])

  return (
    <>
      <div className="card">
        <h1 className="text-2xl font-bold">Habits</h1>
        {habits.map(habit => (
          <div key={habit.id}>{habit.name}</div>
        ))}
      </div>
    </>
  )
}

export default App
