import React from 'react';
import MapComponent from './Map';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Fooglemaps - Singapore Food Map</h1>
        <p>Discover the best food spots in Singapore</p>
      </header>
      <MapComponent />
    </div>
  );
}

export default App;