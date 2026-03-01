import { useState, useEffect } from 'react'
import HabitCard from './HabitCard'

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
      <div className="flex justify-center">
        <div className="w-xl p-6">
          <h1 className="text-2xl font-bold">Habits</h1>
          <section className='py-6'>
            {habits.map(habit => (
              <HabitCard habitData={habit}></HabitCard>
            ))}
          </section>
        </div>
      </div>
    </>
  )
}

export default App
