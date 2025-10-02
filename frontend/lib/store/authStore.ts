import { create } from 'zustand';
import Cookies from 'js-cookie';
import api from '../api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  department: string;
  role: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (username: string, password: string) => {
    try {
      const response = await api.post('/api/auth/login/', {
        username,
        password,
      });

      const { access, refresh, user } = response.data;

      Cookies.set('access_token', access, { expires: 7 });
      Cookies.set('refresh_token', refresh, { expires: 7 });

      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      throw error;
    }
  },

  logout: async () => {
    try {
      const refreshToken = Cookies.get('refresh_token');
      await api.post('/api/auth/logout/', { refresh: refreshToken });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  fetchUser: async () => {
    try {
      const token = Cookies.get('access_token');
      if (!token) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }

      const response = await api.get('/api/auth/me/');
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch (error) {
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user });
  },
}));
