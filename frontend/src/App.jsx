import { useEffect, useLayoutEffect } from "react";
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { DeskBookingAdmin } from "./components/admin/DeskBookingAdmin";
import { Login } from "./components/auth/Login";
import { SignUp } from "./components/auth/SignUp";
import DeskBooking from "./components/desk-booking/DeskBooking";
import Home from "./components/desk-booking/Home";
import UserBookings from "./components/desk-booking/UserBookings";
import AuthService from "./components/services/auth.service";
import { NotFound } from "./NotFound";

const App = () => {
  let location = useLocation();
  let navigate = useNavigate();

  useEffect(() => {
    const user = AuthService.getCurrentUser();
  }, []);

  useLayoutEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));
    if (user) {
      const decodedJwt = JSON.parse(atob(user.access_token.split(".")[1]));
      if (decodedJwt.exp * 1000 < Date.now()) {
        AuthService.logout();
        navigate("/");
        navigate(0);
      }
    }
  }, [location]);

  return (
    <Routes>
      <Route exact path="/" element={<Home />} />
      <Route exact path="/login" element={<Login />} />
      <Route exact path="/sign-up" element={<SignUp />} />
      <Route
        path="/admin/*"
        element={
          <RequireAuth redirectTo="/">
            <DeskBookingAdmin />
          </RequireAuth>
        }
      />
      <Route
        path="/desk-booking"
        element={
          <RequireAuth redirectTo="/">
            <DeskBooking />
          </RequireAuth>
        }
      />
      <Route
        path="/my-bookings"
        element={
          <RequireAuth redirectTo="/">
            <UserBookings />
          </RequireAuth>
        }
      />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

function RequireAuth({ children, redirectTo }) {
  return localStorage.getItem("user") !== null ? (
    children
  ) : (
    <Navigate to={redirectTo} replace={true} />
  );
}

export default App;
