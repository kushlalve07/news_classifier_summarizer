import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser, loginUser, savePreferences } from "../services/api";

const TOPICS = ["Sports", "Technology", "Business", "Entertainment", "World", "India", "Environment"];
const CITIES = ["None", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Lucknow"];

export default function LoginPage({ onLogin }) {
    const [activeForm, setActiveForm] = useState("login"); // "login" or "register"
    const navigate = useNavigate();

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                {/* Header */}
                <div style={styles.header}>
                    <h1 style={styles.title}>📰 Daily Brief</h1>
                    <p style={styles.subtitle}>Your personalised Indian news feed</p>
                </div>

                {/* Tab switcher */}
                <div style={styles.tabSwitcher}>
                    <button
                        style={{
                            ...styles.switchBtn,
                            ...(activeForm === "login" ? styles.switchBtnActive : {})
                        }}
                        onClick={() => setActiveForm("login")}
                    >
                        Login
                    </button>
                    <button
                        style={{
                            ...styles.switchBtn,
                            ...(activeForm === "register" ? styles.switchBtnActive : {})
                        }}
                        onClick={() => setActiveForm("register")}
                    >
                        Register
                    </button>
                </div>

                {/* Forms */}
                {activeForm === "login"
                    ? <LoginForm onLogin={onLogin} />
                    : <RegisterForm onLogin={onLogin} />
                }
            </div>
        </div>
    );
}

// ── Login Form ────────────────────────────────────────
function LoginForm({ onLogin }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async () => {
        if (!username || !password) {
            setError("Please fill in all fields");
            return;
        }
        setIsLoading(true);
        setError("");
        try {
            const res = await loginUser(username.trim(), password);
            console.log("Logging in for user: ",username)
            onLogin(res.data); 
        } catch (e) {
            setError(e.response?.data?.detail || "Invalid username or password");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={styles.formBody}>
            <div style={styles.fieldGroup}>
                <label style={styles.label}>Username</label>
                <input
                    style={styles.input}
                    type="text"
                    placeholder="e.g. kushal007"
                    value={username}
                    onChange={e => { setUsername(e.target.value); setError(""); }}
                    onKeyDown={e => e.key === "Enter" && handleLogin()}
                />
            </div>

            <div style={styles.fieldGroup}>
                <label style={styles.label}>Password</label>
                <input
                    style={styles.input}
                    type="password"
                    placeholder="Your password"
                    value={password}
                    onChange={e => { setPassword(e.target.value); setError(""); }}
                    onKeyDown={e => e.key === "Enter" && handleLogin()}
                />
            </div>

            {error && <p style={styles.error}>{error}</p>}

            <button
                style={{ ...styles.btn, opacity: isLoading ? 0.7 : 1 }}
                onClick={handleLogin}
                disabled={isLoading}
            >
                {isLoading ? "Logging in..." : "Login →"}
            </button>
        </div>
    );
}

// ── Register Form ─────────────────────────────────────
function RegisterForm({ onLogin }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [selectedTopics, setSelectedTopics] = useState([]);
    const [city, setCity] = useState("None");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const toggleTopic = (topic) => {
        setSelectedTopics(prev =>
            prev.includes(topic)
                ? prev.filter(t => t !== topic)
                : [...prev, topic]
        );
    };

    const validate = () => {
        if (username.length < 7)
            return "Username must be at least 7 characters";
        if (username !== username.toLowerCase())
            return "Username must be all lowercase";
        if (username.includes(" "))
            return "Username must not contain spaces";
        if (!/^[a-z0-9_]+$/.test(username))
            return "Only lowercase letters, numbers, underscores allowed";
        if (password.length < 8)
            return "Password must be at least 8 characters";
        if (password !== confirmPassword)
            return "Passwords do not match";
        if (selectedTopics.length === 0)
            return "Please select at least one topic";
        return null;
    };

    const handleRegister = async () => {
        const err = validate();
        if (err) { setError(err); return; }

        setIsLoading(true);
        setError("");
        try {
            const res = await registerUser(username.trim(), password);
            const userData = res.data;

            await savePreferences(
                userData.user_id,
                selectedTopics,
                city === "None" ? null : city
            );

            console.log("Registering user: ", username);
            onLogin(userData);  
        } catch (e) {
            setError(e.response?.data?.detail || "Registration failed");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={styles.formBody}>
            {/* Username */}
            <div style={styles.fieldGroup}>
                <label style={styles.label}>Username</label>
                <input
                    style={styles.input}
                    type="text"
                    placeholder="e.g. kushal007"
                    value={username}
                    onChange={e => { setUsername(e.target.value); setError(""); }}
                />
                <p style={styles.hint}>
                    Min 7 chars · all lowercase · no spaces · letters, numbers, underscores only
                </p>
            </div>

            {/* Password */}
            <div style={styles.fieldGroup}>
                <label style={styles.label}>Password</label>
                <input
                    style={styles.input}
                    type="password"
                    placeholder="Min 8 characters"
                    value={password}
                    onChange={e => { setPassword(e.target.value); setError(""); }}
                />
            </div>

            {/* Confirm Password */}
            <div style={styles.fieldGroup}>
                <label style={styles.label}>Confirm Password</label>
                <input
                    style={styles.input}
                    type="password"
                    placeholder="Re-enter your password"
                    value={confirmPassword}
                    onChange={e => { setConfirmPassword(e.target.value); setError(""); }}
                />
            </div>

            {/* Topics */}
            <div style={styles.fieldGroup}>
                <label style={styles.label}>Topics you care about</label>
                <div style={styles.topicGrid}>
                    {TOPICS.map(topic => (
                        <button
                            key={topic}
                            style={{
                                ...styles.topicBtn,
                                ...(selectedTopics.includes(topic) ? styles.topicBtnActive : {})
                            }}
                            onClick={() => toggleTopic(topic)}
                            type="button"
                        >
                            {topic}
                        </button>
                    ))}
                </div>
            </div>

            {/* City */}
            <div style={styles.fieldGroup}>
                <label style={styles.label}>Your city <span style={styles.optional}>(optional — for local news)</span></label>
                <select
                    style={styles.select}
                    value={city}
                    onChange={e => setCity(e.target.value)}
                >
                    {CITIES.map(c => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
            </div>

            {error && <p style={styles.error}>{error}</p>}

            <button
                style={{ ...styles.btn, opacity: isLoading ? 0.7 : 1 }}
                onClick={handleRegister}
                disabled={isLoading}
            >
                {isLoading ? "Creating account..." : "Create Account →"}
            </button>
        </div>
    );
}

// ── Styles ────────────────────────────────────────────
const styles = {
    container: {
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#f0f2f5",
        fontFamily: "system-ui, sans-serif",
        padding: "24px"
    },
    card: {
        backgroundColor: "white",
        borderRadius: "16px",
        boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
        width: "100%",
        maxWidth: "480px",
        overflow: "hidden"
    },
    header: {
        padding: "32px 32px 0",
        textAlign: "center"
    },
    title: { margin: "0 0 6px", fontSize: "26px" },
    subtitle: { margin: 0, color: "#666", fontSize: "14px" },
    tabSwitcher: {
        display: "flex",
        margin: "24px 32px 0",
        borderRadius: "10px",
        backgroundColor: "#f0f2f5",
        padding: "4px"
    },
    switchBtn: {
        flex: 1,
        padding: "9px",
        border: "none",
        borderRadius: "8px",
        backgroundColor: "transparent",
        fontSize: "14px",
        fontWeight: "600",
        cursor: "pointer",
        color: "#888",
        transition: "all 0.15s"
    },
    switchBtnActive: {
        backgroundColor: "white",
        color: "#111",
        boxShadow: "0 1px 4px rgba(0,0,0,0.1)"
    },
    formBody: {
        padding: "24px 32px 32px",
        display: "flex",
        flexDirection: "column",
        gap: "18px",
        maxHeight: "70vh",
        overflowY: "auto"
    },
    fieldGroup: {
        display: "flex",
        flexDirection: "column",
        gap: "6px"
    },
    label: { fontSize: "13px", fontWeight: "600", color: "#333" },
    hint: { fontSize: "11px", color: "#999", margin: 0 },
    optional: { fontWeight: "400", color: "#aaa" },
    input: {
        padding: "11px 14px",
        borderRadius: "8px",
        border: "1.5px solid #e5e7eb",
        fontSize: "14px",
        outline: "none",
        transition: "border 0.15s"
    },
    select: {
        padding: "11px 14px",
        borderRadius: "8px",
        border: "1.5px solid #e5e7eb",
        fontSize: "14px",
        backgroundColor: "white"
    },
    topicGrid: {
        display: "flex",
        flexWrap: "wrap",
        gap: "8px"
    },
    topicBtn: {
        padding: "7px 16px",
        borderRadius: "20px",
        border: "1.5px solid #e5e7eb",
        backgroundColor: "white",
        fontSize: "13px",
        fontWeight: "500",
        cursor: "pointer",
        transition: "all 0.15s"
    },
    topicBtnActive: {
        backgroundColor: "#2563eb",
        color: "white",
        borderColor: "#2563eb"
    },
    error: {
        fontSize: "13px",
        color: "#dc2626",
        margin: 0,
        padding: "10px 14px",
        backgroundColor: "#fef2f2",
        borderRadius: "8px",
        border: "1px solid #fecaca"
    },
    btn: {
        padding: "13px",
        backgroundColor: "#2563eb",
        color: "white",
        border: "none",
        borderRadius: "8px",
        fontSize: "15px",
        fontWeight: "600",
        cursor: "pointer"
    }
};