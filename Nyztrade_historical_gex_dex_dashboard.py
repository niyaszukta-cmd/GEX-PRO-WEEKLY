# ============================================================================
# NYZTrade Historical GEX/DEX Dashboard
# Historical Options Greeks Analysis with Indian Standard Time
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm
from datetime import datetime, timedelta
import pytz
import requests
import time
from dataclasses import dataclass
from typing import Optional, Dict, List
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="NYZTrade Historical GEX/DEX",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS (Same as your style)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2332;
        --bg-card-hover: #232f42;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-yellow: #f59e0b;
        --accent-cyan: #06b6d4;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: #2d3748;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f172a 50%, var(--bg-primary) 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .sub-title {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 8px;
    }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card.positive { border-left: 4px solid var(--accent-green); }
    .metric-card.negative { border-left: 4px solid var(--accent-red); }
    .metric-card.neutral { border-left: 4px solid var(--accent-yellow); }
    
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-muted);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .metric-value.positive { color: var(--accent-green); }
    .metric-value.negative { color: var(--accent-red); }
    .metric-value.neutral { color: var(--accent-yellow); }
    
    .metric-delta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        margin-top: 8px;
        color: var(--text-secondary);
    }
    
    .signal-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .signal-badge.bullish {
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-green);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .signal-badge.bearish {
        background: rgba(239, 68, 68, 0.15);
        color: var(--accent-red);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .signal-badge.volatile {
        background: rgba(245, 158, 11, 0.15);
        color: var(--accent-yellow);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .history-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
    }
    
    .history-dot {
        width: 8px;
        height: 8px;
        background: var(--accent-blue);
        border-radius: 50%;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class DhanConfig:
    client_id: str = "1100480354"
    access_token: str = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY1OTYzMzk2LCJhcHBfaWQiOiJjOTNkM2UwOSIsImlhdCI6MTc2NTg3Njk5NiwidG9rZW5Db25zdW1lclR5cGUiOiJBUFAiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDQ4MDM1NCJ9.K93qVFYO2XrMJ-Jn4rY2autNZ444tc-AzYtaxVUsjRfsjW7NhfQom58vzuSMVI6nRMMB_sa7fCtWE5JIvk75yw"

DHAN_SECURITY_IDS = {
    "NIFTY": 13, "BANKNIFTY": 25, "FINNIFTY": 27, "MIDCPNIFTY": 442
}

SYMBOL_CONFIG = {
    "NIFTY": {"contract_size": 25, "strike_interval": 50},
    "BANKNIFTY": {"contract_size": 15, "strike_interval": 100},
    "FINNIFTY": {"contract_size": 40, "strike_interval": 50},
    "MIDCPNIFTY": {"contract_size": 75, "strike_interval": 25},
}

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# ============================================================================
# BLACK-SCHOLES CALCULATOR
# ============================================================================

class BlackScholesCalculator:
    @staticmethod
    def calculate_d1(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0:
            return 0
        return (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * np.sqrt(T))
    
    @staticmethod
    def calculate_gamma(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return norm.pdf(d1) / (S * sigma * np.sqrt(T))
        except:
            return 0
    
    @staticmethod
    def calculate_call_delta(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return norm.cdf(d1)
        except:
            return 0
    
    @staticmethod
    def calculate_put_delta(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return norm.cdf(d1) - 1
        except:
            return 0

# ============================================================================
# DHAN ROLLING API FETCHER
# ============================================================================

class DhanHistoricalFetcher:
    def __init__(self, config: DhanConfig):
        self.config = config
        self.headers = {
            'access-token': config.access_token,
            'client-id': config.client_id,
            'Content-Type': 'application/json'
        }
        self.base_url = "https://api.dhan.co/v2"
        self.bs_calc = BlackScholesCalculator()
        self.risk_free_rate = 0.07
    
    def fetch_rolling_data(self, symbol: str, from_date: str, to_date: str, 
                          strike_type: str = "ATM", option_type: str = "CALL", 
                          interval: str = "60", expiry_code: int = 1):
        """Fetch historical rolling options data"""
        try:
            security_id = DHAN_SECURITY_IDS.get(symbol, 13)
            
            payload = {
                "exchangeSegment": "NSE_FNO",
                "interval": interval,
                "securityId": security_id,
                "instrument": "OPTIDX",
                "expiryFlag": "MONTH",
                "expiryCode": expiry_code,  # Now dynamic based on user selection
                "strike": strike_type,
                "drvOptionType": option_type,
                "requiredData": ["open", "high", "low", "close", "volume", "oi", "iv", "strike", "spot"],
                "fromDate": from_date,
                "toDate": to_date
            }
            
            response = requests.post(
                f"{self.base_url}/charts/rollingoption",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                return data
            else:
                st.warning(f"API returned status {response.status_code}")
                return None
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None
    
    def process_historical_data(self, symbol: str, target_date: str, strikes: List[str], 
                               interval: str = "60", expiry_code: int = 1):
        """Process historical data for a specific date"""
        
        # Convert to datetime
        target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        from_date = (target_dt - timedelta(days=1)).strftime('%Y-%m-%d')
        to_date = (target_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        
        config = SYMBOL_CONFIG.get(symbol, SYMBOL_CONFIG["NIFTY"])
        contract_size = config["contract_size"]
        
        all_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_steps = len(strikes) * 2
        current_step = 0
        
        for strike_type in strikes:
            status_text.text(f"Fetching {strike_type} (Expiry Code: {expiry_code})...")
            
            # Fetch CALL data with interval and expiry_code
            call_data = self.fetch_rolling_data(symbol, from_date, to_date, strike_type, "CALL", interval, expiry_code)
            current_step += 1
            progress_bar.progress(current_step / total_steps)
            time.sleep(1)
            
            # Fetch PUT data with interval and expiry_code
            put_data = self.fetch_rolling_data(symbol, from_date, to_date, strike_type, "PUT", interval, expiry_code)
            current_step += 1
            progress_bar.progress(current_step / total_steps)
            time.sleep(1)
            
            if not call_data or not put_data:
                continue
            
            ce_data = call_data.get('ce', {})
            pe_data = put_data.get('pe', {})
            
            if not ce_data:
                continue
            
            timestamps = ce_data.get('timestamp', [])
            
            for i, ts in enumerate(timestamps):
                try:
                    # Convert timestamp to IST
                    dt_utc = datetime.fromtimestamp(ts, tz=pytz.UTC)
                    dt_ist = dt_utc.astimezone(IST)
                    
                    # Filter for target date
                    if dt_ist.date() != target_dt.date():
                        continue
                    
                    spot_price = ce_data.get('spot', [0])[i] if i < len(ce_data.get('spot', [])) else 0
                    strike_price = ce_data.get('strike', [0])[i] if i < len(ce_data.get('strike', [])) else 0
                    
                    if spot_price == 0 or strike_price == 0:
                        continue
                    
                    # Get OI and other data
                    call_oi = ce_data.get('oi', [0])[i] if i < len(ce_data.get('oi', [])) else 0
                    put_oi = pe_data.get('oi', [0])[i] if i < len(pe_data.get('oi', [])) else 0
                    call_volume = ce_data.get('volume', [0])[i] if i < len(ce_data.get('volume', [])) else 0
                    put_volume = pe_data.get('volume', [0])[i] if i < len(pe_data.get('volume', [])) else 0
                    call_iv = ce_data.get('iv', [15])[i] if i < len(ce_data.get('iv', [])) else 15
                    put_iv = pe_data.get('iv', [15])[i] if i < len(pe_data.get('iv', [])) else 15
                    
                    # Calculate Greeks
                    time_to_expiry = 7 / 365  # Approximate
                    call_iv_dec = call_iv / 100 if call_iv > 1 else call_iv
                    put_iv_dec = put_iv / 100 if put_iv > 1 else put_iv
                    
                    call_gamma = self.bs_calc.calculate_gamma(spot_price, strike_price, time_to_expiry, self.risk_free_rate, call_iv_dec)
                    put_gamma = self.bs_calc.calculate_gamma(spot_price, strike_price, time_to_expiry, self.risk_free_rate, put_iv_dec)
                    call_delta = self.bs_calc.calculate_call_delta(spot_price, strike_price, time_to_expiry, self.risk_free_rate, call_iv_dec)
                    put_delta = self.bs_calc.calculate_put_delta(spot_price, strike_price, time_to_expiry, self.risk_free_rate, put_iv_dec)
                    
                    # Calculate GEX and DEX
                    call_gex = (call_oi * call_gamma * spot_price**2 * contract_size) / 1e9
                    put_gex = -(put_oi * put_gamma * spot_price**2 * contract_size) / 1e9
                    call_dex = (call_oi * call_delta * spot_price * contract_size) / 1e9
                    put_dex = (put_oi * put_delta * spot_price * contract_size) / 1e9
                    
                    all_data.append({
                        'timestamp': dt_ist,
                        'time': dt_ist.strftime('%H:%M IST'),
                        'spot_price': spot_price,
                        'strike': strike_price,
                        'strike_type': strike_type,
                        'call_oi': call_oi,
                        'put_oi': put_oi,
                        'call_volume': call_volume,
                        'put_volume': put_volume,
                        'total_volume': call_volume + put_volume,
                        'call_iv': call_iv,
                        'put_iv': put_iv,
                        'call_gex': call_gex,
                        'put_gex': put_gex,
                        'net_gex': call_gex + put_gex,
                        'call_dex': call_dex,
                        'put_dex': put_dex,
                        'net_dex': call_dex + put_dex,
                    })
                    
                except Exception as e:
                    continue
        
        progress_bar.empty()
        status_text.empty()
        
        if not all_data:
            return None, None
        
        df = pd.DataFrame(all_data)
        
        # Sort by timestamp for flow calculations
        df = df.sort_values(['strike', 'timestamp']).reset_index(drop=True)
        
        # Calculate GEX Flow and DEX Flow (change from previous timestamp)
        df['call_gex_flow'] = 0.0
        df['put_gex_flow'] = 0.0
        df['net_gex_flow'] = 0.0
        df['call_dex_flow'] = 0.0
        df['put_dex_flow'] = 0.0
        df['net_dex_flow'] = 0.0
        
        for strike in df['strike'].unique():
            strike_mask = df['strike'] == strike
            strike_data = df[strike_mask].copy()
            
            if len(strike_data) > 1:
                # Calculate flow as difference from previous timestamp
                df.loc[strike_mask, 'call_gex_flow'] = strike_data['call_gex'].diff().fillna(0)
                df.loc[strike_mask, 'put_gex_flow'] = strike_data['put_gex'].diff().fillna(0)
                df.loc[strike_mask, 'net_gex_flow'] = strike_data['net_gex'].diff().fillna(0)
                df.loc[strike_mask, 'call_dex_flow'] = strike_data['call_dex'].diff().fillna(0)
                df.loc[strike_mask, 'put_dex_flow'] = strike_data['put_dex'].diff().fillna(0)
                df.loc[strike_mask, 'net_dex_flow'] = strike_data['net_dex'].diff().fillna(0)
        
        # Calculate hedging pressure
        max_gex = df['net_gex'].abs().max()
        df['hedging_pressure'] = (df['net_gex'] / max_gex * 100) if max_gex > 0 else 0
        
        # Get latest data point for metadata
        latest = df.sort_values('timestamp').iloc[-1]
        
        # Spot price validation
        spot_prices = df['spot_price'].unique()
        spot_variation = (spot_prices.max() - spot_prices.min()) / spot_prices.mean() * 100
        
        meta = {
            'symbol': symbol,
            'date': target_date,
            'spot_price': latest['spot_price'],
            'spot_price_min': spot_prices.min(),
            'spot_price_max': spot_prices.max(),
            'spot_variation_pct': spot_variation,
            'total_records': len(df),
            'time_range': f"{df['time'].min()} - {df['time'].max()}",
            'strikes_count': df['strike'].nunique(),
            'interval': f"{interval} minutes",
            'expiry_code': expiry_code
        }
        
        return df, meta

def create_intraday_timeline(df: pd.DataFrame, selected_timestamp) -> go.Figure:
    """Create intraday timeline of total GEX and DEX"""
    # Aggregate by timestamp
    timeline_df = df.groupby('timestamp').agg({
        'net_gex': 'sum',
        'net_dex': 'sum',
        'spot_price': 'first'
    }).reset_index()
    
    timeline_df = timeline_df.sort_values('timestamp')
    timeline_df['time_str'] = timeline_df['timestamp'].dt.strftime('%H:%M')
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Total Net GEX Over Time', 'Total Net DEX Over Time', 'Spot Price Movement'),
        vertical_spacing=0.1,
        row_heights=[0.35, 0.35, 0.3]
    )
    
    # GEX timeline
    gex_colors = ['#10b981' if x > 0 else '#ef4444' for x in timeline_df['net_gex']]
    fig.add_trace(
        go.Bar(
            x=timeline_df['timestamp'],
            y=timeline_df['net_gex'],
            marker_color=gex_colors,
            name='Net GEX',
            hovertemplate='%{x|%H:%M}<br>GEX: %{y:.4f}B<extra></extra>'
        ),
        row=1, col=1
    )
    
    # DEX timeline
    dex_colors = ['#10b981' if x > 0 else '#ef4444' for x in timeline_df['net_dex']]
    fig.add_trace(
        go.Bar(
            x=timeline_df['timestamp'],
            y=timeline_df['net_dex'],
            marker_color=dex_colors,
            name='Net DEX',
            hovertemplate='%{x|%H:%M}<br>DEX: %{y:.4f}B<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Spot price
    fig.add_trace(
        go.Scatter(
            x=timeline_df['timestamp'],
            y=timeline_df['spot_price'],
            mode='lines+markers',
            line=dict(color='#3b82f6', width=2),
            marker=dict(size=4),
            name='Spot Price',
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)',
            hovertemplate='%{x|%H:%M}<br>Spot: ₹%{y:,.2f}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Add vertical line at selected timestamp
    fig.add_vline(
        x=selected_timestamp,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=3,
        row=1, col=1
    )
    fig.add_vline(
        x=selected_timestamp,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=3,
        row=2, col=1
    )
    fig.add_vline(
        x=selected_timestamp,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=3,
        row=3, col=1
    )
    
    # Add annotations for key times
    key_times = [
        ('Open', '09:15'),
        ('Mid', '12:00'),
        ('Close', '15:30')
    ]
    
    fig.update_layout(
        title=dict(text="<b>📈 Intraday Evolution</b>", font=dict(size=18, color='white')),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=900,
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Time (IST)", row=3, col=1)
    fig.update_yaxes(title_text="GEX (₹B)", row=1, col=1)
    fig.update_yaxes(title_text="DEX (₹B)", row=2, col=1)
    fig.update_yaxes(title_text="Spot Price (₹)", row=3, col=1)
    
    return fig

def create_gex_flow_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Create GEX Flow chart showing inflow/outflow"""
    fig = go.Figure()
    
    # Add call GEX flow
    fig.add_trace(go.Bar(
        y=df['strike'],
        x=df['call_gex_flow'],
        orientation='h',
        name='Call GEX Flow',
        marker_color='rgba(16, 185, 129, 0.6)',
        hovertemplate='Strike: %{y}<br>Call Flow: %{x:.4f}B<extra></extra>'
    ))
    
    # Add put GEX flow
    fig.add_trace(go.Bar(
        y=df['strike'],
        x=df['put_gex_flow'],
        orientation='h',
        name='Put GEX Flow',
        marker_color='rgba(239, 68, 68, 0.6)',
        hovertemplate='Strike: %{y}<br>Put Flow: %{x:.4f}B<extra></extra>'
    ))
    
    # Add spot price line
    fig.add_hline(
        y=spot_price,
        line_dash="dash",
        line_color="#3b82f6",
        line_width=2,
        annotation_text=f"Spot: ₹{spot_price:,.0f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=dict(text="<b>🌊 GEX Flow Distribution</b>", font=dict(size=18, color='white')),
        xaxis_title="GEX Flow (₹B)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=600,
        barmode='relative',
        hovermode='y unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_dex_flow_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Create DEX Flow chart showing directional flow"""
    fig = go.Figure()
    
    # Add call DEX flow
    fig.add_trace(go.Bar(
        y=df['strike'],
        x=df['call_dex_flow'],
        orientation='h',
        name='Call DEX Flow',
        marker_color='rgba(16, 185, 129, 0.6)',
        hovertemplate='Strike: %{y}<br>Call Flow: %{x:.4f}B<extra></extra>'
    ))
    
    # Add put DEX flow
    fig.add_trace(go.Bar(
        y=df['strike'],
        x=df['put_dex_flow'],
        orientation='h',
        name='Put DEX Flow',
        marker_color='rgba(239, 68, 68, 0.6)',
        hovertemplate='Strike: %{y}<br>Put Flow: %{x:.4f}B<extra></extra>'
    ))
    
    # Add spot price line
    fig.add_hline(
        y=spot_price,
        line_dash="dash",
        line_color="#3b82f6",
        line_width=2,
        annotation_text=f"Spot: ₹{spot_price:,.0f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=dict(text="<b>🌊 DEX Flow Distribution</b>", font=dict(size=18, color='white')),
        xaxis_title="DEX Flow (₹B)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=600,
        barmode='relative',
        hovermode='y unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_net_flow_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Create combined Net Flow chart"""
    fig = go.Figure()
    
    # Net GEX Flow
    gex_flow_colors = ['#10b981' if x > 0 else '#ef4444' for x in df['net_gex_flow']]
    fig.add_trace(go.Bar(
        y=df['strike'],
        x=df['net_gex_flow'],
        orientation='h',
        name='Net GEX Flow',
        marker_color=gex_flow_colors,
        opacity=0.7,
        hovertemplate='Strike: %{y}<br>GEX Flow: %{x:.4f}B<extra></extra>'
    ))
    
    # Add spot price line
    fig.add_hline(
        y=spot_price,
        line_dash="dash",
        line_color="#3b82f6",
        line_width=2,
        annotation_text=f"Spot: ₹{spot_price:,.0f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=dict(text="<b>💫 Net GEX Flow</b>", font=dict(size=18, color='white')),
        xaxis_title="Net Flow (₹B)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=600,
        hovermode='y unified'
    )
    
    return fig

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_separate_gex_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Separate GEX chart"""
    # Sort by strike to ensure proper display
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_sorted['net_gex']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['strike'],
        x=df_sorted['net_gex'],
        orientation='h',
        marker_color=colors,
        name='Net GEX',
        hovertemplate='Strike: %{y:,.0f}<br>Net GEX: %{x:.4f}B<extra></extra>',
        showlegend=False
    ))
    
    fig.add_hline(y=spot_price, line_dash="dash", line_color="#06b6d4", line_width=3,
                  annotation_text=f"Spot: {spot_price:,.2f}", annotation_position="top right",
                  annotation=dict(font=dict(size=12, color="white")))
    
    fig.update_layout(
        title=dict(text="<b>🎯 Gamma Exposure (GEX)</b>", font=dict(size=18, color='white')),
        xaxis_title="GEX (₹ Billions)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True, autorange=True),
        margin=dict(l=80, r=80, t=80, b=80)
    )
    
    return fig

def create_separate_dex_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Separate DEX chart"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_sorted['net_dex']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['strike'],
        x=df_sorted['net_dex'],
        orientation='h',
        marker_color=colors,
        name='Net DEX',
        hovertemplate='Strike: %{y:,.0f}<br>Net DEX: %{x:.4f}B<extra></extra>',
        showlegend=False
    ))
    
    fig.add_hline(y=spot_price, line_dash="dash", line_color="#06b6d4", line_width=3,
                  annotation_text=f"Spot: {spot_price:,.2f}", annotation_position="top right",
                  annotation=dict(font=dict(size=12, color="white")))
    
    fig.update_layout(
        title=dict(text="<b>📊 Delta Exposure (DEX)</b>", font=dict(size=18, color='white')),
        xaxis_title="DEX (₹ Billions)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True, autorange=True),
        margin=dict(l=80, r=80, t=80, b=80)
    )
    
    return fig

def create_net_gex_dex_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Combined NET GEX + DEX chart"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    df_sorted['net_gex_dex'] = df_sorted['net_gex'] + df_sorted['net_dex']
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_sorted['net_gex_dex']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['strike'],
        x=df_sorted['net_gex_dex'],
        orientation='h',
        marker_color=colors,
        name='Net GEX+DEX',
        hovertemplate='Strike: %{y:,.0f}<br>Net GEX+DEX: %{x:.4f}B<extra></extra>',
        showlegend=False
    ))
    
    fig.add_hline(y=spot_price, line_dash="dash", line_color="#06b6d4", line_width=3,
                  annotation_text=f"Spot: {spot_price:,.2f}", annotation_position="top right",
                  annotation=dict(font=dict(size=12, color="white")))
    
    fig.update_layout(
        title=dict(text="<b>⚡ Combined NET GEX + DEX</b>", font=dict(size=18, color='white')),
        xaxis_title="Combined Exposure (₹ Billions)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)', showgrid=True, autorange=True),
        margin=dict(l=80, r=80, t=80, b=80)
    )
    
    return fig

def create_hedging_pressure_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Separate Hedging Pressure chart"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['strike'],
        x=df_sorted['hedging_pressure'],
        orientation='h',
        marker=dict(
            color=df_sorted['hedging_pressure'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(
                title=dict(text='Pressure %', font=dict(color='white', size=12)),
                tickfont=dict(color='white'),
                x=1.02,
                len=0.7,
                thickness=20
            ),
            cmin=-100,
            cmax=100
        ),
        hovertemplate='Strike: %{y:,.0f}<br>Pressure: %{x:.1f}%<extra></extra>',
        showlegend=False
    ))
    
    fig.add_hline(y=spot_price, line_dash="dash", line_color="#06b6d4", line_width=3,
                  annotation_text=f"Spot: {spot_price:,.2f}", annotation_position="top right",
                  annotation=dict(font=dict(size=12, color="white")))
    
    # Add zero line
    fig.add_vline(x=0, line_dash="dot", line_color="gray", line_width=1)
    
    fig.update_layout(
        title=dict(text="<b>🎪 Hedging Pressure Distribution</b>", font=dict(size=18, color='white')),
        xaxis_title="Hedging Pressure (%)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.2)', 
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(128,128,128,0.5)',
            zerolinewidth=2,
            range=[-110, 110]
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)', 
            showgrid=True, 
            autorange=True
        ),
        margin=dict(l=80, r=120, t=80, b=80)
    )
    
    return fig

def create_oi_distribution(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """OI Distribution chart"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['strike'],
        x=df_sorted['call_oi'],
        orientation='h',
        name='Call OI',
        marker_color='#10b981',
        opacity=0.7,
        hovertemplate='Strike: %{y:,.0f}<br>Call OI: %{x:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        y=df_sorted['strike'],
        x=-df_sorted['put_oi'],
        orientation='h',
        name='Put OI',
        marker_color='#ef4444',
        opacity=0.7,
        hovertemplate='Strike: %{y:,.0f}<br>Put OI: %{customdata:,.0f}<extra></extra>',
        customdata=df_sorted['put_oi']
    ))
    
    fig.add_hline(y=spot_price, line_dash="dash", line_color="#06b6d4", line_width=2,
                  annotation_text=f"Spot: {spot_price:,.2f}", annotation_position="top right",
                  annotation=dict(font=dict(size=12, color="white")))
    
    # Add zero line
    fig.add_vline(x=0, line_dash="dot", line_color="white", line_width=1)
    
    fig.update_layout(
        title=dict(text="<b>📋 Open Interest Distribution</b>", font=dict(size=16, color='white')),
        xaxis_title="Open Interest (Calls +ve | Puts -ve)",
        yaxis_title="Strike Price",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=500,
        barmode='overlay',
        legend=dict(
            orientation='h', 
            yanchor='bottom', 
            y=1.02, 
            font=dict(color='white')
        ),
        hovermode='closest',
        xaxis=dict(
            gridcolor='rgba(128,128,128,0.2)', 
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.3)',
            zerolinewidth=2
        ),
        yaxis=dict(
            gridcolor='rgba(128,128,128,0.2)', 
            showgrid=True,
            autorange=True
        ),
        margin=dict(l=80, r=80, t=80, b=80)
    )
    
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="main-title">📊 NYZTrade Historical GEX/DEX Dashboard</h1>
                <p class="sub-title">Historical Options Greeks Analysis | Dhan Rolling API | Indian Standard Time</p>
            </div>
            <div class="history-indicator">
                <div class="history-dot"></div>
                <span style="color: #3b82f6; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">HISTORICAL</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        symbol = st.selectbox(
            "📈 Select Index",
            options=list(DHAN_SECURITY_IDS.keys()),
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📅 Historical Date Selection")
        
        # Date range selector
        date_range_option = st.selectbox(
            "Select Date Range",
            ["Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 6 Months", "Custom Range"],
            index=0
        )
        
        if date_range_option == "Custom Range":
            st.info("💡 Select any date range up to 6 months back")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=30),
                    max_value=datetime.now(),
                    min_value=datetime.now() - timedelta(days=180)
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now(),
                    max_value=datetime.now(),
                    min_value=start_date
                )
            
            # Generate list of trading days in range
            date_list = pd.date_range(start=start_date, end=end_date, freq='D')
            # Filter to exclude weekends (API may not have data)
            date_list = [d for d in date_list if d.weekday() < 5]  # Mon-Fri only
            
        else:
            # Predefined ranges
            if date_range_option == "Last 30 Days":
                days_back = 30
            elif date_range_option == "Last 60 Days":
                days_back = 60
            elif date_range_option == "Last 90 Days":
                days_back = 90
            else:  # Last 6 Months
                days_back = 180
            
            date_list = pd.date_range(
                end=datetime.now(),
                periods=days_back,
                freq='D'
            )
            date_list = [d for d in date_list if d.weekday() < 5]
        
        # Convert to date objects for selector
        available_dates = [d.date() for d in date_list]
        
        # Show date range info
        if len(available_dates) > 0:
            st.caption(f"📊 {len(available_dates)} trading days available | From {available_dates[0]} to {available_dates[-1]}")
        
        selected_date = st.selectbox(
            "Select Trading Day",
            options=available_dates,
            index=len(available_dates)-1 if len(available_dates) > 0 else 0,  # Default to most recent
            format_func=lambda x: x.strftime('%Y-%m-%d (%A)')
        )
        
        target_date = selected_date.strftime('%Y-%m-%d')
        
        st.markdown("---")
        st.markdown("### 📆 Expiry Selection")
        
        expiry_option = st.selectbox(
            "Select Expiry",
            ["Current Month (Nearest)", "Next Month", "Far Month"],
            index=0,
            help="Select which monthly expiry to analyze"
        )
        
        # Map to expiryCode
        expiry_code_map = {
            "Current Month (Nearest)": 1,
            "Next Month": 2,
            "Far Month": 3
        }
        expiry_code = expiry_code_map[expiry_option]
        
        st.info(f"📊 Selected expiry code: {expiry_code} | For historical dates, this represents the expiry that was active on that date")
        
        st.markdown("---")
        st.markdown("### 🎯 Strike Selection")
        
        strikes = st.multiselect(
            "Select Strikes",
            ["ATM", "ATM+1", "ATM-1", "ATM+2", "ATM-2", "ATM+3", "ATM-3", 
             "ATM+4", "ATM-4", "ATM+5", "ATM-5", "ATM+6", "ATM-6"],
            default=["ATM", "ATM+1", "ATM-1", "ATM+2", "ATM-2", "ATM+3", "ATM-3"]
        )
        
        st.markdown("---")
        st.markdown("### ⏱️ Time Interval")
        
        interval = st.selectbox(
            "Select Interval",
            options=["5", "15", "60"],
            format_func=lambda x: "5 minutes" if x == "5" else "15 minutes" if x == "15" else "1 hour",
            index=0  # Default to 5 minutes
        )
        
        st.info(f"📊 Selected: {len(strikes)} strikes | {interval} min interval")
        
        st.markdown("---")
        
        fetch_button = st.button("🚀 Fetch Historical Data", use_container_width=True, type="primary")
        
        st.markdown("---")
        st.markdown("### 🕐 Indian Standard Time (IST)")
        ist_now = datetime.now(IST)
        st.info(f"Current IST: {ist_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Store configuration in session state for persistence
    if fetch_button:
        st.session_state.fetch_config = {
            'symbol': symbol,
            'target_date': target_date,
            'strikes': strikes,
            'interval': interval,
            'expiry_code': expiry_code
        }
        st.session_state.data_fetched = False  # Trigger fresh fetch
    
    # Main content
    if fetch_button or (hasattr(st.session_state, 'fetch_config') and st.session_state.get('data_fetched', False)):
        # Get config from session state
        if hasattr(st.session_state, 'fetch_config'):
            config = st.session_state.fetch_config
            symbol = config['symbol']
            target_date = config['target_date']
            strikes = config['strikes']
            interval = config['interval']
            expiry_code = config.get('expiry_code', 1)  # Default to 1 if not present
        
        if not strikes:
            st.error("❌ Please select at least one strike")
            return
        
        # Only fetch if not already in session state or if explicitly requested
        if not st.session_state.get('data_fetched', False) or 'df_data' not in st.session_state:
            st.markdown(f"""
            <div class="metric-card neutral" style="margin: 20px 0;">
                <div class="metric-label">Fetching Historical Data</div>
                <div class="metric-value" style="color: #3b82f6; font-size: 1.2rem;">
                    {symbol} | {target_date} | {interval} min | Strikes: {', '.join(strikes)}
                </div>
                <div class="metric-delta">This may take 1-3 minutes...</div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                fetcher = DhanHistoricalFetcher(DhanConfig())
                df, meta = fetcher.process_historical_data(symbol, target_date, strikes, interval, expiry_code)
                
                if df is None or len(df) == 0:
                    st.error("❌ No data available for the selected date. Please try a different date or check if it was a trading day.")
                    return
                
                # Store in session state
                st.session_state.df_data = df
                st.session_state.meta_data = meta
                st.session_state.data_fetched = True
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Please check your API credentials and try again. Make sure the selected date was a trading day.")
                return
        
        # Retrieve from session state
        df = st.session_state.df_data
        meta = st.session_state.meta_data
        
        # Get all unique timestamps for slider
        all_timestamps = sorted(df['timestamp'].unique())
        timestamp_options = [ts.strftime('%H:%M IST') for ts in all_timestamps]
        
        st.success(f"✅ Data fetched successfully! Total records: {len(df):,} | Interval: {meta['interval']} | Expiry Code: {meta['expiry_code']}")
        
        # Spot price validation warning
        if meta['spot_variation_pct'] > 2:
            st.warning(f"""
            ⚠️ **Spot Price Variation Detected**: {meta['spot_variation_pct']:.2f}%
            - Min: ₹{meta['spot_price_min']:,.2f}
            - Max: ₹{meta['spot_price_max']:,.2f}
            - This is normal for volatile trading days
            """)
        
        # Expiry information
        st.info(f"""
        📆 **Expiry Information**: 
        - Using expiry code: {meta['expiry_code']}
        - Code 1 = Nearest monthly expiry at the time of historical date
        - Code 2 = Next month expiry
        - Code 3 = Far month expiry
        
        **Note**: The spot price shown is from Dhan's historical data feed at that specific timestamp. Minor differences from other data sources are normal.
        """)
        
        st.markdown("---")
        st.markdown("---")
        st.markdown("### ⏱️ Time Navigation")
            
        # Quick jump buttons and playback controls
        control_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
        
        with control_cols[0]:
            if st.button("⏮️ First", use_container_width=True):
                st.session_state.timestamp_idx = 0
        
        with control_cols[1]:
            if st.button("◀️ Prev", use_container_width=True):
                current = st.session_state.get('timestamp_idx', len(all_timestamps) - 1)
                st.session_state.timestamp_idx = max(0, current - 1)
        
        with control_cols[2]:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.timestamp_idx = len(all_timestamps) - 1
        
        with control_cols[3]:
            if st.button("▶️ Next", use_container_width=True):
                current = st.session_state.get('timestamp_idx', len(all_timestamps) - 1)
                st.session_state.timestamp_idx = min(len(all_timestamps) - 1, current + 1)
        
        with control_cols[4]:
            if st.button("⏭️ Last", use_container_width=True):
                st.session_state.timestamp_idx = len(all_timestamps) - 1
        
        with control_cols[5]:
            if st.button("⏰ 9:30", use_container_width=True):
                # Jump to around market open
                morning_times = [i for i, ts in enumerate(all_timestamps) if ts.hour == 9 and ts.minute >= 30]
                if morning_times:
                    st.session_state.timestamp_idx = morning_times[0]
        
        with control_cols[6]:
            if st.button("⏰ 12:00", use_container_width=True):
                # Jump to noon
                noon_times = [i for i, ts in enumerate(all_timestamps) if ts.hour == 12]
                if noon_times:
                    st.session_state.timestamp_idx = noon_times[0]
        
        with control_cols[7]:
            if st.button("⏰ 3:15", use_container_width=True):
                # Jump to near close
                close_times = [i for i, ts in enumerate(all_timestamps) if ts.hour == 15 and ts.minute >= 15]
                if close_times:
                    st.session_state.timestamp_idx = close_times[0]
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"""<div class="metric-card neutral" style="padding: 15px;">
                <div class="metric-label">Start Time</div>
                <div class="metric-value" style="font-size: 1.2rem;">{timestamp_options[0]}</div>
            </div>""", unsafe_allow_html=True)
        
        with col2:
            # Use session state for timestamp index
            if 'timestamp_idx' not in st.session_state:
                st.session_state.timestamp_idx = len(all_timestamps) - 1
            
            selected_timestamp_idx = st.slider(
                "🎯 Drag to navigate through intraday data points",
                min_value=0,
                max_value=len(all_timestamps) - 1,
                value=st.session_state.timestamp_idx,
                format="",
                key="time_slider"
            )
            
            # Update session state
            st.session_state.timestamp_idx = selected_timestamp_idx
            
            selected_timestamp = all_timestamps[selected_timestamp_idx]
            
            # Show progress bar
            progress = (selected_timestamp_idx + 1) / len(all_timestamps)
            st.progress(progress)
            
            st.info(f"📍 **{selected_timestamp.strftime('%H:%M:%S IST')}** | Point {selected_timestamp_idx + 1} of {len(all_timestamps)} | {progress*100:.1f}% through trading day")
        
        with col3:
            st.markdown(f"""<div class="metric-card neutral" style="padding: 15px;">
                <div class="metric-label">End Time</div>
                <div class="metric-value" style="font-size: 1.2rem;">{timestamp_options[-1]}</div>
            </div>""", unsafe_allow_html=True)
        
        # Filter data for selected timestamp
        df_selected = df[df['timestamp'] == selected_timestamp].copy()
        
        # If no data at exact timestamp, get the closest one
        if len(df_selected) == 0:
            closest_idx = min(range(len(all_timestamps)), 
                             key=lambda i: abs((all_timestamps[i] - selected_timestamp).total_seconds()))
            df_selected = df[df['timestamp'] == all_timestamps[closest_idx]].copy()
        
        # Use selected timestamp data
        df_latest = df_selected
        spot_price = df_latest['spot_price'].iloc[0] if len(df_latest) > 0 else 0
        
        # Calculate aggregated metrics
        total_gex = df_latest['net_gex'].sum()
        total_dex = df_latest['net_dex'].sum()
        total_net = total_gex + total_dex
        total_call_oi = df_latest['call_oi'].sum()
        total_put_oi = df_latest['put_oi'].sum()
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1
        
        # Display overview metrics
        st.markdown("### 📊 Historical Data Overview")
        cols = st.columns(6)
        
        with cols[0]:
            st.markdown(f"""<div class="metric-card neutral">
                <div class="metric-label">Date</div>
                <div class="metric-value" style="font-size: 1.2rem;">{target_date}</div>
                <div class="metric-delta">{selected_timestamp.strftime('%H:%M:%S IST')}</div>
            </div>""", unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"""<div class="metric-card neutral">
                <div class="metric-label">Spot Price</div>
                <div class="metric-value">₹{spot_price:,.2f}</div>
                <div class="metric-delta">@ Selected Time</div>
            </div>""", unsafe_allow_html=True)
        
        with cols[2]:
            gex_class = "positive" if total_gex > 0 else "negative"
            st.markdown(f"""<div class="metric-card {gex_class}">
                <div class="metric-label">Total Net GEX</div>
                <div class="metric-value {gex_class}">{total_gex:.4f}B</div>
                <div class="metric-delta">{'Suppression' if total_gex > 0 else 'Amplification'}</div>
            </div>""", unsafe_allow_html=True)
        
        with cols[3]:
            dex_class = "positive" if total_dex > 0 else "negative"
            st.markdown(f"""<div class="metric-card {dex_class}">
                <div class="metric-label">Total Net DEX</div>
                <div class="metric-value {dex_class}">{total_dex:.4f}B</div>
                <div class="metric-delta">{'Bullish' if total_dex > 0 else 'Bearish'}</div>
            </div>""", unsafe_allow_html=True)
        
        with cols[4]:
            net_class = "positive" if total_net > 0 else "negative"
            st.markdown(f"""<div class="metric-card {net_class}">
                <div class="metric-label">GEX + DEX</div>
                <div class="metric-value {net_class}">{total_net:.4f}B</div>
                <div class="metric-delta">Combined Signal</div>
            </div>""", unsafe_allow_html=True)
        
        with cols[5]:
            pcr_class = "positive" if pcr > 1 else "negative"
            st.markdown(f"""<div class="metric-card {pcr_class}">
                <div class="metric-label">Put/Call Ratio</div>
                <div class="metric-value {pcr_class}">{pcr:.2f}</div>
                <div class="metric-delta">{'Bearish' if pcr > 1.2 else 'Bullish' if pcr < 0.8 else 'Neutral'}</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Signal badges
        cols = st.columns(4)
        with cols[0]:
            gex_signal = "🟢 GEX SUPPRESSION" if total_gex > 0 else "🔴 GEX AMPLIFICATION"
            gex_badge = "bullish" if total_gex > 0 else "bearish"
            st.markdown(f'<div class="signal-badge {gex_badge}">{gex_signal}</div>', unsafe_allow_html=True)
        
        with cols[1]:
            dex_signal = "🟢 DEX BULLISH" if total_dex > 0 else "🔴 DEX BEARISH"
            dex_badge = "bullish" if total_dex > 0 else "bearish"
            st.markdown(f'<div class="signal-badge {dex_badge}">{dex_signal}</div>', unsafe_allow_html=True)
        
        with cols[2]:
            net_signal = "🟢 NET POSITIVE" if total_net > 0 else "🔴 NET NEGATIVE"
            net_badge = "bullish" if total_net > 0 else "bearish"
            st.markdown(f'<div class="signal-badge {net_badge}">{net_signal}</div>', unsafe_allow_html=True)
        
        with cols[3]:
            st.markdown(f'<div class="signal-badge volatile">📊 {len(df_latest)} Strikes at {selected_timestamp.strftime("%H:%M")}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs for separate charts
        tabs = st.tabs(["🎯 GEX", "📊 DEX", "⚡ NET GEX+DEX", "🎪 Hedge Pressure", "🌊 GEX Flow", "🌊 DEX Flow", "💫 Net Flow", "📈 Intraday Timeline", "📋 OI & Data"])
        
        with tabs[0]:
            st.markdown("### 🎯 Gamma Exposure (GEX) Analysis")
            st.plotly_chart(create_separate_gex_chart(df_latest, spot_price), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                positive_gex = df_latest[df_latest['net_gex'] > 0]['net_gex'].sum()
                st.metric("Positive GEX", f"{positive_gex:.4f}B")
            with col2:
                negative_gex = df_latest[df_latest['net_gex'] < 0]['net_gex'].sum()
                st.metric("Negative GEX", f"{negative_gex:.4f}B")
            
        with tabs[1]:
            st.markdown("### 📊 Delta Exposure (DEX) Analysis")
            st.plotly_chart(create_separate_dex_chart(df_latest, spot_price), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                positive_dex = df_latest[df_latest['net_dex'] > 0]['net_dex'].sum()
                st.metric("Positive DEX", f"{positive_dex:.4f}B")
            with col2:
                negative_dex = df_latest[df_latest['net_dex'] < 0]['net_dex'].sum()
                st.metric("Negative DEX", f"{negative_dex:.4f}B")
            
        with tabs[2]:
            st.markdown("### ⚡ Combined NET GEX + DEX Analysis")
            st.plotly_chart(create_net_gex_dex_chart(df_latest, spot_price), use_container_width=True)
            
            st.markdown("""
            **Interpretation:**
            - **Positive values**: Market makers providing support/resistance
            - **Negative values**: Volatility amplification expected
            - **Near zero**: Gamma flip zone - critical levels
            """)
            
        with tabs[3]:
            st.markdown("### 🎪 Hedging Pressure Distribution")
            st.plotly_chart(create_hedging_pressure_chart(df_latest, spot_price), use_container_width=True)
            
            max_pressure_strike = df_latest.loc[df_latest['hedging_pressure'].abs().idxmax(), 'strike']
            max_pressure_value = df_latest.loc[df_latest['hedging_pressure'].abs().idxmax(), 'hedging_pressure']
            
            st.info(f"📍 Maximum Hedging Pressure at Strike: ₹{max_pressure_strike:,.0f} ({max_pressure_value:.1f}%)")
        
        with tabs[4]:
            st.markdown("### 🌊 GEX Flow Analysis")
            st.plotly_chart(create_gex_flow_chart(df_latest, spot_price), use_container_width=True)
            
            # Calculate flow metrics
            total_gex_inflow = df_latest[df_latest['net_gex_flow'] > 0]['net_gex_flow'].sum()
            total_gex_outflow = df_latest[df_latest['net_gex_flow'] < 0]['net_gex_flow'].sum()
            net_gex_flow = total_gex_inflow + total_gex_outflow
            
            col1, col2, col3 = st.columns(3)
            with col1:
                flow_class = "positive" if total_gex_inflow > abs(total_gex_outflow) else "negative"
                st.markdown(f"""<div class="metric-card positive">
                    <div class="metric-label">GEX Inflow</div>
                    <div class="metric-value positive">{total_gex_inflow:.4f}B</div>
                    <div class="metric-delta">Building Positions</div>
                </div>""", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""<div class="metric-card negative">
                    <div class="metric-label">GEX Outflow</div>
                    <div class="metric-value negative">{total_gex_outflow:.4f}B</div>
                    <div class="metric-delta">Reducing Positions</div>
                </div>""", unsafe_allow_html=True)
            
            with col3:
                net_class = "positive" if net_gex_flow > 0 else "negative"
                st.markdown(f"""<div class="metric-card {net_class}">
                    <div class="metric-label">Net GEX Flow</div>
                    <div class="metric-value {net_class}">{net_gex_flow:.4f}B</div>
                    <div class="metric-delta">{'Accumulation' if net_gex_flow > 0 else 'Distribution'}</div>
                </div>""", unsafe_allow_html=True)
            
            st.markdown("""
            **GEX Flow Interpretation:**
            - **Positive Flow (Green)**: Market makers building gamma hedges → Expect lower volatility
            - **Negative Flow (Red)**: Market makers reducing gamma hedges → Expect higher volatility
            - **Large inflows** near strikes indicate strong hedging activity
            - **Flow reversal** can signal regime changes
            """)
        
        with tabs[5]:
            st.markdown("### 🌊 DEX Flow Analysis")
            st.plotly_chart(create_dex_flow_chart(df_latest, spot_price), use_container_width=True)
            
            # Calculate DEX flow metrics
            total_dex_inflow = df_latest[df_latest['net_dex_flow'] > 0]['net_dex_flow'].sum()
            total_dex_outflow = df_latest[df_latest['net_dex_flow'] < 0]['net_dex_flow'].sum()
            net_dex_flow = total_dex_inflow + total_dex_outflow
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""<div class="metric-card positive">
                    <div class="metric-label">DEX Inflow</div>
                    <div class="metric-value positive">{total_dex_inflow:.4f}B</div>
                    <div class="metric-delta">Bullish Positioning</div>
                </div>""", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""<div class="metric-card negative">
                    <div class="metric-label">DEX Outflow</div>
                    <div class="metric-value negative">{total_dex_outflow:.4f}B</div>
                    <div class="metric-delta">Bearish Positioning</div>
                </div>""", unsafe_allow_html=True)
            
            with col3:
                net_class = "positive" if net_dex_flow > 0 else "negative"
                st.markdown(f"""<div class="metric-card {net_class}">
                    <div class="metric-label">Net DEX Flow</div>
                    <div class="metric-value {net_class}">{net_dex_flow:.4f}B</div>
                    <div class="metric-delta">{'Bullish Bias' if net_dex_flow > 0 else 'Bearish Bias'}</div>
                </div>""", unsafe_allow_html=True)
            
            st.markdown("""
            **DEX Flow Interpretation:**
            - **Positive Flow (Green)**: Net buying of calls or selling of puts → Bullish sentiment
            - **Negative Flow (Red)**: Net buying of puts or selling of calls → Bearish sentiment
            - **Strong flow** indicates directional conviction
            - **Flow divergence** from price can signal reversal
            """)
        
        with tabs[6]:
            st.markdown("### 💫 Net Flow Analysis (GEX + DEX)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### GEX Flow")
                st.plotly_chart(create_net_flow_chart(df_latest, spot_price), use_container_width=True)
            
            with col2:
                st.markdown("#### DEX Flow")
                # Create DEX flow chart similar to GEX
                fig_dex = go.Figure()
                dex_flow_colors = ['#10b981' if x > 0 else '#ef4444' for x in df_latest['net_dex_flow']]
                fig_dex.add_trace(go.Bar(
                    y=df_latest['strike'],
                    x=df_latest['net_dex_flow'],
                    orientation='h',
                    marker_color=dex_flow_colors,
                    opacity=0.7,
                    hovertemplate='Strike: %{y}<br>DEX Flow: %{x:.4f}B<extra></extra>'
                ))
                fig_dex.add_hline(y=spot_price, line_dash="dash", line_color="#3b82f6", line_width=2)
                fig_dex.update_layout(
                    title=dict(text="<b>💫 Net DEX Flow</b>", font=dict(size=18, color='white')),
                    xaxis_title="Net Flow (₹B)",
                    yaxis_title="Strike Price",
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26,35,50,0.8)',
                    height=600,
                    hovermode='y unified'
                )
                st.plotly_chart(fig_dex, use_container_width=True)
            
            # Combined analysis
            st.markdown("### 🎯 Combined Flow Signals")
            
            gex_signal = "Building" if net_gex_flow > 0 else "Reducing"
            dex_signal = "Bullish" if net_dex_flow > 0 else "Bearish"
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                **Current Flow Regime:**
                - GEX Flow: **{gex_signal}** ({net_gex_flow:.4f}B)
                - DEX Flow: **{dex_signal}** ({net_dex_flow:.4f}B)
                """)
            
            with col2:
                if net_gex_flow > 0 and net_dex_flow > 0:
                    st.success("✅ **Bullish + Low Vol** → Ideal for bull spreads, covered calls")
                elif net_gex_flow < 0 and net_dex_flow > 0:
                    st.warning("⚠️ **Bullish + High Vol** → Long calls, be cautious")
                elif net_gex_flow > 0 and net_dex_flow < 0:
                    st.warning("⚠️ **Bearish + Low Vol** → Bear spreads, selling premium")
                else:
                    st.error("⚡ **Bearish + High Vol** → High risk, long puts or stay out")
            
            st.markdown("""
            **Trading Based on Flow:**
            1. **Strong GEX Inflow + Bullish DEX** → Buy calls, market likely to grind higher with low volatility
            2. **GEX Outflow + Bullish DEX** → Explosive upside possible, buy ATM calls
            3. **GEX Inflow + Bearish DEX** → Rangebound bearish, sell call spreads
            4. **GEX Outflow + Bearish DEX** → Sharp downside risk, buy puts or stay flat
            """)
        
        with tabs[7]:
            st.markdown("### 📈 Intraday GEX/DEX Evolution")
            st.plotly_chart(create_intraday_timeline(df, selected_timestamp), use_container_width=True)
            
            st.markdown("""
            **How to use:**
            - **Yellow dashed line** shows your current selected time
            - **Move the time slider** above to see how GEX/DEX changed
            - **Watch for:**
              - GEX sign flips (suppression ↔ amplification)
              - DEX direction changes (bullish ↔ bearish)
              - Correlation with price movement
            
            **Key Insights:**
            - **Green bars** = Positive (GEX suppression, DEX bullish)
            - **Red bars** = Negative (GEX amplification, DEX bearish)
            - **Height** = Magnitude of exposure
            """)
            
            # Statistics by time period
            st.markdown("### 📊 Session Statistics")
            
            # Divide day into sessions
            df['hour'] = df['timestamp'].dt.hour
            morning = df[df['hour'] < 12].groupby('timestamp')['net_gex'].sum().mean()
            afternoon = df[df['hour'] >= 12].groupby('timestamp')['net_gex'].sum().mean()
            
            col1, col2 = st.columns(2)
            with col1:
                morning_class = "positive" if morning > 0 else "negative"
                st.markdown(f"""<div class="metric-card {morning_class}">
                    <div class="metric-label">Morning Session (9:15-12:00)</div>
                    <div class="metric-value {morning_class}">Avg GEX: {morning:.4f}B</div>
                    <div class="metric-delta">{'Lower volatility expected' if morning > 0 else 'Higher volatility expected'}</div>
                </div>""", unsafe_allow_html=True)
            
            with col2:
                afternoon_class = "positive" if afternoon > 0 else "negative"
                st.markdown(f"""<div class="metric-card {afternoon_class}">
                    <div class="metric-label">Afternoon Session (12:00-15:30)</div>
                    <div class="metric-value {afternoon_class}">Avg GEX: {afternoon:.4f}B</div>
                    <div class="metric-delta">{'Lower volatility expected' if afternoon > 0 else 'Higher volatility expected'}</div>
                </div>""", unsafe_allow_html=True)
        
        with tabs[8]:
            st.markdown("### 📋 Open Interest Distribution")
            st.plotly_chart(create_oi_distribution(df_latest, spot_price), use_container_width=True)
            
            st.markdown("### 📊 Complete Data Table")
            display_df = df_latest[['strike', 'call_oi', 'put_oi', 'call_volume', 'put_volume', 
                                   'net_gex', 'net_dex', 'hedging_pressure']].copy()
            display_df['net_gex'] = display_df['net_gex'].apply(lambda x: f"{x:.4f}B")
            display_df['net_dex'] = display_df['net_dex'].apply(lambda x: f"{x:.4f}B")
            display_df['hedging_pressure'] = display_df['hedging_pressure'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Full Historical Data (CSV)",
                data=csv,
                file_name=f"NYZTrade_Historical_{symbol}_{target_date}.csv",
                mime="text/csv"
            )
    
    else:
        # Initial instructions
        st.info("""
        👋 **Welcome to NYZTrade Historical GEX/DEX Dashboard!**
        
        This dashboard provides **comprehensive analysis** of historical options data:
        
        **Features:**
        - 🎯 **GEX (Gamma Exposure)** - Separate detailed analysis
        - 📊 **DEX (Delta Exposure)** - Separate detailed analysis  
        - ⚡ **NET GEX + DEX** - Combined exposure view
        - 🎪 **Hedging Pressure** - Separate pressure distribution
        - 🌊 **GEX Flow** - Track gamma accumulation/distribution
        - 🌊 **DEX Flow** - Monitor directional positioning changes
        - 💫 **Net Flow** - Combined flow analysis with trading signals
        - 📈 **Intraday Timeline** - See evolution throughout the day
        - 📅 **Flexible Date Ranges** - 30/60/90/180 days or custom
        - 🕐 **Indian Standard Time** - All timestamps in IST
        - ⏱️ **5/15/60-min Intervals** - Ultra-granular backtesting capability
        - 🎯 **Extended Strikes** - ATM ±6 for comprehensive analysis
        
        **How to use:**
        1. Select date range (Last 30/60/90 days or Custom)
        2. Choose specific trading day from dropdown
        3. Select your preferred index (NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY)
        4. Select time interval (5-min for scalping, 15-min for intraday, 60-min for swing)
        5. Select strikes (ATM ±6)
        6. Click "Fetch Historical Data"
        7. Use time slider to navigate through the trading day
        8. View separate charts for GEX, DEX, Flow, and more
        
        **Date Ranges Available:**
        - Last 30 Days (default)
        - Last 60 Days (2 months)
        - Last 90 Days (3 months)
        - Last 180 Days (6 months)
        - Custom Range (any dates within 6 months)
        
        **Data Source:** Dhan Rolling Options API
        
        **Backtesting:** Use 5-minute intervals for scalping analysis, 15-minute for intraday patterns, and track GEX/DEX flow changes across multiple months!
        
        **NEW: Extended Historical Data** - Analyze patterns across 2, 3, or even 6 months!
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Sample Analysis")
        st.markdown("""
        **GEX Analysis:**
        - Positive GEX = Market makers suppress volatility (range-bound)
        - Negative GEX = Volatility amplification (trending moves)
        
        **DEX Analysis:**
        - Positive DEX = Bullish positioning
        - Negative DEX = Bearish positioning
        
        **Hedging Pressure:**
        - Shows relative strength of positioning at each strike
        - Higher pressure = Stronger support/resistance
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""<div style="text-align: center; padding: 20px; color: #64748b;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
        NYZTrade Historical GEX/DEX Dashboard | Data: Dhan Rolling API | Indian Standard Time (IST)<br>
        Symbol: {symbol if 'symbol' in locals() else 'Select'} | Analysis: GEX | DEX | NET GEX+DEX | Hedge Pressure | Flow Analysis<br>
        Ultra-granular backtesting with 5-min intervals | GEX/DEX Flow tracking for position changes</p>
        <p style="font-size: 0.75rem;">⚠️ Educational purposes only. Options trading involves substantial risk.</p>
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
