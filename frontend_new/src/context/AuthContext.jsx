import { createContext } from 'react';

const AuthContext = createContext({
  user: null,
  setUser: () => {},
  handleLogout: () => {}
});

export default AuthContext;
