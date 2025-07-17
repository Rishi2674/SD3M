import React from 'react';
import Header from './components/header';
import Footer from './components/footer';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="App" style={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Header />
      <main style={{
        flex: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '20px'
      }}>
        <ChatInterface />
      </main>
      <Footer />
    </div>
  );
}

export default App;