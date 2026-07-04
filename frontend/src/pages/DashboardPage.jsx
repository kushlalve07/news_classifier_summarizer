import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getFeed } from "../services/api";
import NewsCard from "../components/NewsCard";

const ALL_TABS = ["All", "Sports", "Technology", "Business", "Entertainment", "World", "India", "Environment", "Regional"];

// Filter to only last 24 hours
const isRecent = (dateStr) => {
    if (!dateStr) return true; // keep if no date
    try {
        const published = new Date(dateStr);
        const now = new Date();
        const diffHours = (now - published) / (1000 * 60 * 60);
        return diffHours <= 24;
    } catch {
        return true;
    }
};

// Sort most recent first
const sortByDate = (articles) => {
    return [...articles].sort((a, b) => {
        if (!a.published) return 1;
        if (!b.published) return -1;
        return new Date(b.published) - new Date(a.published);
    });
};

export default function DashboardPage({ onLogout }) {
    const [articles, setArticles] = useState([]);
    const [activeTab, setActiveTab] = useState("All");
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");
    const [searchQuery, setSearchQuery] = useState("");
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("user"));

    useEffect(() => {
        loadFeed();
    }, []);

    const loadFeed = async () => {
        setIsLoading(true);
        setError("");
        try {
            const res = await getFeed(user.user_id);
            
            // 1. Force is_regional articles into the "Regional" category tab
            const normalizedArticles = res.data.articles.map(a => ({
                ...a,
                category: a.is_regional ? "Regional" : a.category
            }));
        
            // 2. Filter by date and sort
            const recent = normalizedArticles.filter(a => isRecent(a.published));
            setArticles(sortByDate(recent));
        } catch (e) {
            setError("Failed to load feed. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogout = () => {
        console.log("Logging out of app");
        onLogout();
    };

    const handleEditPrefs = () => {
        alert("Edit preferences coming soon!");
    };

    // Filter by active tab + search query
    const filteredArticles = articles
        .filter(a => activeTab === "All" || a.category === activeTab)
        .filter(a => {
            if (!searchQuery) return true;
            const q = searchQuery.toLowerCase();
            return (
                a.title.toLowerCase().includes(q) ||
                a.summary.toLowerCase().includes(q) ||
                a.source.toLowerCase().includes(q)
            );
        });

    // Only show tabs that have articles
    const activeTabs = ALL_TABS.filter(tab =>
        tab === "All" || articles.some(a => a.category === tab)
    );

    return (
        <div style={styles.page}>
            {/* ── Navbar ── */}
            <nav style={styles.navbar}>
                <span style={styles.logo}>📰 Daily Brief</span>
                <div style={styles.navRight}>
                    <span style={styles.welcomeText}>👤 {user?.username}</span>
                    <button style={styles.navBtn} onClick={handleEditPrefs}>
                        ⚙️ Preferences
                    </button>
                    <button style={{...styles.navBtn, ...styles.logoutBtn}} onClick={handleLogout}>
                        Logout
                    </button>
                </div>
            </nav>

            <div style={styles.content}>
                {/* ── Search bar ── */}
                <input
                    style={styles.searchBar}
                    type="text"
                    placeholder="🔍 Search headlines, sources..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                />

                {/* ── Tab bar ── */}
                <div style={styles.tabBar}>
                    {activeTabs.map(tab => (
                        <button
                            key={tab}
                            style={{
                                ...styles.tab,
                                ...(activeTab === tab ? styles.tabActive : {})
                            }}
                            onClick={() => setActiveTab(tab)}
                        >
                            {tab}
                            {tab !== "All" && (
                                <span style={styles.tabCount}>
                                    {articles.filter(a => a.category === tab).length}
                                </span>
                            )}
                        </button>
                    ))}
                </div>

                {/* ── Feed ── */}
                {isLoading ? (
                    <div style={styles.loadingBox}>
                        {/* Updated Text */}
                        <p style={styles.loadingText}>
                            ⏳ Fetching your personalized daily brief...
                        </p>
                        <div style={styles.loadingBar}>
                            <div style={styles.loadingBarInner} />
                        </div>
                    </div>
                ) : error ? (
                    <div style={styles.errorBox}>
                        <p>{error}</p>
                        <button style={styles.retryBtn} onClick={loadFeed}>Retry</button>
                    </div>
                ) : filteredArticles.length === 0 ? (
                    <p style={styles.emptyText}>
                        {searchQuery ? "No articles match your search." : "No recent articles in this category."}
                    </p>
                ) : (
                    <div style={styles.grid}>
                        {filteredArticles.map((article, i) => (
                            <NewsCard key={i} article={article} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

const styles = {
    page: { minHeight: "100vh", backgroundColor: "#f0f2f5", fontFamily: "system-ui, sans-serif" },
    navbar: {
        backgroundColor: "white",
        padding: "0 32px",
        height: "60px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
        position: "sticky",
        top: 0,
        zIndex: 100
    },
    logo: { fontSize: "20px", fontWeight: "700" },
    navRight: { display: "flex", alignItems: "center", gap: "12px" },
    welcomeText: { fontSize: "14px", color: "#555" },
    navBtn: {
        padding: "7px 14px",
        borderRadius: "8px",
        border: "1.5px solid #ddd",
        backgroundColor: "white",
        fontSize: "13px",
        fontWeight: "600",
        cursor: "pointer"
    },
    logoutBtn: { borderColor: "#fecaca", color: "#dc2626", backgroundColor: "#fff5f5" },
    content: { maxWidth: "900px", margin: "0 auto", padding: "24px 16px" },
    searchBar: {
        width: "100%",
        padding: "12px 16px",
        borderRadius: "10px",
        border: "1.5px solid #ddd",
        fontSize: "15px",
        backgroundColor: "white",
        marginBottom: "16px",
        boxSizing: "border-box"
    },
    tabBar: {
        display: "flex",
        gap: "8px",
        flexWrap: "wrap",
        marginBottom: "20px"
    },
    tab: {
        padding: "7px 16px",
        borderRadius: "20px",
        border: "1.5px solid #ddd",
        backgroundColor: "white",
        fontSize: "13px",
        fontWeight: "600",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        gap: "6px",
        transition: "all 0.15s"
    },
    tabActive: { backgroundColor: "#2563eb", color: "white", borderColor: "#2563eb" },
    tabCount: {
        backgroundColor: "rgba(0,0,0,0.1)",
        borderRadius: "10px",
        padding: "1px 6px",
        fontSize: "11px"
    },
    grid: { display: "flex", flexDirection: "column", gap: "14px" },
    loadingBox: {
        backgroundColor: "white",
        borderRadius: "12px",
        padding: "40px",
        textAlign: "center"
    },
    loadingText: { color: "#555", marginBottom: "16px" },
    loadingBar: {
        height: "6px",
        backgroundColor: "#e5e7eb",
        borderRadius: "3px",
        overflow: "hidden"
    },
    loadingBarInner: {
        height: "100%",
        width: "60%",
        backgroundColor: "#2563eb",
        borderRadius: "3px",
        animation: "pulse 1.5s ease-in-out infinite"
    },
    errorBox: { textAlign: "center", padding: "40px", color: "#e53e3e" },
    retryBtn: {
        marginTop: "12px",
        padding: "10px 24px",
        backgroundColor: "#2563eb",
        color: "white",
        border: "none",
        borderRadius: "8px",
        cursor: "pointer",
        fontWeight: "600"
    },
    emptyText: { textAlign: "center", color: "#999", padding: "40px" }
};