import { create } from 'zustand';
import { authAPI } from './api';

const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authAPI.login(email, password);
      localStorage.setItem('token', data.access_token);
      set({ token: data.access_token, isLoading: false });
      await get().fetchUser();
      return true;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      });
      return false;
    }
  },

  register: async (email, password, firstName, lastName) => {
    set({ isLoading: true, error: null });
    try {
      await authAPI.register(email, password, firstName, lastName);
      set({ isLoading: false });
      return true;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      });
      return false;
    }
  },

  fetchUser: async () => {
    if (!get().token) return;
    try {
      const user = await authAPI.getMe();
      set({ user });
    } catch (error) {
      set({ user: null, token: null });
      localStorage.removeItem('token');
    }
  },

  logout: () => {
    authAPI.logout();
    set({ user: null, token: null });
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
