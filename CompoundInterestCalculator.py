import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def calculate_expectancy(win_probability, win_reward):
    return round(win_probability / 100 * win_reward - (1-win_probability/100), 2)


def calculate_kelly_criterion(win_probability, win_reward):
    win_decimal = win_probability / 100
    loss_decimal = 1 - win_decimal
    return round((win_decimal-(loss_decimal/win_reward)), 4)


# Page headers
st.set_page_config(page_title="Compound Interest Calculator", layout="wide", page_icon="📈")

st.title("Compound Interest Calculator")
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


# Trading System Setup Section

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

    no_of_cycles = st.slider(
        "**Number of Cycles**",
        min_value=1,
        max_value=50,
        value=30,
        help="Number of cycles to project forward"
    )

with col2:
    st.header("📊 Position Size Setup")
    period_cycle_choice = ["Period", "Cycle"]

    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            starting_account_balance = st.number_input(
                "Starting Account Balance",
                min_value=500,
                max_value=500000,
            )
        with col_b:
            ending_account_balance = st.number_input(
                "Ending Account Balance",
                min_value=100000,
                max_value=100000000,
            )

    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            add_to_account_value = st.number_input("Add to account", min_value=0, max_value=10000)
        with col_b:
            add_to_account_period = st.segmented_control(
                "Added to account period",
                period_cycle_choice,
                key="Add period"
            )
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            withdraw_from_account_value = st.number_input("Withdraw from account", min_value=0, max_value=10000)
        with col_b:
            withdraw_from_account_period = st.segmented_control(
                "Withdrawn from account period",
                period_cycle_choice,
                key="Withdraw period"
            )

    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            tax_value_pct = st.slider("Capital Gains Tax", min_value=0, max_value=100)
        with col_b:
            tax_period = st.segmented_control(
                "Tax paid per period",
                period_cycle_choice,
                key="Tax period"
            )
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            user_risk_pct = st.number_input("Risk per trade as a % of bankroll", min_value=0.1, max_value=100.00)
        with col_b:
            user_risk_adj_period = st.segmented_control(
                "Adjust per period",
                period_cycle_choice,
                key="Adjust risk period")

# Calculations section:
expectancy = calculate_expectancy(win_probability_pct, win_reward_R)
r_return_per_period = round(expectancy * no_of_opportunities_per_period, 1)
kelly_percentage = calculate_kelly_criterion(win_probability_pct, win_reward_R) * 100
kelly_percentage = max(0, kelly_percentage)

# Strategy Summary
st.markdown("#")
st.header("⚖️ Strategy Summary")
strategy_obj_df = pd.DataFrame({
    "Win-Rate %": win_probability_pct,
    "R Ratio": win_reward_R,
    "Expectancy": expectancy,
    "Kelly Criterion": kelly_percentage,
    "User Risk %": user_risk_pct
}, index=[0])
st.dataframe(strategy_obj_df, hide_index=True)

strategy_container = st.container()


# Visualisation section
st.markdown("#")
st.header("📈 Expectancy Analysis")
st.markdown("""
**Visualizing how win rate and Reward to Risk ratio relate for the same expectancy**  
*The curves below show alternative parameter combinations that yield the same expectancy*
""")
tab1, tab2 = st.tabs(["DataTable", "Chart"])
with tab1:
    compound_interest_result_df = pd.DataFrame()
    start_balance = starting_account_balance
    risk_per_trade = start_balance * user_risk_pct / 100

    for cycle in range(no_of_cycles):
        return_per_cycle = []

        for period in range(no_of_periods):
            if start_balance >= ending_account_balance: break;
            if (period == 0) and (user_risk_adj_period == "Cycle"):
                risk_per_trade = start_balance * user_risk_pct / 100
            elif user_risk_adj_period == "Period":
                risk_per_trade = start_balance * user_risk_pct / 100
            else:
                risk_per_trade = risk_per_trade
            return_on_period = r_return_per_period * risk_per_trade
            return_per_cycle.append(return_on_period)
            tax_withheld = return_on_period * tax_value_pct / 100 if tax_period == "Period" else 0
            add_to_account = add_to_account_value if add_to_account_period == "Period"  else 0
            withdraw_from_account = withdraw_from_account_value if withdraw_from_account_period == "Period" else 0

            if period == no_of_periods-1:
                add_to_account = add_to_account_value if add_to_account_period == "Cycle" else 0
                withdraw_from_account = withdraw_from_account_value if withdraw_from_account_period == "Cycle" else 0
                tax_withheld = sum(return_per_cycle) * tax_value_pct / 100 if tax_period == "Cycle" else 0

            end_balance = start_balance + return_on_period + add_to_account - withdraw_from_account - tax_withheld

            new_row_df = pd.DataFrame(
                {
                    "Cycle": cycle+1,
                    "Period": period+1,
                    "Starting Balance": start_balance,
                    "Risk per trade": risk_per_trade,
                    "Return" : return_on_period,
                    "Added to account": add_to_account,
                    "Withdrawn from account": withdraw_from_account,
                    "Tax withheld" : tax_withheld,
                    "Ending Balance": end_balance
                },
                index=[0])
            compound_interest_result_df = pd.concat([compound_interest_result_df, new_row_df], ignore_index=True)
            start_balance = end_balance


    st.dataframe(compound_interest_result_df)

with tab2:
    # Present data in the container with tabs - one for chart, one for data table
    chart_container = st.container()
    with chart_container:
        st.line_chart(compound_interest_result_df, y=["Ending Balance"])
        # else:
        #     st.warning("This expectancy value is not mathematically possible with positive risk:reward ratios")


# Explanation section
# with st.expander("💡 How to interpret these results"):
#     st.markdown(f"""
#     With a **{win_probability_pct}% win rate** and **{win_reward_R} : 1 reward-to-risk ratio**:
#
#     - Your expectancy is **{expectancy}R** per trade
#     - This means you'll average **&dollar;{expectancy} per &dollar;1 risked** over many trades
#     - With **{no_of_opportunities_per_period} trades per period** over **{no_of_periods} periods**:
#         - Total projected return = **{total_return}R**
#         - This equals **&dollar;{total_return} per &dollar;1 risked** overall
#     """)
#
#     st.markdown("""
#     **Key Insights:**
#     - Positive expectancy (>0) indicates a profitable strategy
#     - Expectancy > 0.2 is generally considered good
#     - Expectancy > 0.5 is considered excellent
#     - Negative expectancy means the strategy loses money over time
#     """)
#
#     st.subheader("Position Sizing")
#     st.markdown(f"""
#         For your strategy parameters:
#
#         - **Kelly Criterion** suggests risking **{display_kelly:.2f}%** of capital per trade
#         - **Half-Kelly** approach recommends **{display_kelly / 2:.2f}%** per trade
#         - Most risk managers recommend **never risking more than 1-2%** per trade
#
#         *Why the differences?*
#         - Kelly Criterion maximizes long-term growth but assumes perfect knowledge
#         - Real trading has uncertainty, so most traders use fractional Kelly
#         - Conservative sizing protects against black swan events and estimation errors
#         """)


# Footer
st.markdown("---")
st.caption("© 2025 ClockTrades.com • All calculations are theoretical and don't guarantee future results • "
           "Risk management is essential in trading")
