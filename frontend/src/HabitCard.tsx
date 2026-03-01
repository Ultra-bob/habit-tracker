import { IconCheck, IconPlus } from "@tabler/icons-react"
import { useEffect, useState } from "react"

function HabitCard({ habitData }) {

    const [habitLogStatus, setHabitLogStatus] = useState([])

    useEffect(() => {
        fetch(`http://localhost:8000/log/${habitData.id}/summary`)
            .then(response => response.json())
            .then(data => setHabitLogStatus(data[(new Date()).toISOString().split('T')[0]] ?? 0))
            .catch(error => console.error('Error fetching habits:', error))
    }, [habitData.id])

    return (
        <div className="bg-gray-800 w-auto max-w-lg p-2 flex flex-row justify-between" key={habitData.id}>
            <p className="flex-1 mx-4 text-lg">{habitData.name}</p>
            <div className="bg-gray-600 flex px-3 mx-2 justify-center flex-col">
                <p className="text-gray-400"><span className="text-2xl text-white">{habitLogStatus}</span> / {habitData.completion_target}</p>
            </div>
            <div className="flex flex-col justify-center">
                <button className="bg-emerald-600 hover:bg-emerald-500 transition-colors p-1">
                    <IconCheck />
                </button>
            </div>
        </div>
    )
}

export default HabitCard