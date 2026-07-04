import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";

function App() {
    const [user, setUser] = useState(
        () => JSON.parse(localStorage.getItem("user"))
    );

    const handleLogin = (userData) => {
        localStorage.setItem("user", JSON.stringify(userData));
        setUser(userData);
    };

    const handleLogout = () => {
        localStorage.removeItem("user");
        setUser(null);
    };

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={
                    user ? <Navigate to="/dashboard" /> : <LoginPage onLogin={handleLogin} />
                } />
                <Route path="/dashboard" element={
                    user
                        ? <DashboardPage onLogout={handleLogout} />
                        : <Navigate to="/" />
                } />
            </Routes>
        </BrowserRouter>
    );
}

export default App;