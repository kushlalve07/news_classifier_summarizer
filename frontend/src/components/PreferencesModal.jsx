import { useState } from "react";
import { savePreferences } from "../services/api";

const TOPICS = ["Sports", "Technology", "Business", "Entertainment", "World", "India", "Environment"];
const CITIES = ["None", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Chandigarh", "Jaipur", "Lucknow", "Nagpur"];

export default function PreferencesModal({ currentPrefs, userId, onSave, onClose }) {
    const [selectedTopics, setSelectedTopics] = useState(currentPrefs?.topics || []);
    const [city, setCity] = useState(currentPrefs?.city || "None");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const toggleTopic = (topic) => {
        setSelectedTopics(prev =>
            prev.includes(topic)
                ? prev.filter(t => t !== topic)
                : [...prev, topic]
        );
    };

    const handleSave = async () => {
        if (selectedTopics.length === 0) {
            setError("Please select at least one topic");
            return;
        }
        setIsLoading(true);
        setError("");
        try {
            await savePreferences(
                userId,
                selectedTopics,
                city === "None" ? null : city
            );
            onSave(selectedTopics, city === "None" ? null : city);
        } catch (e) {
            setError("Failed to save preferences");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        // Backdrop
        <div style={styles.backdrop} onClick={onClose}>
            {/* Modal — stop click propagating to backdrop */}
            <div style={styles.modal} onClick={e => e.stopPropagation()}>

                {/* Header */}
                <div style={styles.header}>
                    <h2 style={styles.title}>⚙️ Edit Preferences</h2>
                    <button style={styles.closeBtn} onClick={onClose}>✕</button>
                </div>

                {/* Topics */}
                <div style={styles.section}>
                    <p style={styles.sectionLabel}>Topics</p>
                    <div style={styles.topicGrid}>
                        {TOPICS.map(topic => (
                            <button
                                key={topic}
                                type="button"
                                style={{
                                    ...styles.topicBtn,
                                    ...(selectedTopics.includes(topic) ? styles.topicBtnActive : {})
                                }}
                                onClick={() => toggleTopic(topic)}
                            >
                                {topic}
                            </button>
                        ))}
                    </div>
                </div>

                {/* City */}
                <div style={styles.section}>
                    <p style={styles.sectionLabel}>City</p>
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

                {/* Footer */}
                <div style={styles.footer}>
                    <button style={styles.cancelBtn} onClick={onClose}>
                        Cancel
                    </button>
                    <button
                        style={{ ...styles.saveBtn, opacity: isLoading ? 0.7 : 1 }}
                        onClick={handleSave}
                        disabled={isLoading}
                    >
                        {isLoading ? "Saving..." : "Save & Reload Feed"}
                    </button>
                </div>
            </div>
        </div>
    );
}

const styles = {
    backdrop: {
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: "20px"
    },
    modal: {
        backgroundColor: "white",
        borderRadius: "16px",
        width: "100%",
        maxWidth: "480px",
        maxHeight: "85vh",
        overflowY: "auto",
        boxShadow: "0 20px 60px rgba(0,0,0,0.3)"
    },
    header: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "24px 24px 0"
    },
    title: { margin: 0, fontSize: "20px" },
    closeBtn: {
        background: "none",
        border: "none",
        fontSize: "18px",
        cursor: "pointer",
        color: "#888",
        padding: "4px 8px",
        borderRadius: "6px"
    },
    section: { padding: "20px 24px 0" },
    sectionLabel: {
        fontWeight: "600",
        fontSize: "14px",
        marginBottom: "10px",
        color: "#333"
    },
    topicGrid: { display: "flex", flexWrap: "wrap", gap: "8px" },
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
    select: {
        width: "100%",
        padding: "10px 14px",
        borderRadius: "8px",
        border: "1.5px solid #e5e7eb",
        fontSize: "14px",
        backgroundColor: "white"
    },
    error: {
        margin: "16px 24px 0",
        padding: "10px 14px",
        backgroundColor: "#fef2f2",
        border: "1px solid #fecaca",
        borderRadius: "8px",
        color: "#dc2626",
        fontSize: "13px"
    },
    footer: {
        display: "flex",
        gap: "12px",
        padding: "24px",
        justifyContent: "flex-end"
    },
    cancelBtn: {
        padding: "10px 20px",
        borderRadius: "8px",
        border: "1.5px solid #e5e7eb",
        backgroundColor: "white",
        fontSize: "14px",
        fontWeight: "600",
        cursor: "pointer"
    },
    saveBtn: {
        padding: "10px 20px",
        borderRadius: "8px",
        border: "none",
        backgroundColor: "#2563eb",
        color: "white",
        fontSize: "14px",
        fontWeight: "600",
        cursor: "pointer"
    }
};