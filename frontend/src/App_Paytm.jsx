import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import PaytmHeader from './components/PaytmHeader';
import MainActionCards from './components/MainActionCards';
import InvestmentAnalyticsCards from './components/InvestmentAnalyticsCards';
import TransactionHistoryPage from './components/TransactionHistoryPage';
import BalancePage from './components/BalancePage';
import VoicePaymentModal from './components/VoicePaymentModal';
import PinModal from './components/PinModal';
import PaymentSuccessModal from './components/PaymentSuccessModal';
import InvestmentNudge from './components/InvestmentNudge';
import PhoneInputModal from './components/PhoneInputModal';
import Toast from './components/Toast';
import Login from './components/Login';
import { getUserData, makePayment, savePhoneNumber } from './services/api';
import { isAuthenticated, getCurrentUser as getStoredUser, logout, fetchCurrentUser } from './services/auth';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function PaytmApp() {
  const [currentUser, setCurrentUser] = useState(null);
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState('home'); // 'home', 'history', 'balance'
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [showPinModal, setShowPinModal] = useState(false);
  const [pendingPayment, setPendingPayment] = useState(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successPayment, setSuccessPayment] = useState(null);
  const [investmentNudge, setInvestmentNudge] = useState(null);
  const [toast, setToast] = useState(null);
  const [showPhoneModal, setShowPhoneModal] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    loadCurrentUser();
  }, []);

  const loadCurrentUser = async () => {
    try {
      let user = getStoredUser();
      
      if (user) {
        setCurrentUser(user);
        
        // Fetch fresh user data
        try {
          const freshUserData = await getUserData(user.id);
          if (freshUserData) {
            const updatedUser = {
              ...user,
              phone_number: freshUserData.phone_number,
              balance: freshUserData.balance
            };
            
            setCurrentUser(updatedUser);
            localStorage.setItem('user', JSON.stringify(updatedUser));
            
            // Check if user needs to add phone number
            if (!freshUserData.phone_number) {
              setShowPhoneModal(true);
            }
          }
        } catch (error) {
          console.error('Error fetching fresh user data:', error);
        }
        
        await loadUserData(user.id);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading current user:', error);
      setLoading(false);
    }
  };

  const loadUserData = async (userId = null) => {
    try {
      const id = userId || currentUser?.id;
      if (!id) return;

      const data = await getUserData(id);
      setUserData(data);
      
      // Update current user balance
      if (currentUser) {
        const updatedUser = { ...currentUser, balance: data.balance };
        setCurrentUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const handleVoiceResponse = (response) => {
    const needsPin = (response.intent === 'payment' || 
                      response.intent === 'phone_confirmation' || 
                      response.intent === 'phone_account_creation') 
                     && response.data?.requires_pin;
    
    if (needsPin) {
      setPendingPayment({
        recipient: response.data.recipient,
        amount: response.data.amount
      });
      setShowVoiceModal(false);
      setShowPinModal(true);
    } else if (response.intent === 'balance' || response.intent === 'history') {
      loadUserData();
    }
  };

  const handlePaymentConfirm = async (pin) => {
    try {
      const result = await makePayment(
        pendingPayment.recipient,
        pendingPayment.amount,
        pin,
        currentUser.id
      );

      if (result.success) {
        setShowPinModal(false);
        setSuccessPayment(pendingPayment);
        setShowSuccessModal(true);
        setPendingPayment(null);
        
        // Update balance immediately
        if (currentUser) {
          const updatedUser = { 
            ...currentUser, 
            balance: result.data.new_balance 
          };
          setCurrentUser(updatedUser);
          localStorage.setItem('user', JSON.stringify(updatedUser));
        }
        
        // Reload full data after delay
        setTimeout(() => loadUserData(), 1000);
      } else {
        showToast(result.message || 'Payment failed', 'error');
      }
    } catch (error) {
      console.error('Payment error:', error);
      showToast('Payment failed. Please try again.', 'error');
    }
  };

  const handlePhoneSubmit = async (phoneNumber) => {
    try {
      const result = await savePhoneNumber(currentUser.id, phoneNumber);
      
      if (result.success) {
        showToast(result.message, 'success');
        setShowPhoneModal(false);
        await loadCurrentUser();
      } else {
        throw new Error(result.message || 'Failed to save phone number');
      }
    } catch (error) {
      throw error;
    }
  };

  const handlePhoneSkip = () => {
    setShowPhoneModal(false);
  };

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar 
        user={currentUser}
        onNavigate={(view) => {
          setCurrentView(view);
          setSidebarOpen(false); // Close sidebar on mobile after navigation
        }}
        onLogout={handleLogout}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        {currentView === 'home' && (
          <PaytmHeader 
            user={currentUser} 
            onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          />
        )}
        
        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto">
          {currentView === 'home' && (
            <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8">
              {/* Main Action Cards */}
              <MainActionCards
                onPayClick={() => setShowVoiceModal(true)}
                onBalanceClick={() => setCurrentView('balance')}
              />

              {/* Investment Analytics */}
              <InvestmentAnalyticsCards userData={userData} />
            </div>
          )}

          {currentView === 'history' && (
            <TransactionHistoryPage
              userData={userData}
              onBack={() => setCurrentView('home')}
            />
          )}

          {currentView === 'balance' && (
            <BalancePage
              userData={userData}
              onBack={() => setCurrentView('home')}
            />
          )}
        </div>
      </div>

      {/* Modals */}
      {showVoiceModal && (
        <VoicePaymentModal
          onClose={() => setShowVoiceModal(false)}
          onVoiceResponse={handleVoiceResponse}
        />
      )}

      {showPinModal && (
        <PinModal
          pendingPayment={pendingPayment}
          userId={currentUser?.id}
          onSuccess={(data) => {
            setShowPinModal(false);
            setSuccessPayment(pendingPayment);
            setShowSuccessModal(true);
            setPendingPayment(null);
            
            // Update balance immediately
            if (currentUser && data?.new_balance !== undefined) {
              const updatedUser = { 
                ...currentUser, 
                balance: data.new_balance 
              };
              setCurrentUser(updatedUser);
              localStorage.setItem('user', JSON.stringify(updatedUser));
            }
            
            // Show investment nudge if available
            if (data?.nudge) {
              setInvestmentNudge(data.nudge);
            }
            
            // Reload full data after delay
            setTimeout(() => loadUserData(), 1000);
          }}
          onClose={() => {
            setShowPinModal(false);
            setPendingPayment(null);
          }}
        />
      )}

      {showSuccessModal && (
        <PaymentSuccessModal
          payment={successPayment}
          onClose={() => {
            setShowSuccessModal(false);
            setSuccessPayment(null);
          }}
        />
      )}

      {investmentNudge && (
        <InvestmentNudge
          nudge={investmentNudge}
          userId={currentUser?.id}
          onInvest={() => {
            setInvestmentNudge(null);
            showToast('Investment successful! 🎉', 'success');
            setTimeout(() => loadUserData(), 1000);
          }}
          onClose={() => setInvestmentNudge(null)}
        />
      )}

      {showPhoneModal && (
        <PhoneInputModal
          onSubmit={handlePhoneSubmit}
          onSkip={handlePhoneSkip}
        />
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <PaytmApp />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;

