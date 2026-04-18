"""
Hockey Belgium Analytics Dashboard
====================================
Version Streamlit Cloud — lit les fichiers Parquet du repo
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.hb-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    letter-spacing: 0.08em;
    color: #F0F4FF;
    line-height: 1;
    margin-bottom: 0;
}
.hb-subtitle {
    font-size: 0.95rem;
    color: #8A9BB5;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
}
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
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 0.06em;
    color: #E2E8F0;
    border-left: 4px solid #4FC3F7;
    padding-left: 12px;
    margin: 24px 0 12px 0;
}
[data-testid="stSidebar"] { background: #0A1628; border-right: 1px solid #1E2D42; }
.main .block-container { background: #0D1B2A; padding-top: 1.5rem; }
hr { border-color: #1E2D42; }
</style>
""", unsafe_allow_html=True)

# ── CHARGEMENT PARQUET ────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

@st.cache_data
def load_data():
    standings = pd.read_parquet(os.path.join(DATA_DIR, "standings.parquet"))
    team_stats = pd.read_parquet(os.path.join(DATA_DIR, "team_stats.parquet"))
    programs = pd.read_parquet(os.path.join(DATA_DIR, "programs.parquet"))
    return standings, team_stats, programs

try:
    df_standings, df_stats, df_programs = load_data()
except Exception as e:
    st.error(f"Erreur chargement données : {e}")
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0;'>
        <span style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#4FC3F7;letter-spacing:0.08em;'>
            🏑 HB Analytics
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    categories = sorted(df_standings["league_category"].unique())
    selected_cat = st.selectbox("Compétition", categories,
                                index=categories.index("MHL") if "MHL" in categories else 0)

    genders = ["Tous"] + sorted(df_standings["gender"].dropna().unique().tolist())
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

st.markdown(f"""
<div class='hb-title'>Hockey Belgium</div>
<div class='hb-subtitle'>Analytics Dashboard &nbsp;·&nbsp; {selected_cat}</div>
""", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────

n_teams   = len(standings_f["team_name"].unique()) if not standings_f.empty else 0
n_matches = len(programs_f) if not programs_f.empty else 0
n_future  = len(programs_f[programs_f["match_status"] == "FUTURE"]) if not programs_f.empty else 0
leader    = standings_f.loc[standings_f["calculated_rank"] == 1, "team_name"].iloc[0] if not standings_f.empty and len(standings_f[standings_f["calculated_rank"] == 1]) > 0 else "-"
avg_goals = round(standings_f["goals_per_match"].mean(), 1) if not standings_f.empty else 0

for col, val, label in zip(
    st.columns(5),
    [n_teams, n_matches, n_future, avg_goals, leader],
    ["Équipes", "Matchs total", "Matchs à venir", "Buts/match moy.", "Leader"]
):
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
    "📊  Classement", "🎯  Profils Tactiques", "📅  Calendrier", "📈  Analyse"
])

# ── TAB 1 : CLASSEMENT ───────────────────────────────────────────────────────
with tab1:
    if standings_f.empty:
        st.warning("Aucune donnée pour cette sélection.")
    else:
        pools = sorted(standings_f["pool_name"].unique())
        if len(pools) > 1:
            sel_pool = st.selectbox("Poule", ["Toutes"] + pools)
            if sel_pool != "Toutes":
                standings_f = standings_f[standings_f["pool_name"] == sel_pool]

        display_cols = {
            "calculated_rank": "Rang", "team_name": "Équipe",
            "played": "J", "wins": "V", "draws": "N", "losses": "D",
            "goals_for": "BP", "goals_against": "BC", "goal_diff": "Diff",
            "points": "Pts", "win_pct": "% Vic", "goals_per_match": "Buts/M",
        }
        cols_ok = [c for c in display_cols if c in standings_f.columns]
        df_disp = standings_f[cols_ok].rename(columns=display_cols).sort_values("Rang")

        st.markdown("<div class='section-title'>Classement général</div>", unsafe_allow_html=True)
        st.dataframe(
            df_disp, hide_index=True, use_container_width=True,
            column_config={
                "% Vic": st.column_config.ProgressColumn("% Vic", min_value=0, max_value=100, format="%.1f%%"),
            }
        )

        st.markdown("<div class='section-title'>Points par équipe</div>", unsafe_allow_html=True)
        fig = px.bar(
            df_disp.sort_values("Pts", ascending=True).tail(15),
            x="Pts", y="Équipe", orientation="h",
            color="Pts", color_continuous_scale=["#1A3A5C", "#4FC3F7"],
            template="plotly_dark",
        )
        fig.update_layout(
            plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
            coloraxis_showscale=False, margin=dict(l=10,r=10,t=10,b=10), height=420
        )
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 2 : PROFILS TACTIQUES ────────────────────────────────────────────────
with tab2:
    if stats_f.empty:
        st.warning("Aucune donnée pour cette sélection.")
    else:
        st.markdown("<div class='section-title'>Quadrant Attaque / Défense</div>", unsafe_allow_html=True)
        col_chart, col_legend = st.columns([3, 1])

        with col_chart:
            color_map = {"DOMINANT": "#4ADE80", "OFFENSIVE": "#FB923C",
                         "DEFENSIVE": "#60A5FA", "BALANCED": "#A78BFA"}
            fig2 = px.scatter(
                stats_f, x="avg_goals_per_match", y="avg_conceded_per_match",
                size="avg_win_pct", color="tactical_profile",
                color_discrete_map=color_map, hover_name="team_name",
                labels={"avg_goals_per_match": "Buts marqués/match",
                        "avg_conceded_per_match": "Buts encaissés/match",
                        "tactical_profile": "Profil"},
                template="plotly_dark", size_max=40,
            )
            avg_s = stats_f["avg_goals_per_match"].mean()
            avg_c = stats_f["avg_conceded_per_match"].mean()
            fig2.add_vline(x=avg_s, line_dash="dash", line_color="#334155", line_width=1)
            fig2.add_hline(y=avg_c, line_dash="dash", line_color="#334155", line_width=1)
            fig2.update_layout(
                plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                margin=dict(l=10,r=10,t=10,b=10), height=420,
                legend=dict(bgcolor="rgba(0,0,0,0)"),
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

        st.markdown("<div class='section-title'>Performance Tier</div>", unsafe_allow_html=True)
        if "performance_tier" in stats_f.columns:
            tier_counts = stats_f["performance_tier"].value_counts().reset_index()
            tier_counts.columns = ["Tier", "Équipes"]
            colors_tier = {"TOP": "#4ADE80", "GOOD": "#60A5FA", "MID": "#FBBF24", "BOTTOM": "#F87171"}
            fig3 = px.bar(tier_counts, x="Tier", y="Équipes", color="Tier",
                          color_discrete_map=colors_tier, template="plotly_dark")
            fig3.update_layout(plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                               showlegend=False, margin=dict(l=10,r=10,t=10,b=10), height=280)
            st.plotly_chart(fig3, use_container_width=True)

# ── TAB 3 : CALENDRIER ───────────────────────────────────────────────────────
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
                pool_sel = st.selectbox("Filtrer par poule", pools_cal, key="cal_pool")
                if pool_sel != "Toutes":
                    future = future[future["pool_name"] == pool_sel]
                for _, row in future.head(20).iterrows():
                    date_str = pd.to_datetime(row["match_date"]).strftime("%d/%m/%Y") if pd.notna(row.get("match_date")) else "?"
                    home = row.get("home_club", row.get("home_team", "?"))
                    away = row.get("away_club", row.get("away_team", "?"))
                    time_val = str(row.get("match_time", ""))[:5]
                    st.markdown(f"""
                    <div style='background:#111E2E;border:1px solid #1E2D42;border-radius:8px;
                                padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:12px;'>
                        <span style='color:#4FC3F7;font-size:0.8rem;min-width:80px;'>{date_str}</span>
                        <span style='color:#E2E8F0;font-size:0.88rem;flex:1;text-align:right;'>{home}</span>
                        <span style='color:#4A6080;font-size:0.75rem;padding:2px 8px;'>vs</span>
                        <span style='color:#E2E8F0;font-size:0.88rem;flex:1;'>{away}</span>
                        <span style='color:#4A6080;font-size:0.78rem;'>{time_val}</span>
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

# ── TAB 4 : ANALYSE ──────────────────────────────────────────────────────────
with tab4:
    if standings_f.empty:
        st.warning("Aucune donnée pour cette sélection.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("<div class='section-title'>Buts marqués / match</div>", unsafe_allow_html=True)
            fig4 = px.histogram(standings_f, x="goals_per_match", nbins=15,
                                template="plotly_dark", color_discrete_sequence=["#4FC3F7"])
            fig4.update_layout(plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                               margin=dict(l=10,r=10,t=10,b=10), height=280, showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)

        with col_b:
            st.markdown("<div class='section-title'>Buts encaissés / match</div>", unsafe_allow_html=True)
            fig5 = px.histogram(standings_f, x="conceded_per_match", nbins=15,
                                template="plotly_dark", color_discrete_sequence=["#F87171"])
            fig5.update_layout(plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                               margin=dict(l=10,r=10,t=10,b=10), height=280, showlegend=False)
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("<div class='section-title'>Top équipes — Buts</div>", unsafe_allow_html=True)
        top10 = standings_f.nlargest(10, "goals_for")[["team_name", "goals_for", "goals_against"]]
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(name="Buts pour",   x=top10["team_name"], y=top10["goals_for"],  marker_color="#4FC3F7"))
        fig6.add_trace(go.Bar(name="Buts contre", x=top10["team_name"], y=top10["goals_against"], marker_color="#F87171"))
        fig6.update_layout(barmode="group", plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                           template="plotly_dark", margin=dict(l=10,r=10,t=10,b=10), height=320,
                           legend=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig6, use_container_width=True)

        st.markdown("<div class='section-title'>Corrélation Points ↔ Buts marqués</div>", unsafe_allow_html=True)
        fig7 = px.scatter(standings_f, x="goals_for", y="points", hover_name="team_name",
                          trendline="ols", template="plotly_dark",
                          color_discrete_sequence=["#4FC3F7"],
                          labels={"goals_for": "Buts marqués", "points": "Points"})
        fig7.update_layout(plot_bgcolor="#0D1B2A", paper_bgcolor="#0D1B2A",
                           margin=dict(l=10,r=10,t=10,b=10), height=300)
        st.plotly_chart(fig7, use_container_width=True)