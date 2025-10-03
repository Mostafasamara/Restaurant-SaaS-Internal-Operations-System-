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
      console.log('AuthStore: Sending login request...');

      const response = await api.post('/api/auth/login/', {
        username,
        password,
      });

      console.log('AuthStore: Login response received:', response.data);

      const { access, refresh, user } = response.data;

      if (!access || !refresh || !user) {
        throw new Error('Invalid response from server');
      }

      // Store tokens in cookies
      Cookies.set('access_token', access, { expires: 7 });
      Cookies.set('refresh_token', refresh, { expires: 7 });

      console.log('AuthStore: Tokens saved to cookies');
      console.log('AuthStore: User data:', user);

      // Update state
      set({ user, isAuthenticated: true, isLoading: false });

      console.log('AuthStore: Login complete');
    } catch (error: any) {
      console.error('AuthStore: Login failed:', error);
      console.error('AuthStore: Error response:', error.response?.data);

      // Clear any existing tokens
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });

      throw error;
    }
  },

  logout: async () => {
    console.log('AuthStore: Logging out...');
    try {
      const refreshToken = Cookies.get('refresh_token');
      if (refreshToken) {
        await api.post('/api/auth/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('AuthStore: Logout error:', error);
    } finally {
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
      console.log('AuthStore: Logout complete');
    }
  },

  fetchUser: async () => {
    console.log('AuthStore: Fetching user...');
    try {
      const token = Cookies.get('access_token');

      if (!token) {
        console.log('AuthStore: No token found');
        set({ user: null, isAuthenticated: false, isLoading: false });
        return;
      }

      console.log('AuthStore: Token found, fetching user data...');
      const response = await api.get('/api/auth/me/');

      console.log('AuthStore: User data fetched:', response.data);
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch (error) {
      console.error('AuthStore: Fetch user error:', error);
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user });
  },
}));
