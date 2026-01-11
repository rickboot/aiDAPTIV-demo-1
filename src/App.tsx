import { ScenarioProvider } from './ScenarioContext';
import { Dashboard } from './components/Dashboard';
import { HardwareMonitor } from './components/HardwareMonitor';
import { BackendStatusBanner } from './components/BackendStatusBanner';

function App() {
  return (
    <ScenarioProvider>
      <div className="relative min-h-screen bg-black">
        <BackendStatusBanner />
        <Dashboard />
        <HardwareMonitor />
      </div>
    </ScenarioProvider>
  );
}

export default App;
