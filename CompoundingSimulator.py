import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set page headers
st.set_page_config(page_title="Trading Strategy Compounding Simulator", layout="wide", page_icon="📈")

# Custom CSS
st.markdown("""
<style>
.main {background-color: #f5f5f5;}
h1 {color: #1e3a8a; font-family: 'Arial', sans-serif;}
h2 {color: #1e3a8a;}
.stButton>button {background-color: #2563eb; color: white; border-radius: 5px;}
.stSlider .st-bx {background-color: #bfdbfe;}
</style>
""", unsafe_allow_html=True)


def calculate_expectancy(win_probability: float, win_reward: float) -> float:
    """
    Calculate the average expected return (expected value) per trade.

    Args:
        win_probability (float): Chance of winning (0–100).
        win_reward (float): Reward-to-risk ratio (e.g., 2 means 2:1).

    Returns:
        float: Expectancy value, rounded to 2 decimals.
               Positive = profitable on average, negative = losing.
    """
    return round(win_probability / 100 * win_reward - (1 - win_probability / 100), 2)


def calculate_kelly_criterion(win_probability: float, win_reward: float) -> float:
    """
    Calculate the Kelly Criterion position sizing fraction.

    Args:
        win_probability (float): Probability of winning, as a percentage (0–100).
        win_reward (float): Reward-to-risk ratio (e.g., 2 means 2:1).

    Returns:
        float: Fraction of capital to risk per trade, rounded to 4 decimals.
    """
    win_decimal = win_probability / 100
    loss_decimal = 1 - win_decimal
    return round((win_decimal - (loss_decimal / win_reward)), 4)


# Start page with the title and description
st.title("💸 Trading Strategy Compounding Simulator")
st.markdown("""
**Visualize how compounding affects your trading results over time**  
*This calculator simulates the growth of your trading account based on your strategy parameters and risk management rules*
""")

# Sidebar with information
# Sidebar
with st.sidebar:
    st.header("About Compounding")
    st.markdown("""
    **Formula**: `A = P × (1 + r/n)^(n×t)`
    - **A**: Ending balance
    - **P**: Starting balance
    - **r**: Expected return per period (based on expectancy)
    - **n**: Number of compounding periods per cycle
    - **t**: Number of cycles

    In trading, we compound the **risk per trade** (adjusted as a percentage of the account balance), factoring in wins, losses, taxes, and cash flows.
    """)
    st.markdown("---")
    st.markdown("For more Free Tools Visit:")
    st.markdown("[ClockTrades.com - Free Trading Tools](https://clocktrades.com/free-trading-tools/)")
    st.caption("*For educational purposes only*")


# Trading System Setup Section - create two columns
# Left column for Strategy setup
# Right column for Account Management settings
col1, col2 = st.columns(2)
with col1:
    st.header("🧮 Strategy Setup")
    st.subheader("Trading System")

    # Slider for strategy win rate setting
    win_probability_pct = st.slider(
        "**Win Probability (%)**",
        min_value=1,
        max_value=100,
        value=40,
        help="Percentage of trades that are winners"
    )

    # Slider for strategy avg R multiple reward setting
    win_reward_R = st.slider(
        "**Reward to Risk Ratio**",
        min_value=0.1,
        max_value=20.0,
        value=2.0,
        step=0.1,
        help="Profit potential relative to your risk (e.g., 2.0 = 2:1 ratio)"
    )

    # User sets expected number of opportunities/trades per period
    st.subheader("Time Horizon")
    no_of_opportunities_per_period = st.slider(
        "**Opportunities per Period**",
        min_value=1,
        max_value=100,
        value=10,
        help="Number of trading opportunities in a given time period"
    )

    # User sets how many periods are in cycle
    # Usecase: if traders works finds opportunities daily they
    # may be interested in tracking 20 periods per cycle (20 days in a month - no weekends)
    # if weekly they may track 50 periods in a cycle (50 weeks in a year - excluding holiday weeks approx.)
    no_of_periods = st.slider(
        "**Periods per Cycle**",
        min_value=1,
        max_value=200,
        value=12,
        help="Number of periods in each cycle (e.g., months in a year)"
    )

    no_of_cycles = st.slider(
        "**Number of Cycles**",
        min_value=1,
        max_value=50,
        value=30,
        help="Total cycles to simulate (e.g., years)"
    )

with col2:
    st.header("💰Account Management")
    # Use list as an input for Period or Cycle choice
    period_cycle_choice = ["Period", "Cycle"]

    # Container for account balance - we want to know starting balance and the users target
    with st.container():
        st.subheader("Capital Setup")
        col_balance_1, col_balance_2 = st.columns(2)
        with col_balance_1:
            starting_account_balance = st.number_input(
                "Starting Account Balance",
                min_value=500,
                max_value=1000000,
                value=1000,
                help="Initial trading capital"
            )
        with col_balance_2:
            ending_account_balance = st.number_input(
                "Ending Account Balance",
                min_value=int(starting_account_balance),  # min value cannot be below starting balance
                max_value=100000000,
                value=max(1000000, int(starting_account_balance)),
                help="Financial target"
            )

    # We want to know if user wants to add funds to the account per period or cycle
    with st.container():
        st.subheader("Cash Flows")
        col_add_1, col_add_2 = st.columns(2)
        with col_add_1:
            add_to_account_value = st.number_input(
                "Regular Contributions($)",
                min_value=0,
                max_value=10000,
                value=0,
                help="Amount added to account regularly"
            )
        with col_add_2:
            add_to_account_period = st.segmented_control(
                "Contribution Frequency",
                period_cycle_choice,
                key="Add period",
                help="When contributions are made"
            )

    # We want to know if user withdraw funds from the account per period or cycle
    with st.container():
        col_withdraw_1, col_withdraw_2 = st.columns(2)
        with col_withdraw_1:
            withdraw_from_account_value = st.number_input(
                "Regular Withdrawals ($)",
                min_value=0,
                max_value=10000,
                value=0,
                help="Amount withdrawn from account regularly"
            )
        with col_withdraw_2:
            withdraw_from_account_period = st.segmented_control(
                "Withdrawal Frequency",
                period_cycle_choice,
                key="Withdraw period",
                help="User wants to withdraw certain amount of money to the account per Period or Cycle"
            )

    # Tax rate
    with st.container():
        st.subheader("Risk & Tax Management")
        col_tax_1, col_tax_2 = st.columns(2)
        with col_tax_1:
            tax_value_pct = st.slider(
                "Capital Gains Tax",
                min_value=0,
                max_value=100,
                value=0,
                step=1,
                help="Tax rate on profits"
            )
        with col_tax_2:
            tax_period = st.segmented_control(
                "Pay Tax every:",
                period_cycle_choice,
                key="Tax period",
                help="When taxes are paid"
            )

    # Risk Management
    with st.container():

        col_risk_1, col_risk_2 = st.columns(2)
        with col_risk_1:
            user_risk_pct = st.number_input(
                "Risk per trade as a % of bankroll",
                min_value=0.1,
                max_value=100.00,
                value=2.0,
                step=0.1,
                help="Percentage of capital risked per trade"
            )
        with col_risk_2:
            user_risk_adj_period = st.segmented_control(
                "Adjust Risk every:",
                period_cycle_choice,
                key="Adjust risk period",
                help="When risk percentage is recalculated"
            )

# Calculations section:
expectancy = calculate_expectancy(win_probability_pct, win_reward_R)
r_return_per_period = round(expectancy * no_of_opportunities_per_period, 1)
kelly_percentage = calculate_kelly_criterion(win_probability_pct, win_reward_R) * 100
kelly_percentage = max(0.0, kelly_percentage)

# Strategy Summary
strategy_container = st.container()

with strategy_container:
    st.header("📊 Strategy Performance Summary")
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    with col_metric1:
        st.metric("Expectancy per Trade", f"{expectancy}R", help="Average return per $1 risked")
    with col_metric2:
        st.metric("Period Return", f"{r_return_per_period}R", help="Total return per period")
    with col_metric3:
        st.metric("Kelly Criterion", f"{kelly_percentage:.2f}%", help="Optimal risk percentage")
    with col_metric4:
        risk_comparison = "✅ Below Kelly" if user_risk_pct < kelly_percentage else "⚠️ Above Kelly"
        st.metric("Your Risk Level", f"{user_risk_pct}%", risk_comparison)


# Visualisation section
visualisation_container = st.container()
with visualisation_container:
    st.header("🚀 Compounding Growth Simulation")
    st.markdown("""
    **Visualizing how your trading strategy compounds over time**  
    *The chart below shows your account growth trajectory based on the parameters you've set*
    """)

    # Present data in tabs - one for table and one for chart
    tab1, tab2 = st.tabs(["DataTable", "Chart"])
    with tab1:
        # Create DataFrame for the compound rate results
        compound_interest_result_df = pd.DataFrame()
        # Take start balance before entering the loop
        start_balance = starting_account_balance
        # Set the initial risk before entering the loop
        risk_per_trade = round(start_balance * user_risk_pct / 100, 0)

        # Enter the loop - cycles contains periods
        for cycle in range(1, no_of_cycles+1):
            return_per_cycle = []

            for period in range(1, no_of_periods+1):
                # Work only until the account target has been reached
                if (start_balance >= ending_account_balance) or (start_balance <= 0):
                    break
                # Adjust risk if user adapts risk per cycle or per period in other cases or never it nothing is chosen
                if (period == 1) and (user_risk_adj_period == "Cycle"):
                    risk_per_trade = round(start_balance * user_risk_pct / 100, 0)
                elif user_risk_adj_period == "Period":
                    risk_per_trade = round(start_balance * user_risk_pct / 100, 0)
                else:
                    risk_per_trade = risk_per_trade

                # Calculations required per period
                return_on_period = r_return_per_period * risk_per_trade
                return_per_cycle.append(return_on_period)
                tax_withheld = round(return_on_period * tax_value_pct / 100, 0) if tax_period == "Period" else 0
                add_to_account = add_to_account_value if add_to_account_period == "Period" else 0
                withdraw_from_account = withdraw_from_account_value if withdraw_from_account_period == "Period" else 0

                # Calculations required if user choose Cycle in some cases rather than Period
                if period == no_of_periods:
                    add_to_account = add_to_account_value if add_to_account_period == "Cycle" else add_to_account
                    withdraw_from_account = withdraw_from_account_value if withdraw_from_account_period == "Cycle" else withdraw_from_account
                    tax_withheld = sum(return_per_cycle) * tax_value_pct / 100 if tax_period == "Cycle" else tax_withheld

                end_balance = round(start_balance + return_on_period + add_to_account - withdraw_from_account - tax_withheld, 0)

                # Create new row per each period and later concatenate it with the existing DataFrame
                new_row_df = pd.DataFrame(
                    {
                        "Cycle": cycle,
                        "Period": period,
                        "Starting Balance": start_balance,
                        "Risk": risk_per_trade,
                        "Return": return_on_period,
                        "Added": add_to_account,
                        "Withdrawn": withdraw_from_account,
                        "Tax": tax_withheld,
                        "Ending Balance": end_balance
                    },
                    index=[0])
                compound_interest_result_df = pd.concat([compound_interest_result_df, new_row_df], ignore_index=True)
                start_balance = end_balance

        # Show DataFrame
        st.dataframe(
            compound_interest_result_df.style.format(
                {
                    "Starting Balance": "${:,.0f}",
                    "Risk": "${:,.0f}",
                    "Return": "${:,.0f}",
                    "Added": "${:,.0f}",
                    "Withdrawn": "${:,.0f}",
                    "Tax": "${:,.0f}",
                    "Ending Balance": "${:,.0f}"
                }
            ),
            hide_index=True, width='content')

    with tab2:
        # Present data in the container with tabs - one for chart, one for data table
        # Use plotly fig

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=compound_interest_result_df.index,
            y=compound_interest_result_df["Ending Balance"],
            mode="lines",
            line=dict(color='#3498db', width=3),
            hovertemplate="Cycle: %{customdata[0]}<br>Period: %{customdata[1]}<br>Balance: $%{y:,.0f}<extra></extra>",
            customdata=compound_interest_result_df[["Cycle", "Period"]],

        ))

        # Target line
        fig.add_hline(
            y=ending_account_balance,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Target: ${ending_account_balance:,.0f}",
            annotation_position="bottom right"
        )

        # Update layout
        fig.update_layout(
            title="Account Growth Over Time",
            xaxis_title="Period Sequence",
            yaxis_title="Account Balance ($)",
            hovermode="x unified",
            template="plotly_white",

        )
        st.plotly_chart(fig, config={"displayModeBar": False}, use_container_width=True)
        # else:
        #     st.warning("This expectancy value is not mathematically possible with positive risk:reward ratios")


# Explanation
with st.expander("💡 How to Interpret These Results"):
    st.markdown(f"""
    Your trading strategy's performance is modeled using the **compound interest formula** adapted for trading risk:

    **Formula**: `A = P × (1 + r/n)^(n×t)`
    - **A**: Ending balance
    - **P**: Starting balance ({starting_account_balance:,.0f})
    - **r**: Expected return per period ({r_return_per_period:.1f}R)
    - **n**: Opportunities per period ({no_of_opportunities_per_period})
    - **t**: Total periods ({no_of_periods * no_of_cycles})

    **Key Insights**:
    - **Expectancy**: {expectancy:.2f}R per trade
    - **Kelly Criterion**: Risk {kelly_percentage:.2f}% per trade (half-Kelly: {kelly_percentage/2:.2f}%)
    - **Ending Balance**: {compound_interest_result_df['Ending Balance'].iloc[-1]:,.0f}
    - **Risk Management**: Adjust risk per {user_risk_adj_period} for balance.
    """)


# Footer
st.markdown("---")
st.caption("© 2025 ClockTrades.com • All calculations are theoretical and don't guarantee future results • "
           "Risk management is essential in trading")
