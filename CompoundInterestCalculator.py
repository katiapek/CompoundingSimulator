import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def calculate_expectancy(win_probability, win_reward):
    return round(win_probability / 100 * win_reward - (1-win_probability/100), 2)


def calculate_kelly_criterion(win_probability, win_reward):
    win_decimal = win_probability / 100
    loss_decimal = 1 - win_decimal
    return round((win_decimal-(loss_decimal/win_reward)), 4)


# Page headers
st.set_page_config(page_title="Compound Interest Calculator", layout="wide", page_icon="📈")

st.title("Compound Calculator")
st.markdown("""
**Explain what the app does**  
*Explain it even more*
""")

# Sidebar with information
with st.sidebar:
    st.header("About Compound Interest")
    st.subheader("Compounded Interest Formula")
    st.markdown("""
    ```
    like that:
    E = (W × R) - (1 - W)*1
    ```
    - **W** = Win probability (decimal, 0-1)
    - **R** = Reward to Risk ratio (multiple of risk)
    - **1-W** = Loss probability
    - **1** = Avg Loss (always 1R)
    """)

    st.markdown("---")
    st.markdown("For More Tools Visit: \n\n"
                "[ClockTrades - Free Trading Tools]"
                "(https://clocktrades.com/free-trading-tools/)")
    st.markdown("*For educational purposes only*")


# Expectancy Section

col1, col2 = st.columns(2)
with col1:
    st.header("🧮 Strategy Parameters")
    win_probability_pct = st.slider(
        "**Win Probability (%)**",
        min_value=1,
        max_value=100,
        value=40,
        help="Percentage of trades that are winners"
    )

    win_reward_R = st.slider(
        "**Reward to Risk Ratio**",
        min_value=0.1,
        max_value=20.0,
        value=2.0,
        step=0.1,
        help="Profit potential relative to your risk (e.g., 2.0 = 2:1 ratio)"
    )

    expectancy = calculate_expectancy(win_probability_pct, win_reward_R)

    # Color-coded expectancy display
    if expectancy >= 0:
        exp_color = "green"
        exp_icon = "✅"
    else:
        exp_color = "red"
        exp_icon = "⚠️"

    st.markdown(f"<h3 style='text-align: center; color: {exp_color};'>"
                f"{exp_icon} Expectancy: <b>{expectancy}R</b> per trade </h3>",
                unsafe_allow_html=True)

with col2:
    st.header("📊 Projected Returns")

    no_of_opportunities_per_period = st.slider(
        "**Opportunities per Period**",
        min_value=1,
        max_value=100,
        value=10,
        help="Number of trading opportunities in a given time period"
    )

    no_of_periods = st.slider(
        "**Number of Periods**",
        min_value=1,
        max_value=100,
        value=12,
        help="Number of periods to project forward"
    )

    total_return = round(expectancy * no_of_opportunities_per_period * no_of_periods, 1)

    # Color-coded total return display
    return_color = "green" if total_return >= 0 else "red"
    st.markdown(f"<h3 style='text-align: center; color: {return_color};'>"
                f"Total Return: <b>{total_return}R</b></h3>",
                unsafe_allow_html=True)

# Kelly Criterion section
st.markdown("#")
st.header("⚖️ Risk Management - Position Sizing")
kelly_container = st.container()

with kelly_container:
    kelly_percentage = calculate_kelly_criterion(win_probability_pct, win_reward_R) * 100
    display_kelly = max(0, kelly_percentage)

    if display_kelly > 20:
        # kelly_color = 'red'
        risk_advice = 'Aggressive'
    elif display_kelly > 10:
        # kelly_color = 'orange'
        risk_advice = 'Moderately Aggressive'
    elif display_kelly > 5:
        # kelly_color = 'teal'
        risk_advice = 'Moderate'
    else:
        # kelly_color = 'green'
        risk_advice = 'Conservative'

col3, col4 = st.columns(2)
with col3:
    st.subheader("Kelly Criterion")
    st.metric(
        "Optimal Risk",
        f"{display_kelly:.2f}%",
        help="Theoretical maximum % of capital to risk per trade"
    )
    st.metric(
        "Risk level",
        risk_advice
    )

with col4:
    st.subheader("Safer approach")
    st.metric(
        "Half-Kelly",
        f"{display_kelly/2:.2f}%",
        help="Common recommended practice to reduce volatility"
    )
    st.metric("Most common recommendation",
              "1-2%",
              help="Standard risk management guideline")


# Visualisation section
st.markdown("#")
st.header("📈 Expectancy Analysis")
st.markdown("""
**Visualizing how win rate and Reward to Risk ratio relate for the same expectancy**  
*The curves below show alternative parameter combinations that yield the same expectancy*
""")

# Present data in the container with tabs - one for chart, one for data table
chart_container = st.container()
with chart_container:
    # Generate data - for each win rate 1-99 find R required to maintain expectancy
    if expectancy > 0:
        win_rates = list(range(5, 100))
        R_required = []
        kelly_values = []

        # For each win rate calculate R
        for wr in win_rates:
            R_val = (expectancy + 1) * (100 / wr) - 1
            if R_val > 0:
                R_required.append(R_val)
                kelly_values.append(calculate_kelly_criterion(wr, R_val) * 100)

        # Create a plot with two y-axis
        fig = make_subplots(specs=[[{'secondary_y': True}]])

        # Add R curve
        fig.add_trace(
            go.Scatter(
                x=win_rates,
                y=R_required,
                mode='lines',
                name='Reward to Risk Ratio',
                line=dict(color='#1f77b4', width=3),
                hovertemplate="Required R: %{y:.2f}<extra></extra>",
            ),
            secondary_y=False,
        )

        # Add Kelly curve
        fig.add_trace(
            go.Scatter(
                x=win_rates,
                y=kelly_values,
                mode='lines',
                name='Kelly Criterion %',
                line=dict(color='#ff7f0e', width=3, dash='dot'),
                hovertemplate="Kelly Criterion %: %{y:.2f}%<extra></extra>",
            ),
            secondary_y=True
        )

        # Setting titles
        fig.update_layout(
            title=f"Parameter Combinations for Expectancy = {expectancy}R",
            xaxis_title="Win Rate (%)",
            yaxis_title="Reward to Risk Ratio",
            yaxis2_title="Kelly Criterion %",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            yaxis2=dict(showgrid=False),
            hovermode='x',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            template='plotly_white'
        )

        st.plotly_chart(fig, config={'displayModeBar': False}, use_container_width=True)
    else:
        st.warning("This expectancy value is not mathematically possible with positive risk:reward ratios")

# Explanation section
with st.expander("💡 How to interpret these results"):
    st.markdown(f"""
    With a **{win_probability_pct}% win rate** and **{win_reward_R} : 1 reward-to-risk ratio**:

    - Your expectancy is **{expectancy}R** per trade
    - This means you'll average **&dollar;{expectancy} per &dollar;1 risked** over many trades
    - With **{no_of_opportunities_per_period} trades per period** over **{no_of_periods} periods**:
        - Total projected return = **{total_return}R**
        - This equals **&dollar;{total_return} per &dollar;1 risked** overall
    """)

    st.markdown("""
    **Key Insights:**
    - Positive expectancy (>0) indicates a profitable strategy
    - Expectancy > 0.2 is generally considered good
    - Expectancy > 0.5 is considered excellent
    - Negative expectancy means the strategy loses money over time
    """)

    st.subheader("Position Sizing")
    st.markdown(f"""
        For your strategy parameters:

        - **Kelly Criterion** suggests risking **{display_kelly:.2f}%** of capital per trade
        - **Half-Kelly** approach recommends **{display_kelly / 2:.2f}%** per trade
        - Most risk managers recommend **never risking more than 1-2%** per trade

        *Why the differences?*
        - Kelly Criterion maximizes long-term growth but assumes perfect knowledge
        - Real trading has uncertainty, so most traders use fractional Kelly
        - Conservative sizing protects against black swan events and estimation errors
        """)


# Footer
st.markdown("---")
st.caption("© 2025 ClockTrades.com • All calculations are theoretical and don't guarantee future results • "
           "Risk management is essential in trading")
