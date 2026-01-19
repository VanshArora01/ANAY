import { motion } from 'framer-motion';
import { LayoutDashboard, Users, FileText, Link, Phone } from 'lucide-react';

interface NavigationBarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isOnline: boolean;
}

const NavigationBar = ({ activeTab, onTabChange, isOnline }: NavigationBarProps) => {
  const tabs = [
    { id: 'dashboard', label: 'DASHBOARD', icon: LayoutDashboard },
    { id: 'contacts', label: 'CONTACTS', icon: Users },
    { id: 'notes', label: 'NOTES', icon: FileText },
    { id: 'connect', label: 'CONNECT', icon: Link },
  ];

  const statusItems = [
    { label: 'SYSTEM READY', active: true },
    { label: 'NET LINKED', active: isOnline },
    { label: 'LISTENING', active: false },
  ];

  return (
    <nav className="px-1 flex items-center justify-between overflow-x-auto custom-scrollbar">
      {/* Left - Navigation Tabs */}
      <div className="flex items-center gap-2 flex-shrink-0">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;

          return (
            <motion.button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`anay-nav-item flex items-center gap-2 py-1.5 px-3 md:px-4 ${isActive ? 'anay-nav-item-active' : ''
                }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="font-orbitron text-[10px] md:text-xs tracking-wider">
                {tab.label}
              </span>
            </motion.button>
          );
        })}
      </div>

      {/* Center - ANAY Branding */}
      <div className="flex items-center gap-2 px-4 rounded-xl">
        <span className="text-sm md:text-base font-orbitron font-bold tracking-wider text-cyan-400">
          ANAY
        </span>
        <span className="text-[10px] md:text-xs font-light text-muted-foreground tracking-wide">
          Personal Assistant
        </span>
      </div>

      {/* Right - Status Indicators */}
      <div className="hidden lg:flex items-center gap-4 flex-shrink-0 opacity-80">
        {statusItems.map((item) => (
          <div
            key={item.label}
            className="flex items-center gap-2"
          >
            <span className="text-[9px] text-foreground/60 font-orbitron uppercase tracking-wider">
              {item.label}
            </span>
            <span className={`text-[10px] ${item.active ? 'text-anay-green' : 'text-muted-foreground'}`}>
              {item.active ? '🛰️' : '🔘'}
            </span>
          </div>
        ))}
      </div>
    </nav>
  );
};

export default NavigationBar;
