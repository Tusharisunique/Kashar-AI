import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  BookOpen, 
  Home, 
  Upload, 
  MessageCircle, 
  Brain, 
  CreditCard, 
  BarChart3,
  FileText,
  Mic
} from 'lucide-react';

function Sidebar() {
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Upload Documents', href: '/upload', icon: Upload },
    { name: 'My Documents', href: '/documents', icon: FileText },
    { name: 'AI Tutor', href: '/tutor', icon: MessageCircle },
    { name: 'Live Tutor', href: '/live-tutor', icon: Mic },
    { name: 'Quiz', href: '/quiz', icon: Brain },
    { name: 'Flashcards', href: '/flashcards', icon: CreditCard },
    { name: 'Progress', href: '/progress', icon: BarChart3 },
  ];

  return (
    <div className="w-64 bg-white shadow-sm border-r border-primary-200 min-h-screen">
      <div className="p-6">
        <div className="flex items-center space-x-2">
          <BookOpen className="h-8 w-8 text-accent-600" />
          <h1 className="text-xl font-bold text-primary-900">Kashar AI</h1>
        </div>
      </div>
      
      <nav className="px-4 pb-4">
        <ul className="space-y-2">
          {navigation.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-accent-100 text-accent-700 border-r-2 border-accent-600'
                      : 'text-primary-600 hover:bg-primary-100 hover:text-primary-900'
                  }`
                }
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}

export default Sidebar;
