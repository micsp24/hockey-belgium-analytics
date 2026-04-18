"""
Hockey Belgium Analytics Dashboard
====================================
Lance depuis Datastackv2/ :
    streamlit run streamlit/streamlit/hockey/app.py
"""

import os
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── CONFIG ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Hockey Belgium Analytics",
    page_icon="🏑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLE ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Header principal */
.hb-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    letter-spacing: 0.08em;
    color: #F0F4FF;
    line-height: 1;
    margin-bottom: 0;
}
.hb-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    color: #8A9BB5;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #1A2332 0%, #0F1923 100%);
    border: 1px solid #2A3A4A;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.kpi-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: #4FC3F7;
    letter-spacing: 0.05em;
    line-height: 1;
}
.kpi-label {
    font-size: 0.78rem;
    color: #8A9BB5;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

/* Rank badge */
.rank-1 { color: #FFD700; font-weight: 700; }
.rank-2 { color: #C0C0C0; font-weight: 700; }
.rank-3 { color: #CD7F32; font-weight: 700; }

/* Tactical badge */
.badge-dominant  { background: #1B4D2E; color: #4ADE80; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
.badge-offensive { background: #4D2B1B; color: #FB923C; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
.badge-defensive { background: #1B2E4D; color: #60A5FA; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
.badge-balanced  { background: #2D1B4D; color: #A78BFA; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }

/* Section title */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 0.06em;
    color: #E2E8F0;
    border-left: 4px solid #4FC3F7;
    padding-left: 12px;
    margin: 24px 0 12px 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0A1628;
    border-right: 1px solid #1E2D42;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #8A9BB5 !important;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Main background */
.main .block-container {
    background: #0D1B2A;
    padding-top: 1.5rem;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #1E2D42;
    border-radius: 8px;
}

/* Divider */
hr { border-color: #1E2D42; }
</style>
""", unsafe_allow_html=True)

# ── CONNEXION DUCKDB ──────────────────────────────────────────────────────────

@st.cache_resource
def get_connection():
    db_path = os.environ.get(
        "DUCKDB_TRANSFORM_FULL_FILENAME",
        r"C:\Users\MISP\Documents\dep_poc_delta_lake\Datastackv2\transform_database.duckdb"
    )
    return duckdb.connect(db_path, read_only=True)

@st.cache_data(ttl=300)
def load_standings():
    con = get_connection()
    return con.execute("SELECT * FROM gold_hockey_league_standings").fetchdf()

@st.cache_data(ttl=300)
def load_team_stats():
    con = get_connection()
    return con.execute("SELECT * FROM gold_hockey_team_stats").fetchdf()

@st.cache_data(ttl=300)
def load_programs():
    con = get_connection()
    return con.execute("SELECT * FROM silver_hockey_programs").fetchdf()

# ── CHARGEMENT ────────────────────────────────────────────────────────────────

try:
    df_standings = load_standings()
    df_stats     = load_team_stats()
    df_programs  = load_programs()
    data_ok = True
except Exception as e:
    st.error(f"Erreur connexion DuckDB : {e}")
    st.info("Lance d'abord :  . .\\load_env.ps1  puis  .\\run_hockey.ps1")
    data_ok = False
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 8px 0;'>
        <span style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#4FC3F7;letter-spacing:0.08em;'>
            🏑 HB Analytics
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Catégories disponibles
    categories = sorted(df_standings["league_category"].unique())
    selected_cat = st.selectbox("Compétition", categories,
                                 index=categories.index("MHL") if "MHL" in categories else 0)

    genders = ["Tous"] + sorted(df_standings["gender"].unique().tolist())
    selected_gender = st.selectbox("Genre", genders)

    surfaces = ["Tous", "OUTDOOR", "INDOOR"]
    selected_surface = st.selectbox("Surface", surfaces)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;color:#4A6080;'>
        <div>Source : hockey.be</div>
        <div>Pipeline : DLT → Delta → DBT</div>
    </div>
    """, unsafe_allow_html=True)

# ── FILTRES ───────────────────────────────────────────────────────────────────

def filter_df(df):
    mask = df["league_category"] == selected_cat
    if selected_gender != "Tous":
        mask &= df["gender"] == selected_gender
    if selected_surface != "Tous":
        mask &= df["surface"] == selected_surface
    return df[mask]

standings_f = filter_df(df_standings)
stats_f     = filter_df(df_stats)
programs_f  = filter_df(df_programs) if "league_category" in df_programs.columns else df_programs

# ── HEADER ────────────────────────────────────────────────────────────────────

col_title, col_logo = st.columns([4, 1])
with col_title:
    st.markdown(f"""
    <div class='hb-title'>Hockey Belgium</div>
    <div class='hb-subtitle'>Analytics Dashboard &nbsp;·&nbsp; {selected_cat}</div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────

n_teams   = len(standings_f["team_name"].unique()) if not standings_f.empty else 0
n_matches = len(programs_f) if not programs_f.empty else 0
n_future  = len(programs_f[programs_f["match_status"] == "FUTURE"]) if not programs_f.empty else 0

if not standings_f.empty:
    leader = standings_f.loc[standings_f["calculated_rank"] == 1, "team_name"].iloc[0] if len(standings_f[standings_f["calculated_rank"] == 1]) > 0 else "-"
    avg_goals = round(standings_f["goals_per_match"].mean(), 1)
else:
    leader, avg_goals = "-", 0

k1, k2, k3, k4, k5 = st.columns(5)
for col, val, label in [
    (k1, n_teams,   "Équipes"),
    (k2, n_matches, "Matchs total"),
    (k3, n_future,  "Matchs à venir"),
    (k4, avg_goals, "Buts/match moy."),
    (k5, leader,    "Leader"),
]:
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{val}</div>
            <div class='kpi-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Classement",
    "🎯  Profils Tactiques",
    "📅  Calendrier",
    "📈  Analyse",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — CLASSEMENT
# ═══════════════════════════════════════════════════════════════
with tab1:
    if standings_f.empty:
        st.warning("Aucune donnée pour cette sélection.")
    else:
        # Pools disponibles dans cette catégorie
        pools = sorted(standings_f["pool_name"].unique())
        if len(pools) > 1:
            selected_pool = st.selectbox("Poule", ["Toutes"] + pools)
            if selected_pool != "Toutes":
                standings_f = standings_f[standings_f["pool_name"] == selected_pool]

        # Tableau classement
        display_cols = {
            "calculated_rank": "Rang",
            "team_name":        "Équipe",
            "played":           "J",
            "wins":             "V",
            "draws":            "N",
            "losses":           "D",
            "goals_for":        "BP",
            "goals_against":    "BC",
            "goal_diff":        "Diff",
            "points":           "Pts",
            "win_pct":          "% Vic",
            "goals_per_match":  "Buts/M",
        }
        cols_available = [c for c in display_cols if c in standings_f.columns]
        df_display = standings_f[cols_available].rename(columns=display_cols)
        df_display = df_display.sort_values("Rang")

        st.markdown("<div class='section-title'>Classement général</div>", unsafe_allow_html=True)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rang":   st.column_config.NumberColumn(width="small"),
                "% Vic":  st.column_config.ProgressColumn("% Vic", min_value=0, max_value=100, format="%.1f%%"),
                "Pts":    st.column_config.NumberColumn(width="small"),
            }
        )

        # Bar chart points
        st.markdown("<div class='section-title'>Points par équipe</div>", unsafe_allow_html=True)
        fig = px.bar(
            df_display.sort_values("Pts", ascending=True).tail(15),
            x="Pts", y="Équipe", orientation="h",
            color="Pts",
            color_continuous_scale=["#1A3A5C", "#4FC3F7"],
            template="plotly_dark",
        )
        fig.update_layout(
            plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=420,
            yaxis=dict(tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 — PROFILS TACTIQUES
# ═══════════════════════════════════════════════════════════════
with tab2:
    if stats_f.empty:
        st.warning("Aucune donnée pour cette sélection.")
    else:
        st.markdown("<div class='section-title'>Quadrant Attaque / Défense</div>", unsafe_allow_html=True)
        st.caption("Positionnement des équipes selon leur profil offensif et défensif")

        col_chart, col_legend = st.columns([3, 1])

        with col_chart:
            color_map = {
                "DOMINANT":  "#4ADE80",
                "OFFENSIVE": "#FB923C",
                "DEFENSIVE": "#60A5FA",
                "BALANCED":  "#A78BFA",
            }
            profile_col = "tactical_profile" if "tactical_profile" in stats_f.columns else None
            color_col   = profile_col if profile_col else None

            fig2 = px.scatter(
                stats_f,
                x="avg_goals_per_match",
                y="avg_conceded_per_match",
                size="avg_win_pct",
                color=color_col,
                color_discrete_map=color_map,
                hover_name="team_name",
                hover_data={
                    "avg_win_pct": ":.1f",
                    "avg_goals_per_match": ":.2f",
                    "avg_conceded_per_match": ":.2f",
                },
                labels={
                    "avg_goals_per_match":    "Buts marqués / match",
                    "avg_conceded_per_match": "Buts encaissés / match",
                    "tactical_profile":       "Profil",
                },
                template="plotly_dark",
                size_max=40,
            )
            # Lignes de référence
            avg_scored   = stats_f["avg_goals_per_match"].mean()
            avg_conceded = stats_f["avg_conceded_per_match"].mean()
            fig2.add_vline(x=avg_scored,   line_dash="dash", line_color="#334155", line_width=1)
            fig2.add_hline(y=avg_conceded, line_dash="dash", line_color="#334155", line_width=1)

            # Labels quadrants
            x_max = stats_f["avg_goals_per_match"].max() * 1.05
            y_max = stats_f["avg_conceded_per_match"].max() * 1.05
            for text, x, y, color in [
                ("DOMINANT",  avg_scored * 0.3,  avg_conceded * 0.3, "#4ADE80"),
                ("OFFENSIVE", x_max * 0.9,       avg_conceded * 0.3, "#FB923C"),
                ("VULNÉRABLE",avg_scored * 0.3,  y_max * 0.9,        "#F87171"),
                ("ÉQUILIBRÉ", x_max * 0.9,       y_max * 0.9,        "#A78BFA"),
            ]:
                fig2.add_annotation(
                    x=x, y=y, text=text,
                    showarrow=False,
                    font=dict(color=color, size=10, family="DM Sans"),
                    opacity=0.5,
                )

            fig2.update_layout(
                plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                margin=dict(l=10, r=10, t=10, b=10),
                height=420,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            )
            st.plotly_chart(fig2, use_container_width=True)

        with col_legend:
            st.markdown("<br><br>", unsafe_allow_html=True)
            for profile, color, desc in [
                ("DOMINANT",  "#4ADE80", "Marque beaucoup, encaisse peu"),
                ("OFFENSIVE", "#FB923C", "Marque beaucoup, encaisse aussi"),
                ("DEFENSIVE", "#60A5FA", "Marque peu, encaisse peu"),
                ("BALANCED",  "#A78BFA", "Profil équilibré"),
            ]:
                st.markdown(f"""
                <div style='margin-bottom:12px;'>
                    <span style='background:{color}22;color:{color};padding:3px 8px;
                    border-radius:4px;font-size:0.75rem;font-weight:600;'>{profile}</span>
                    <div style='font-size:0.75rem;color:#8A9BB5;margin-top:4px;'>{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        # Tableau performance tier
        st.markdown("<div class='section-title'>Performance Tier</div>", unsafe_allow_html=True)
        if "performance_tier" in stats_f.columns:
            tier_counts = stats_f["performance_tier"].value_counts().reset_index()
            tier_counts.columns = ["Tier", "Équipes"]
            tier_order = ["TOP", "GOOD", "MID", "BOTTOM"]
            tier_counts["Tier"] = pd.Categorical(tier_counts["Tier"], categories=tier_order, ordered=True)
            tier_counts = tier_counts.sort_values("Tier")

            colors_tier = {"TOP": "#4ADE80", "GOOD": "#60A5FA", "MID": "#FBBF24", "BOTTOM": "#F87171"}
            fig3 = px.bar(
                tier_counts, x="Tier", y="Équipes",
                color="Tier", color_discrete_map=colors_tier,
                template="plotly_dark",
            )
            fig3.update_layout(
                plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
            )
            st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3 — CALENDRIER
# ═══════════════════════════════════════════════════════════════
with tab3:
    if programs_f.empty:
        st.warning("Aucune donnée calendrier pour cette sélection.")
    else:
        col_f, col_p = st.columns(2)

        with col_f:
            st.markdown("<div class='section-title'>Prochains matchs</div>", unsafe_allow_html=True)
            future = programs_f[programs_f["match_status"] == "FUTURE"].sort_values("match_date")
            if future.empty:
                st.info("Aucun match à venir.")
            else:
                pools_cal = ["Toutes"] + sorted(future["pool_name"].unique().tolist())
                pool_sel  = st.selectbox("Filtrer par poule", pools_cal, key="cal_pool")
                if pool_sel != "Toutes":
                    future = future[future["pool_name"] == pool_sel]

                for _, row in future.head(20).iterrows():
                    date_str = pd.to_datetime(row["match_date"]).strftime("%d/%m/%Y") if pd.notna(row.get("match_date")) else "?"
                    home = row.get("home_club", row.get("home_team", "?"))
                    away = row.get("away_club", row.get("away_team", "?"))
                    time = row.get("match_time", "")
                    st.markdown(f"""
                    <div style='background:#111E2E;border:1px solid #1E2D42;border-radius:8px;
                                padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:12px;'>
                        <span style='color:#4FC3F7;font-size:0.8rem;min-width:80px;'>{date_str}</span>
                        <span style='color:#E2E8F0;font-size:0.88rem;flex:1;text-align:right;'>{home}</span>
                        <span style='color:#4A6080;font-size:0.75rem;padding:2px 8px;'>vs</span>
                        <span style='color:#E2E8F0;font-size:0.88rem;flex:1;'>{away}</span>
                        <span style='color:#4A6080;font-size:0.78rem;'>{str(time)[:5] if time else ""}</span>
                    </div>
                    """, unsafe_allow_html=True)

        with col_p:
            st.markdown("<div class='section-title'>Matchs passés</div>", unsafe_allow_html=True)
            past = programs_f[programs_f["match_status"] == "PAST"].sort_values("match_date", ascending=False)
            if past.empty:
                st.info("Aucun match passé.")
            else:
                for _, row in past.head(15).iterrows():
                    date_str = pd.to_datetime(row["match_date"]).strftime("%d/%m/%Y") if pd.notna(row.get("match_date")) else "?"
                    home = row.get("home_club", row.get("home_team", "?"))
                    away = row.get("away_club", row.get("away_team", "?"))
                    st.markdown(f"""
                    <div style='background:#0F1923;border:1px solid #162030;border-radius:8px;
                                padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:12px;opacity:0.7;'>
                        <span style='color:#4A6080;font-size:0.8rem;min-width:80px;'>{date_str}</span>
                        <span style='color:#8A9BB5;font-size:0.88rem;flex:1;text-align:right;'>{home}</span>
                        <span style='color:#2A3A4A;font-size:0.75rem;padding:2px 8px;'>vs</span>
                        <span style='color:#8A9BB5;font-size:0.88rem;flex:1;'>{away}</span>
                    </div>
                    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 4 — ANALYSE
# ═══════════════════════════════════════════════════════════════
with tab4:
    if standings_f.empty:
        st.warning("Aucune donnée pour cette sélection.")
    else:
        st.markdown("<div class='section-title'>Distribution des buts</div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig4 = px.histogram(
                standings_f, x="goals_per_match", nbins=15,
                title="Buts marqués / match",
                template="plotly_dark",
                color_discrete_sequence=["#4FC3F7"],
            )
            fig4.update_layout(
                plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                margin=dict(l=10, r=10, t=40, b=10), height=280,
                showlegend=False,
            )
            st.plotly_chart(fig4, use_container_width=True)

        with col_b:
            fig5 = px.histogram(
                standings_f, x="conceded_per_match", nbins=15,
                title="Buts encaissés / match",
                template="plotly_dark",
                color_discrete_sequence=["#F87171"],
            )
            fig5.update_layout(
                plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                margin=dict(l=10, r=10, t=40, b=10), height=280,
                showlegend=False,
            )
            st.plotly_chart(fig5, use_container_width=True)

        # Top scoreurs (équipes)
        st.markdown("<div class='section-title'>Top équipes — Buts marqués</div>", unsafe_allow_html=True)
        top_scorers = standings_f.nlargest(10, "goals_for")[["team_name", "goals_for", "goals_against", "goal_diff"]]
        top_scorers.columns = ["Équipe", "Buts pour", "Buts contre", "Différence"]

        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            name="Buts pour", x=top_scorers["Équipe"], y=top_scorers["Buts pour"],
            marker_color="#4FC3F7",
        ))
        fig6.add_trace(go.Bar(
            name="Buts contre", x=top_scorers["Équipe"], y=top_scorers["Buts contre"],
            marker_color="#F87171",
        ))
        fig6.update_layout(
            barmode="group",
            plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
            template="plotly_dark",
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig6, use_container_width=True)

        # Corrélation points / buts
        st.markdown("<div class='section-title'>Corrélation Points ↔ Buts marqués</div>", unsafe_allow_html=True)
        fig7 = px.scatter(
            standings_f,
            x="goals_for", y="points",
            hover_name="team_name",
            trendline="ols",
            template="plotly_dark",
            color_discrete_sequence=["#4FC3F7"],
            labels={"goals_for": "Buts marqués", "points": "Points"},
        )
        fig7.update_layout(
            plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
        )
        st.plotly_chart(fig7, use_container_width=True)
