import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Arbitrage Scanner + Flash Loan Wizard", 
    page_icon="⚡", 
    layout="wide"
)

# Main title and description
st.title("⚡ Crypto Arbitrage Scanner + Flash Loan Wizard")
st.markdown("**AI-assisted • Real-time opportunities • One-click Solidity flash-loan contracts**  \n*Built for GitHub + Streamlit*")

# SIDEBAR FILTERS 
st.sidebar.header("🔍 Filters")

min_profit = st.sidebar.slider("Minimum Profit (%)", 0.0, 10.0, 1.0, 0.1)
min_confidence = st.sidebar.slider("Minimum Confidence (%)", 0, 100, 80, 1)

all_tokens = ["ETH/USDC", "WBTC/USDC", "ETH/WBTC", "USDC/DAI", "SOL/USDC"]
selected_tokens = st.sidebar.multiselect("Tokens / Pairs to monitor", all_tokens, default=all_tokens)

all_exchanges = ["Uniswap V2", "Sushiswap", "Uniswap V3", "Balancer V2", "Curve"]
selected_exchanges = st.sidebar.multiselect("Exchanges to monitor", all_exchanges, default=all_exchanges)

st.sidebar.markdown("---")
st.sidebar.caption("🔌 Connect your own arbitrage engine in production (Web3 + 1inch / CCXT)")

# MOCK ARBITRAGE DATA (replace with real scanner) 
@st.cache_data(ttl=60)
def get_opportunities():
    data = {
        "ID": [1, 2, 3, 4, 5],
        "Pair": ["ETH/USDC", "WBTC/USDC", "ETH/WBTC", "USDC/DAI", "ETH/USDC"],
        "Buy on": ["Uniswap V2", "Sushiswap", "Uniswap V2", "Curve", "Balancer V2"],
        "Sell on": ["Sushiswap", "Uniswap V2", "Sushiswap", "Uniswap V3", "Uniswap V2"],
        "Profit %": [3.8, 2.1, 4.5, 1.2, 2.9],
        "Confidence %": [94, 87, 96, 79, 91],
        "Est. Profit (USD)": [1240, 680, 2150, 310, 890],
        "Volume (24h)": ["$42M", "$18M", "$67M", "$9M", "\$31M"],
        "Last seen": [datetime.now().strftime("%H:%M:%S")] * 5,
        "Direction": [
            "Buy ETH on Uniswap V2 → Sell on Sushiswap",
            "Buy WBTC on Sushiswap → Sell on Uniswap V2",
            "Buy ETH on Uniswap V2 → Sell WBTC on Sushiswap",
            "Buy USDC on Curve → Sell on Uniswap V3",
            "Buy ETH on Balancer V2 → Sell on Uniswap V2"
        ]
    }
    df = pd.DataFrame(data)
    # Apply user filters
    df = df[
        (df["Profit %"] >= min_profit) &
        (df["Confidence %"] >= min_confidence) &
        (df["Pair"].isin(selected_tokens)) &
        ((df["Buy on"].isin(selected_exchanges)) | (df["Sell on"].isin(selected_exchanges)))
    ]
    return df

df = get_opportunities()

st.header("📊 Live Arbitrage Opportunities")
if df.empty:
    st.warning("No opportunities match your filters. Lower the thresholds!")
else:
    st.dataframe(
        df.style.format({"Profit %": "{:.1f}%", "Confidence %": "{:.0f}%"}),
        use_container_width=True,
        hide_index=True
    )

# OPPORTUNITY SELECTOR
st.markdown("---")
st.subheader("🎯 Select an Opportunity to Execute")

if not df.empty:
    selected_id = st.selectbox(
        "Choose opportunity",
        options=df["ID"].tolist(),
        format_func=lambda x: f"ID {x} — {df[df['ID']==x]['Pair'].values[0]} — {df[df['ID']==x]['Profit %'].values[0]:.1f}% profit"
    )
   
    opp = df[df["ID"] == selected_id].iloc[0]
   
    st.success(f"**Selected:** {opp['Pair']} • Buy on **{opp['Buy on']}** → Sell on **{opp['Sell on']}** • {opp['Profit %']}% profit @ {opp['Confidence %']}% confidence")
   
    # AI-ASSISTED INSIGHTS 
    st.markdown("### 🤖 AI Insights (powered by your favorite LLM)")
    with st.expander("Click for instant AI analysis", expanded=True):
        st.markdown(f"""
        **High-confidence opportunity detected** 
        • Profit spread: **{opp['Profit %']}%** after fees 
        • Confidence: **{opp['Confidence %']}%** (low slippage expected) 
        • Recommended flash-loan size: **\${int(opp['Est. Profit (USD)'] * 15):,}** USDC 
        • Risk: Gas fees ~\$18, MEV protection recommended 
        *Would you like me to generate a full execution plan?* (extend this section with LangChain/OpenAI in production)
        """)
   
    # FLASH LOAN WIZARD 
    st.header("⚡ Flash Loan Wizard — Plug & Play Solidity Generator")
    st.caption("Choose provider → amount → token → generate complete contract with all approvals & interfaces")

    col1, col2, col3 = st.columns(3)
    with col1:
        provider = st.selectbox(
            "Flash Loan Provider",
            ["Aave V3 (most popular)", "Balancer V2"],
            help="Aave V3 uses FlashLoanSimpleReceiverBase pattern. Balancer uses Vault.flashLoan()"
        )
    with col2:
        borrow_token = st.selectbox(
            "Borrow Token",
            ["USDC", "WETH", "DAI"],
            index=0 if "USDC" in opp["Pair"] else 1
        )
    with col3:
        flash_amount = st.number_input(
            "Flash Loan Amount",
            min_value=1000,
            value=int(opp['Est. Profit (USD)'] * 12),
            step=1000,
            format="%d"
        )

    # Router mapping for the selected opportunity
    routers = {
        "Uniswap V2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "Sushiswap": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
        "Uniswap V3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "Balancer V2": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
        "Curve": "0x80466dDd1d5B6D9A1f4A9d2f7D7e5C5e5C5e5C5e"
    }

    buy_router = routers.get(opp["Buy on"], "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
    sell_router = routers.get(opp["Sell on"], "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")

    if st.button("🚀 Generate Plug-and-Play Solidity Contract", type="primary", use_container_width=True):
        with st.spinner("Generating complete contract with all interfaces..."):
            # Generate contract using string formatting to avoid f-string conflicts
            contract_code =  SPDX-License-Identifier: MIT
pragma solidity .8.24;

/**
 * @title {provider} Flash Loan Arbitrage Bot
 * @notice Plug-and-play contract generated by the Streamlit Wizard
 * @dev Deploy on Ethereum mainnet • All approvals & interfaces included
 * Generated for opportunity: {opp['Pair']} | {opp['Buy on']} → {opp['Sell on']} | {opp['Profit %']}% profit
 */

interface IERC20 {{
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external returns (bool);
    function transfer(address, uint256) external returns (bool);
}}

interface IUniswapV2Router {{
    function swapExactTokensForTokens(
        uint amountIn, uint amountOutMin, address[]
