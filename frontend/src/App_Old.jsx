import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Wallet, LogOut } from 'lucide-react';
import VoiceInterface from './components/VoiceInterface';
import Dashboard from './components/Dashboard';
import TransactionList from './components/TransactionList';
import PinModal from './components/PinModal';
import PaymentSuccessModal from './components/PaymentSuccessModal';
import InvestmentNudge from './components/InvestmentNudge';
import MonthlyInvestmentAnalysis from './components/MonthlyInvestmentAnalysis';
import PhoneInputModal from './components/PhoneInputModal';
import Toast from './components/Toast';
import Login from './components/Login';
import { getAllUsers, getUserData, makePayment, makeInvestment, getInvestmentAnalysis, savePhoneNumber } from './services/api';
import { isAuthenticated, getCurrentUser as getStoredUser, logout, fetchCurrentUser } from './services/auth';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function MainApp() {
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPinModal, setShowPinModal] = useState(false);
  const [pendingPayment, setPendingPayment] = useState(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successPayment, setSuccessPayment] = useState(null);
  const [investmentNudge, setInvestmentNudge] = useState(null);
  const [monthlyAnalysis, setMonthlyAnalysis] = useState(null);
  const [toast, setToast] = useState(null);
  const [showPhoneModal, setShowPhoneModal] = useState(false);

  useEffect(() => {
    loadCurrentUser();
  }, []);

  const loadCurrentUser = async () => {
    try {
      // Try to get user from localStorage first
      let user = getStoredUser();
      
      console.log('Loading current user from localStorage:', user);
      
      if (user) {
        console.log('Setting current user:', user);
        setCurrentUser(user);
        setSelectedUserId(user.id);
        
        console.log('Set user ID to:', user.id);
        console.log('This user ID should NEVER change!');
        
        // Fetch fresh user data from backend to get phone_number
        try {
          const freshUserData = await getUserData(user.id);
          if (freshUserData) {
            console.log('Fresh user data from backend:', freshUserData);
            
            // Update user with fresh data including phone_number
            const updatedUser = {
              ...user,
              phone_number: freshUserData.phone_number,
              balance: freshUserData.balance
            };
            
            setCurrentUser(updatedUser);
            localStorage.setItem('user', JSON.stringify(updatedUser));
            
            // Check if user needs to add phone number (after fetching fresh data)
            if (!freshUserData.phone_number) {
              console.log('User has no phone number, showing phone modal');
              setShowPhoneModal(true);
            } else {
              console.log('User already has phone number:', freshUserData.phone_number);
            }
          }
        } catch (err) {
          console.error('Error fetching fresh user data:', err);
          // If fetch fails, check with existing user data
          if (!user.phone_number) {
            console.log('User has no phone number (from localStorage), showing phone modal');
            setShowPhoneModal(true);
          }
        }
        
        // Load other users for display (but don't change selectedUserId)
        loadUsers();
      } else {
        throw new Error('No user found');
      }
    } catch (error) {
      console.error('Error loading current user:', error);
      showToast('Failed to load user', 'error');
      setLoading(false);
    }
  };

  const handlePhoneSubmit = async (phoneNumber) => {
    try {
      console.log('Submitting phone number:', phoneNumber);
      const response = await savePhoneNumber(currentUser.id, phoneNumber);
      
      if (response.success) {
        console.log('Phone number saved:', response);
        
        // Update current user with phone number
        const updatedUser = { ...currentUser, phone_number: phoneNumber };
        if (response.data.new_balance) {
          updatedUser.balance = response.data.new_balance;
        }
        
        setCurrentUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
        
        setShowPhoneModal(false);
        showToast(response.message, 'success');
        
        // Reload user data to get updated balance if accounts were linked
        if (response.data.linked) {
          loadUserData();
        }
      }
    } catch (error) {
      console.error('Error saving phone number:', error);
      showToast('Failed to save phone number', 'error');
      throw error;
    }
  };

  const handlePhoneSkip = () => {
    setShowPhoneModal(false);
    showToast('You can add your phone number later from settings', 'info');
  };

  useEffect(() => {
    if (selectedUserId) {
      loadUserData();
    }
  }, [selectedUserId]);

  const loadUsers = async () => {
    try {
      const allUsers = await getAllUsers();
      setUsers(allUsers);
      // DON'T change selectedUserId if already set
      console.log('[App] Loaded users, keeping selectedUserId:', selectedUserId);
    } catch (error) {
      console.error('Error loading users:', error);
      showToast('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadUserData = async () => {
    try {
      console.log('[App] Loading user data for user ID:', selectedUserId);
      const data = await getUserData(selectedUserId);
      console.log('[App] User data loaded:', {
        balance: data.balance,
        transactions: data.transactions?.length || 0,
        investments: data.investments?.total || 0
      });
      
      // Force update state
      setUserData({ ...data });
      
      // Update currentUser balance in state and localStorage
      if (currentUser && data.balance !== undefined) {
        const updatedUser = { 
          ...currentUser, 
          balance: data.balance 
        };
        console.log('[App] Updating currentUser balance:', updatedUser.balance);
        setCurrentUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
    } catch (error) {
      console.error('[App] Error loading user data:', error);
      showToast('Failed to load user data', 'error');
    }
  };

  const checkMonthlyAnalysis = async () => {
    try {
      const analysis = await getInvestmentAnalysis(selectedUserId);
      if (analysis.success && analysis.data.show) {
        setMonthlyAnalysis(analysis.data);
      } else {
        showToast(analysis.message || 'Need at least 5 transactions this month for analysis', 'info');
      }
    } catch (error) {
      console.error('Error fetching investment analysis:', error);
      showToast('Failed to load investment analysis', 'error');
    }
  };

  const handleVoiceResponse = (response) => {
    // Handle payment intent OR phone confirmation OR phone account creation with PIN requirement
    const needsPin = (response.intent === 'payment' || 
                      response.intent === 'phone_confirmation' || 
                      response.intent === 'phone_account_creation') 
                     && response.data?.requires_pin;
    
    if (needsPin) {
      console.log('🔑 PIN required for:', response.intent);
      console.log('📝 Pending payment data:', response.data);
      
      setPendingPayment({
        recipient: response.data.recipient,
        amount: response.data.amount
      });
      setShowPinModal(true);
    } else if (response.intent === 'balance' || response.intent === 'history') {
      loadUserData();
    }
  };

  const handlePinSubmit = async (pin) => {
    try {
      const response = await makePayment(
        pendingPayment.recipient,
        pendingPayment.amount,
        pin,
        selectedUserId
      );

      if (response.success) {
        handlePaymentSuccess(response.data);
      } else {
        showToast(response.message, 'error');
      }
    } catch (error) {
      showToast('Payment failed', 'error');
    }
  };

  const handlePaymentSuccess = (data) => {
    console.log('[App] Payment success:', data);
    
    // Close PIN modal immediately
    setShowPinModal(false);
    
    // Show success modal with payment details
    setSuccessPayment({
      amount: pendingPayment.amount,
      recipient: pendingPayment.recipient
    });
    setShowSuccessModal(true);
    setPendingPayment(null);
    
    // CRITICAL: Update balance immediately from response
    if (data.new_balance !== undefined) {
      console.log('[App] Updating balance immediately to:', data.new_balance);
      const updatedUser = { 
        ...currentUser, 
        balance: data.new_balance 
      };
      setCurrentUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
    
    // Reload user data to get full transaction list
    // Use setTimeout to ensure state updates
    setTimeout(() => {
      console.log('[App] Reloading user data after payment...');
      loadUserData().then(() => {
        console.log('[App] User data reloaded successfully');
      });
    }, 100);
    
    // Show investment nudge after success modal auto-closes
    if (data.nudge) {
      setTimeout(() => {
        setInvestmentNudge(data.nudge);
      }, 2500);
    }
  };

  const handleSuccessModalClose = () => {
    setShowSuccessModal(false);
    setSuccessPayment(null);
  };

  const handleInvestmentSuccess = () => {
    console.log('Investment success');
    setInvestmentNudge(null);
    
    // Force reload user data
    loadUserData().then(() => {
      console.log('User data reloaded after investment');
      showToast('Investment successful!', 'success');
    });
  };

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleLogout = async () => {
    try {
      await logout();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      window.location.href = '/login';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center">
        <div className="text-white text-xl">Loading VoicePay...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-4">
      <div className="max-w-md mx-auto">
        {/* Header with User Selector */}
        <div className="bg-white/10 backdrop-blur-lg rounded-t-3xl p-6 text-white">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              {currentUser?.picture ? (
                <img 
                  src={currentUser.picture} 
                  alt={currentUser.name}
                  className="w-10 h-10 rounded-full border-2 border-white/30"
                />
              ) : (
                <div className="bg-white/20 p-2 rounded-full">
                  <Wallet className="w-6 h-6" />
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold">VoicePay</h1>
                <p className="text-sm opacity-80">{currentUser?.name || 'User'}</p>
              </div>
            </div>
            
            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="bg-white/20 text-white px-4 py-2 rounded-lg border border-white/30 hover:bg-white/30 transition flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
          
          {/* Investment Analysis Button */}
          <button
            onClick={checkMonthlyAnalysis}
            className="w-full bg-gradient-to-r from-green-400/20 to-emerald-400/20 text-white px-4 py-2 rounded-lg border border-white/30 hover:from-green-400/30 hover:to-emerald-400/30 transition text-sm flex items-center justify-center gap-2"
          >
            <span>📊</span>
            <span>View Investment Insights</span>
          </button>
        </div>

        {/* Voice Interface */}
        <VoiceInterface 
          onResponse={handleVoiceResponse}
          userId={selectedUserId}
        />

        {/* Dashboard */}
        <Dashboard userData={userData} />

        {/* Transaction List */}
        <TransactionList transactions={userData?.transactions || []} />

        {/* PIN Modal */}
        {showPinModal && (
          <PinModal
            pendingPayment={pendingPayment}
            onSuccess={handlePaymentSuccess}
            onClose={() => {
              setShowPinModal(false);
              setPendingPayment(null);
            }}
            userId={selectedUserId}
          />
        )}

        {/* Payment Success Modal */}
        {showSuccessModal && (
          <PaymentSuccessModal
            payment={successPayment}
            onClose={handleSuccessModalClose}
          />
        )}

        {/* Investment Nudge */}
        {investmentNudge && (
          <InvestmentNudge
            nudge={investmentNudge}
            onInvest={handleInvestmentSuccess}
            onClose={() => setInvestmentNudge(null)}
            userId={selectedUserId}
          />
        )}

        {/* Monthly Investment Analysis */}
        {monthlyAnalysis && (
          <MonthlyInvestmentAnalysis
            analysis={monthlyAnalysis}
            onClose={() => setMonthlyAnalysis(null)}
            onViewDetails={() => {
              setMonthlyAnalysis(null);
              showToast('Auto-invest feature coming soon!', 'info');
            }}
          />
        )}

        {/* Phone Number Input Modal */}
        {showPhoneModal && (
          <PhoneInputModal
            onSubmit={handlePhoneSubmit}
            onSkip={handlePhoneSkip}
          />
        )}

        {/* Toast Notification */}
        {toast && <Toast message={toast.message} type={toast.type} />}
      </div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainApp />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;

