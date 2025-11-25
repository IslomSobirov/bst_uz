import React from 'react';
import { User, LogOut, Star } from 'lucide-react';

function Header({ user, onLogin, onLogout, currentView, onViewChange }) {
  const navItems = [
    { id: 'creators', label: 'Creators' },
    { id: 'posts', label: 'Posts' },
    { id: 'pricing', label: 'Pricing' },
  ];

  if (user) {
    navItems.push({ id: 'feed', label: 'My Feed' });
  }

  return (
    <header className="sticky top-0 z-50 w-full glass border-b border-border/40">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <h1
            className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-600 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => onViewChange('creators')}
          >
            Boosty
          </h1>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${currentView === item.id
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                  }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                {user.is_creator && (
                  <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r from-amber-500/10 to-orange-500/10 text-amber-600 border border-amber-500/20">
                    <Star className="w-3 h-3 fill-amber-500 text-amber-500" />
                    Creator
                  </span>
                )}
                <button
                  onClick={() => onViewChange('myProfile')}
                  className="flex items-center gap-2 text-sm font-medium text-foreground hover:text-primary transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <User className="w-4 h-4" />
                  </div>
                  <span className="hidden sm:block">{user.username}</span>
                </button>
              </div>

              <div className="h-6 w-px bg-border/60" />

              <button
                onClick={onLogout}
                className="p-2 rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onLogin}
              className="px-5 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
            >
              Login / Register
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
