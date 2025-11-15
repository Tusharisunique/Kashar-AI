import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { LogOut, User } from 'lucide-react';

function Header() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="bg-white shadow-sm border-b border-primary-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-primary-900">
              Welcome back!
            </h2>
            <p className="text-sm text-primary-600">
              Ready to continue your learning journey?
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-primary-600">
              <User className="h-4 w-4" />
              <span>{user?.email}</span>
            </div>
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-primary-600 hover:text-primary-900 hover:bg-primary-100 rounded-md transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
