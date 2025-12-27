def create_separate_gex_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """GEX chart with gamma flip zones and volume overlay - FULLY FIXED"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_sorted['net_gex']]
    
    # Identify gamma flip zones
    flip_zones = identify_gamma_flip_zones(df_sorted, spot_price)
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add GEX bars (primary y-axis)
    fig.add_trace(
        go.Bar(
            y=df_sorted['strike'],
            x=df_sorted['net_gex'],
            orientation='h',
            marker_color=colors,
            name='Net GEX',
            hovertemplate='Strike: %{y:,.0f}<br>Net GEX: %{x:.4f}B<extra></extra>',
            opacity=0.8
        ),
        secondary_y=False
    )
    
    # Add volume overlay (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            y=df_sorted['strike'],
            x=df_sorted['total_volume'],
            mode='lines+markers',
            line=dict(color='rgba(245, 158, 11, 0.6)', width=2),
            marker=dict(size=6, color='rgba(245, 158, 11, 0.8)'),
            name='Total Volume',
            hovertemplate='Strike: %{y:,.0f}<br>Volume: %{x:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Add spot price line
    fig.add_hline(
        y=spot_price, 
        line_dash="dash", 
        line_color="#06b6d4", 
        line_width=3,
        annotation_text=f"Spot: {spot_price:,.2f}", 
        annotation_position="top right",
        annotation=dict(font=dict(size=12, color="white"))
    )
    
    # Add gamma flip zones
    for zone in flip_zones:
        # Add horizontal line at flip zone
        fig.add_hline(
            y=zone['strike'],
            line_dash="dot",
            line_color=zone['color'],
            line_width=2,
            annotation_text=f"🔄 Flip {zone['arrow']} {zone['strike']:,.0f}",
            annotation_position="left",
            annotation=dict(
                font=dict(size=10, color=zone['color']),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor=zone['color'],
                borderwidth=1
            )
        )
        
        # Add shaded region around flip zone
        fig.add_hrect(
            y0=zone['lower_strike'],
            y1=zone['upper_strike'],
            fillcolor=zone['color'],
            opacity=0.1,
            line_width=0,
            annotation_text=zone['arrow'],
            annotation_position="right",
            annotation=dict(font=dict(size=16, color=zone['color']))
        )
    
    fig.update_layout(
        title=dict(
            text="<b>🎯 Gamma Exposure (GEX) with Flip Zones & Volume</b>", 
            font=dict(size=18, color='white')
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        ),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    # FULLY FIXED: Specify row and col for subplot updates
    fig.update_xaxes(
        title_text="GEX (₹ Billions)", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Strike Price", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True, 
        autorange=True,
        secondary_y=False,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Volume",
        gridcolor='rgba(128,128,128,0.1)',
        showgrid=False,
        secondary_y=True,
        row=1, col=1
    )
    
    return fig

def create_separate_dex_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """DEX chart with volume overlay - FULLY FIXED"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_sorted['net_dex']]
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add DEX bars (primary y-axis)
    fig.add_trace(
        go.Bar(
            y=df_sorted['strike'],
            x=df_sorted['net_dex'],
            orientation='h',
            marker_color=colors,
            name='Net DEX',
            hovertemplate='Strike: %{y:,.0f}<br>Net DEX: %{x:.4f}B<extra></extra>',
            opacity=0.8
        ),
        secondary_y=False
    )
    
    # Add volume overlay (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            y=df_sorted['strike'],
            x=df_sorted['total_volume'],
            mode='lines+markers',
            line=dict(color='rgba(245, 158, 11, 0.6)', width=2),
            marker=dict(size=6, color='rgba(245, 158, 11, 0.8)'),
            name='Total Volume',
            hovertemplate='Strike: %{y:,.0f}<br>Volume: %{x:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Add spot price line
    fig.add_hline(
        y=spot_price, 
        line_dash="dash", 
        line_color="#06b6d4", 
        line_width=3,
        annotation_text=f"Spot: {spot_price:,.2f}", 
        annotation_position="top right",
        annotation=dict(font=dict(size=12, color="white"))
    )
    
    fig.update_layout(
        title=dict(
            text="<b>📊 Delta Exposure (DEX) with Volume</b>", 
            font=dict(size=18, color='white')
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        ),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    # FULLY FIXED: Specify row and col for subplot updates
    fig.update_xaxes(
        title_text="DEX (₹ Billions)", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Strike Price", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True, 
        autorange=True,
        secondary_y=False,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Volume",
        gridcolor='rgba(128,128,128,0.1)',
        showgrid=False,
        secondary_y=True,
        row=1, col=1
    )
    
    return fig

def create_net_gex_dex_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Combined NET GEX+DEX chart with gamma flip zones and volume overlay - FULLY FIXED"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    df_sorted['net_gex_dex'] = df_sorted['net_gex'] + df_sorted['net_dex']
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df_sorted['net_gex_dex']]
    
    # Identify gamma flip zones (based on GEX)
    flip_zones = identify_gamma_flip_zones(df_sorted, spot_price)
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add NET GEX+DEX bars (primary y-axis)
    fig.add_trace(
        go.Bar(
            y=df_sorted['strike'],
            x=df_sorted['net_gex_dex'],
            orientation='h',
            marker_color=colors,
            name='Net GEX+DEX',
            hovertemplate='Strike: %{y:,.0f}<br>Net GEX+DEX: %{x:.4f}B<extra></extra>',
            opacity=0.8
        ),
        secondary_y=False
    )
    
    # Add volume overlay (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            y=df_sorted['strike'],
            x=df_sorted['total_volume'],
            mode='lines+markers',
            line=dict(color='rgba(245, 158, 11, 0.6)', width=2),
            marker=dict(size=6, color='rgba(245, 158, 11, 0.8)'),
            name='Total Volume',
            hovertemplate='Strike: %{y:,.0f}<br>Volume: %{x:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Add spot price line
    fig.add_hline(
        y=spot_price, 
        line_dash="dash", 
        line_color="#06b6d4", 
        line_width=3,
        annotation_text=f"Spot: {spot_price:,.2f}", 
        annotation_position="top right",
        annotation=dict(font=dict(size=12, color="white"))
    )
    
    # Add gamma flip zones
    for zone in flip_zones:
        fig.add_hline(
            y=zone['strike'],
            line_dash="dot",
            line_color=zone['color'],
            line_width=2,
            annotation_text=f"🔄 Flip {zone['arrow']} {zone['strike']:,.0f}",
            annotation_position="left",
            annotation=dict(
                font=dict(size=10, color=zone['color']),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor=zone['color'],
                borderwidth=1
            )
        )
        
        fig.add_hrect(
            y0=zone['lower_strike'],
            y1=zone['upper_strike'],
            fillcolor=zone['color'],
            opacity=0.1,
            line_width=0,
            annotation_text=zone['arrow'],
            annotation_position="right",
            annotation=dict(font=dict(size=16, color=zone['color']))
        )
    
    fig.update_layout(
        title=dict(
            text="<b>⚡ Combined NET GEX + DEX with Flip Zones & Volume</b>", 
            font=dict(size=18, color='white')
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        ),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    # FULLY FIXED: Specify row and col for subplot updates
    fig.update_xaxes(
        title_text="Combined Exposure (₹ Billions)", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Strike Price", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True, 
        autorange=True,
        secondary_y=False,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Volume",
        gridcolor='rgba(128,128,128,0.1)',
        showgrid=False,
        secondary_y=True,
        row=1, col=1
    )
    
    return fig

def create_hedging_pressure_chart(df: pd.DataFrame, spot_price: float) -> go.Figure:
    """Hedging pressure chart with gamma flip zones and volume overlay - FULLY FIXED"""
    df_sorted = df.sort_values('strike').reset_index(drop=True)
    
    # Identify gamma flip zones
    flip_zones = identify_gamma_flip_zones(df_sorted, spot_price)
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add hedging pressure bars (primary y-axis)
    fig.add_trace(
        go.Bar(
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
                    x=1.15,
                    len=0.7,
                    thickness=20
                ),
                cmin=-100,
                cmax=100
            ),
            hovertemplate='Strike: %{y:,.0f}<br>Pressure: %{x:.1f}%<extra></extra>',
            name='Hedging Pressure',
            opacity=0.8
        ),
        secondary_y=False
    )
    
    # Add volume overlay (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            y=df_sorted['strike'],
            x=df_sorted['total_volume'],
            mode='lines+markers',
            line=dict(color='rgba(245, 158, 11, 0.6)', width=2),
            marker=dict(size=6, color='rgba(245, 158, 11, 0.8)'),
            name='Total Volume',
            hovertemplate='Strike: %{y:,.0f}<br>Volume: %{x:,.0f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Add spot price line
    fig.add_hline(
        y=spot_price, 
        line_dash="dash", 
        line_color="#06b6d4", 
        line_width=3,
        annotation_text=f"Spot: {spot_price:,.2f}", 
        annotation_position="top right",
        annotation=dict(font=dict(size=12, color="white"))
    )
    
    # Add zero line
    fig.add_vline(x=0, line_dash="dot", line_color="gray", line_width=1)
    
    # Add gamma flip zones
    for zone in flip_zones:
        fig.add_hline(
            y=zone['strike'],
            line_dash="dot",
            line_color=zone['color'],
            line_width=2,
            annotation_text=f"🔄 Flip {zone['arrow']} {zone['strike']:,.0f}",
            annotation_position="left",
            annotation=dict(
                font=dict(size=10, color=zone['color']),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor=zone['color'],
                borderwidth=1
            )
        )
        
        fig.add_hrect(
            y0=zone['lower_strike'],
            y1=zone['upper_strike'],
            fillcolor=zone['color'],
            opacity=0.1,
            line_width=0,
            annotation_text=zone['arrow'],
            annotation_position="right",
            annotation=dict(font=dict(size=16, color=zone['color']))
        )
    
    fig.update_layout(
        title=dict(
            text="<b>🎪 Hedging Pressure with Flip Zones & Volume</b>", 
            font=dict(size=18, color='white')
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)',
        height=700,
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='white')
        ),
        margin=dict(l=80, r=120, t=100, b=80)
    )
    
    # FULLY FIXED: Specify row and col for subplot updates
    fig.update_xaxes(
        title_text="Hedging Pressure (%)", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True,
        zeroline=True,
        zerolinecolor='rgba(128,128,128,0.5)',
        zerolinewidth=2,
        range=[-110, 110],
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Strike Price", 
        gridcolor='rgba(128,128,128,0.2)', 
        showgrid=True, 
        autorange=True,
        secondary_y=False,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Volume",
        gridcolor='rgba(128,128,128,0.1)',
        showgrid=False,
        secondary_y=True,
        row=1, col=1
    )
    
    return fig
