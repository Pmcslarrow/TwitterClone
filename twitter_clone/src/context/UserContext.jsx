import { createContext, useState, useContext } from 'react';

/*

This file handles the global user context for a logged
in user. This makes it easier to reference the user rather than 
passing it down through props.

*/

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null); 

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
