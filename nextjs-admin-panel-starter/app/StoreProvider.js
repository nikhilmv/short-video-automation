"use client"

import { Provider, useDispatch } from "react-redux";
import { useEffect } from "react";
import axios from "axios";
import { store } from "./store/store";
import { setUser, setLoading } from "./store/authSlice";

function AuthLoader({ children }) {
  const dispatch = useDispatch();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/admin/me", {
          withCredentials: true
        });
        if (response.data && response.data.email) {
          dispatch(setUser(response.data));
        }
      } catch (error) {
        // Not logged in or error
      } finally {
        dispatch(setLoading(false));
      }
    };
    
    checkAuth();
  }, [dispatch]);

  return <>{children}</>;
}

export default function StoreProvider({ children }) {
  return (
    <Provider store={store}>
      <AuthLoader>{children}</AuthLoader>
    </Provider>
  );
}