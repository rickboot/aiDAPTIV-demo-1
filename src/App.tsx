import React from 'react';
import { ScenarioProvider } from './ScenarioContext';
import { WarRoomDisplay } from './components/WarRoomDisplay';
import { HardwareMonitor } from './components/HardwareMonitor';

function App() {
  return (
    <ScenarioProvider>
      <div className="relative min-h-screen bg-black">
        <WarRoomDisplay />
        <HardwareMonitor />
      </div>
    </ScenarioProvider>
  );
}

export default App;
