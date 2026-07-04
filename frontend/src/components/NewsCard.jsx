export default function NewsCard({ article }) {
    const formatDate = (dateStr) => {
        if (!dateStr) return "Recently";
        try {
            return new Date(dateStr).toLocaleString("en-IN", {
                day: "numeric",
                month: "short",
                hour: "2-digit",
                minute: "2-digit"
            });
        } catch {
            return dateStr;
        }
    };

    return (
        <div style={styles.card}>
            <div style={styles.topRow}>
                <div style={styles.badges}>
                    <span style={styles.sourceBadge}>{article.source}</span>
                    <span style={styles.categoryBadge}>{article.category}</span>
                    {article.is_regional && <span style={styles.regionalBadge}>📍 Local</span>}
                </div>
                <span style={styles.time}>{formatDate(article.published)}</span>
            </div>

            <h3 style={styles.headline}>{article.title}</h3>
            <p style={styles.summary}>{article.summary}</p>

            <a
                href={article.link}
                target="_blank"
                rel="noopener noreferrer"
                style={styles.readLink}
            >
                Read full article →
            </a>
        </div>
    );
}

const styles = {
    card: {
        backgroundColor: "white",
        borderRadius: "12px",
        padding: "20px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        border: "1px solid #f0f0f0",
        transition: "box-shadow 0.2s"
    },
    topRow: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "8px"
    },
    badges: { display: "flex", gap: "6px", flexWrap: "wrap" },
    sourceBadge: {
        backgroundColor: "#eff6ff",
        color: "#2563eb",
        padding: "3px 10px",
        borderRadius: "20px",
        fontSize: "12px",
        fontWeight: "600"
    },
    categoryBadge: {
        backgroundColor: "#f0fdf4",
        color: "#16a34a",
        padding: "3px 10px",
        borderRadius: "20px",
        fontSize: "12px",
        fontWeight: "600"
    },
    regionalBadge: {
        backgroundColor: "#fff7ed",
        color: "#ea580c",
        padding: "3px 10px",
        borderRadius: "20px",
        fontSize: "12px",
        fontWeight: "600"
    },
    time: { fontSize: "12px", color: "#999" },
    headline: { margin: 0, fontSize: "16px", fontWeight: "700", lineHeight: "1.4", color: "#111" },
    summary: { margin: 0, fontSize: "14px", color: "#555", lineHeight: "1.6" },
    readLink: {
        color: "#2563eb",
        fontSize: "13px",
        fontWeight: "600",
        textDecoration: "none",
        alignSelf: "flex-start"
    }
};