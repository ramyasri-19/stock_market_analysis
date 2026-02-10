import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_pills import pills

st.set_page_config(
    page_title="Stock Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
title, info = st.columns([0.925,0.075])
with title:
    st.markdown("<h1 style='text-align: center;'>Stock Dashboard</h1>", unsafe_allow_html=True)

selected_option = option_menu(None,
                          ['Stock Analysis',
                           'Stock Tickers Comparison',
                           ],
                          icons=['bookmark tags','newspaper'],
                          default_index=0, orientation="horizontal")

file_path = "Stock_Data.xlsx"

@st.cache_data
def load_data(file):
    try:
        sheets = pd.read_excel(file, sheet_name=None)
        if 'Stock Data' in sheets:
            sheets['Stock Data']['Date'] = pd.to_datetime(sheets['Stock Data']['Date'])

        return sheets
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None
    
if selected_option == "Stock Analysis":
    stock_tickers = ["BAC", "JPM", "WFC", "C", "GS"]
    with st.container(border=True):
        selected_ticker = pills("Select a Stock Ticker to analyze:", stock_tickers, index = 0, key="selected_ticker")
    st.markdown(f"## {selected_ticker} Stock Analysis")
    data_sheets = load_data(file_path) 

    def filter_by_ticker(df, ticker):
        if df is not None and 'Ticker' in df.columns:
            return df[df['Ticker'] == ticker]
        return df

    df = filter_by_ticker(data_sheets.get('Stock Data'), selected_ticker)
    df_key_executives = filter_by_ticker(data_sheets.get('Key Executives'), selected_ticker)
    df_institutional_holders = filter_by_ticker(data_sheets.get('Top Institutional Holders'), selected_ticker)
    df_mutual_fund_holders = filter_by_ticker(data_sheets.get('Top Mutual Fund Holders'), selected_ticker)

    if df is not None:
        df = df.sort_values(by='Date', ascending=False)
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        total_days = (max_date - min_date).days
        total_years = total_days // 365
        with info:
            with st.popover(" ",icon=":material/info:"):
                st.write(f"Analyzing {selected_ticker} data from {min_date.strftime('%B %d, %Y') } to {max_date.strftime('%B %d, %Y') } over a period of {total_years} years.")
        recent_row = df.iloc[0]
        previous_row = df.iloc[1]
        recent_open = recent_row['Open']
        previous_open = previous_row['Open'] 
        recent_close = recent_row['Close']
        previous_close = previous_row['Close']
        recent_volume = recent_row['Volume']
        previous_volume = previous_row['Volume']

        dollar_change = recent_close - previous_close
        percent_change = (dollar_change / previous_close) * 100
        open_change = recent_open - previous_open 
        volume_change = recent_volume - previous_volume
        open_percent_change = (open_change / previous_open) * 100 if previous_open != 0 else 0 
        volume_percent_change = (volume_change / previous_volume) * 100 if previous_volume != 0 else 0 

        metric_1, metric_2, metric_3, metric_4 = st.columns([1,1,1,1])
        with metric_1:
            with st.container(border=True):
                st.metric("Open Value", f"${recent_open:.2f}", delta=f"{open_change:+.2f}")
        with metric_2:
            with st.container(border=True):
                st.metric("Dollar Change", f"${dollar_change:.2f}", delta=f"{dollar_change:+.2f}")
        with metric_3:
            with st.container(border=True):
                st.metric("Percentage Change", f"{percent_change:.2f}%", delta=f"{percent_change:+.2f}%")
        with metric_4: 
            with st.container(border=True):
                st.metric("Volume", f"{recent_volume:,.0f}", delta=f"{volume_change:+.0f}")
        df_key_executives_filtered = df_key_executives[['Name', 'Title']]
        mid_index = len(df_key_executives_filtered) // 2
        df_part1 = df_key_executives_filtered.iloc[:mid_index]
        df_part2 = df_key_executives_filtered.iloc[mid_index:]
        st.markdown("#### Key Executives")
        with st.container(border=True):
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                for _, row in df_part1.iterrows():
                    st.write(f"**{row['Name']}** ({row['Title']})")

            with col2:
                for _, row in df_part2.iterrows():
                    st.write(f"**{row['Name']}** ({row['Title']})")

        recent_date = df['Date'].iloc[0]
        time_options = ["1 Month", "3 Months", "6 Months", "1 Year", "10 Years"]
        with st.container(border=True):
            selected_time = pills("Select Time Period:", time_options, index = 0, key="selected_time")

        if selected_time == "1 Month":
            start_date = recent_date - pd.DateOffset(months=1)
        elif selected_time == "3 Months":
            start_date = recent_date - pd.DateOffset(months=3)
        elif selected_time == "6 Months":
            start_date = recent_date - pd.DateOffset(months=6)
        elif selected_time == "1 Year":
            start_date = recent_date - pd.DateOffset(years=1)
        elif selected_time == "10 Years":
            start_date = recent_date - pd.DateOffset(years=10)

        filtered_df = df[df['Date'] >= start_date]

        if not filtered_df.empty:
            fig_candle = go.Figure(data=[go.Candlestick(
                x=filtered_df['Date'],
                open=filtered_df['Open'],
                high=filtered_df['High'],
                low=filtered_df['Low'],
                close=filtered_df['Close'],
                name='Candlestick'
            )])
            candle_plot, volume_plot =  st.columns([1,1])
            with candle_plot:
                with st.container(border=True):
                    fig_candle.update_layout(
                        title=f"BAC Stock Candlestick Chart ({selected_time})",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        xaxis_rangeslider_visible=True,
                        template="plotly_white",
                        font=dict(size=12),
                        margin=dict(l=0, r=0, t=50, b=40),
                        showlegend=False
                    )
                    max_price = filtered_df['High'].max()
                    max_date = filtered_df.loc[filtered_df['High'].idxmax(), 'Date']
                    fig_candle.add_annotation(
                        x=max_date,
                        y=max_price,
                        text=f'Max Price: ${max_price:.2f}<br>Date: {max_date.strftime("%Y-%m-%d")}',
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=-40,
                        font=dict(color='green', size=12),
                        bgcolor='rgba(255, 255, 255, 0.7)',
                        bordercolor='green',
                        borderwidth=1,
                        borderpad=5
                    )
                    min_price = filtered_df['Low'].min()
                    min_date = filtered_df.loc[filtered_df['Low'].idxmin(), 'Date']
                    fig_candle.add_annotation(
                        x=min_date,
                        y=min_price,
                        text=f'Min Price: ${min_price:.2f}<br>Date: {min_date.strftime("%Y-%m-%d")}',
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=40,
                        font=dict(color='red', size=12),
                        bgcolor='rgba(255, 255, 255, 0.7)', 
                        bordercolor='red',
                        borderwidth=1,
                        borderpad=5
                    )
                    st.plotly_chart(fig_candle, use_container_width=True)

            with volume_plot:
                with st.container(border=True):
                    fig_volume = go.Figure()
                    fig_volume.add_trace(go.Bar(
                        x=filtered_df['Date'],
                        y=filtered_df['Volume'],
                        name='Volume',
                        marker_color='orange',
                        marker=dict(cornerradius=30)
                    ))
                    highest_volume = filtered_df['Volume'].max()
                    highest_volume_date = filtered_df.loc[filtered_df['Volume'].idxmax(), 'Date']
                    average_volume = filtered_df['Volume'].mean()
                    fig_volume.update_layout(
                        title=f"BAC Stock Trading Volume ({selected_time})",
                        xaxis_title="Date",
                        yaxis_title="Volume",
                        template="plotly_white",
                        font=dict(size=12),
                        margin=dict(l=0, r=0, t=50, b=40),
                    )
                    fig_volume.add_annotation(
                        x=highest_volume_date,
                        y=highest_volume,
                        text=f'Highest Volume: {highest_volume:,}<br>Date: {highest_volume_date.strftime("%Y-%m-%d")}',
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=-40,
                        font=dict(color='green', size=12),
                        bgcolor='rgba(255, 255, 255, 0.7)',
                        bordercolor='green',
                        borderwidth=1,
                        borderpad=5
                    )
                    fig_volume.add_annotation(
                        x=filtered_df['Date'].iloc[len(filtered_df)//2],  
                        y=average_volume,
                        text=f'Average Volume: {average_volume:,.0f}',
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=-40,
                        font=dict(color='blue', size=12),
                        bgcolor='rgba(255, 255, 255, 0.7)', 
                        bordercolor='blue',
                        borderwidth=1,
                        borderpad=5
                    )
                    st.plotly_chart(fig_volume, use_container_width=True)

            st.subheader("Technical Indicators")
            with st.expander("Technical Indicators (Set-01)", expanded = True, icon=":material/candlestick_chart:"):
                technical_1, technical_2, technical_3 = st.columns([1,1,1])
                with technical_1:
                    with st.container(border=True):
                        # Calculate Moving Averages
                        filtered_df['MA20'] = filtered_df['Close'].rolling(window=20).mean()
                        filtered_df['MA50'] = filtered_df['Close'].rolling(window=50).mean()
                        fig_ma = go.Figure()
                        fig_ma.add_trace(go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['Close'],
                            mode='lines',
                            name='Close Price',
                            line=dict(color='blue', width=2)
                        ))
                        fig_ma.add_trace(go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['MA20'],
                            mode='lines',
                            name='20-Day MA',
                            line=dict(color='red', width=2)
                        ))
                        fig_ma.add_trace(go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['MA50'],
                            mode='lines',
                            name='50-Day MA',
                            line=dict(color='green', width=2)
                        ))
                        fig_ma.update_layout(
                            title=f"BAC Stock Moving Averages ({selected_time})",
                            xaxis_title="Date",
                            yaxis_title="Price (USD)",
                            template="plotly_white",
                            hovermode='x unified',
                            font=dict(size=12),
                            margin=dict(l=0, r=0, t=50, b=40),
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.4,
                            xanchor="center",
                            x=0.4
                        )
                        )
                        st.plotly_chart(fig_ma, use_container_width=True)
                        
                with technical_2:
                    with st.container(border=True):
                        # Calculate RSI
                        delta = filtered_df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        filtered_df['RSI'] = 100 - (100 / (1 + rs))
                        fig_rsi = go.Figure()
                        fig_rsi.add_trace(go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['RSI'],
                            mode='lines',
                            name='RSI',
                            line=dict(color='blue')
                        ))
                        fig_rsi.add_annotation(
                            x=filtered_df['Date'].iloc[-1], y=80, 
                            text="Overbought Threshold (80)", 
                            showarrow=True,
                            arrowhead=2, 
                            font=dict(color='red', size=12),
                            bgcolor='rgba(255, 255, 255, 0.7)', 
                            bordercolor='red',
                            borderwidth=1,
                            borderpad=5
                        )
                        fig_rsi.add_annotation(
                            x=filtered_df['Date'].iloc[-1], y=20, 
                            text="Oversold Threshold (20)", 
                            showarrow=True,
                            arrowhead=2, 
                            font=dict(color='green', size=12),
                            bgcolor='rgba(255, 255, 255, 0.7)',
                            bordercolor='green',
                            borderwidth=1,
                            borderpad=5
                        )
                        fig_rsi.update_layout(
                            title=f"BAC Stock RSI ({selected_time})",
                            xaxis_title="Date",
                            yaxis_title="RSI",
                            template="plotly_white",
                            hovermode='x unified',
                            font=dict(size=12),
                            margin=dict(l=0, r=0, t=50, b=40),
                            shapes=[ 
                                dict(type='rect', xref='paper', x0=0, x1=1, y0=80, y1=100, 
                                    fillcolor='rgba(255, 0, 0, 0.1)', line_width=0),
                                dict(type='rect', xref='paper', x0=0, x1=1, y0=0, y1=20, 
                                    fillcolor='rgba(0, 255, 0, 0.1)', line_width=0)
                            ]
                        )
                        st.plotly_chart(fig_rsi, use_container_width=True)

                with technical_3:
                    with st.container(border=True):
                        # Calculate Bollinger Bands
                        window = 20
                        std = filtered_df['Close'].rolling(window).std()
                        filtered_df['Upper Band'] = filtered_df['MA20'] + (std * 2)
                        filtered_df['Lower Band'] = filtered_df['MA20'] - (std * 2)
                        fig_bollinger = go.Figure()
                        fig_bollinger.add_trace(go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['Close'],
                            mode='lines',
                            name='Close Price',
                            line=dict(color='blue', width=2)
                        ))
                        fig_bollinger.add_trace(go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['Upper Band'],
                            mode='lines',
                            name='Upper Band',
                            line=dict(color='red', width=2),
                            fill=None
                        ))
                        fig_bollinger.add_trace(go.Scatter(
                            x=filtered_df['Date'],
                            y=filtered_df['Lower Band'],
                            mode='lines',
                            name='Lower Band',
                            line=dict(color='green', width=2),
                            fill='tonexty'
                        ))
                        fig_bollinger.update_layout(
                            title=f"Bollinger Bands ({selected_time})",
                            xaxis_title="Date",
                            yaxis_title="Price (USD)",
                            template="plotly_white",
                            font=dict(size=12),
                            margin=dict(l=0, r=0, t=50, b=40),
                            hovermode='x unified',
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.4,
                            xanchor="center",
                            x=0.4
                        )
                        )
                        st.plotly_chart(fig_bollinger, use_container_width=True)

            with st.expander("Technical Indicators (Set-02)", expanded = False, icon=":material/candlestick_chart:"):
                technical_4, technical_5, technical_6 = st.columns([1,1,1])
            
                with technical_4:
                    with st.container(border=True):
                        # Volume Weighted Average Price (VWAP)
                        vwap = (filtered_df['Close'] * filtered_df['Volume']).cumsum() / filtered_df['Volume'].cumsum()
                        filtered_df['VWAP'] = vwap
                        fig_vwap = go.Figure()
                        fig_vwap.add_trace(go.Scatter(
                            x=filtered_df['Date'], 
                            y=filtered_df['Close'], 
                            mode='lines', 
                            name='Close Price'
                        ))
                        fig_vwap.add_trace(go.Scatter(
                            x=filtered_df['Date'], 
                            y=filtered_df['VWAP'], 
                            mode='lines', 
                            name='VWAP', 
                            line=dict(dash='dot', color='firebrick')
                        ))
                        highest_close = filtered_df.loc[filtered_df['Close'].idxmax()]
                        lowest_close = filtered_df.loc[filtered_df['Close'].idxmin()]
                        most_recent_vwap = filtered_df.iloc[-1]
                        fig_vwap.add_annotation(
                            x=highest_close['Date'], 
                            y=highest_close['Close'], 
                            text=f"Peak Close: {highest_close['Close']:.2f}", 
                            showarrow=True, 
                            arrowhead=2, 
                            ax=0, ay=-40,
                            bgcolor='rgba(255, 255, 255, 0.7)', 
                            font=dict(color='green', size=12), 
                            bordercolor="green", 
                            borderwidth=1, 
                            borderpad=5
                        )
                        fig_vwap.add_annotation(
                            x=lowest_close['Date'], 
                            y=lowest_close['Close'], 
                            text=f"Trough Close: {lowest_close['Close']:.2f}", 
                            showarrow=True, 
                            arrowhead=2, 
                            ax=0, ay=40,
                            font=dict(color='red', size=12),
                            bgcolor='rgba(255, 255, 255, 0.7)', 
                            bordercolor='red',
                            borderwidth=1,
                            borderpad=5
                        )
                        fig_vwap.update_layout(
                            title=f'BAC Volume Weighted Average Price (VWAP) ({selected_time})',
                            xaxis_title='Date',
                            yaxis_title='Price (USD)',
                            legend=dict(
                                orientation='h', 
                                yanchor='bottom', 
                                y=-0.4, 
                                xanchor='center', 
                                x=0.4
                            ),
                            template='plotly_white',
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig_vwap)

                with technical_5:
                    with st.container(border=True):
                        # Stochastic Oscillator Calculation
                        min_low = filtered_df['Low'].rolling(window=14).min()
                        max_high = filtered_df['High'].rolling(window=14).max()
                        filtered_df['%K'] = 100 * (filtered_df['Close'] - min_low) / (max_high - min_low)
                        filtered_df['%D'] = filtered_df['%K'].rolling(window=3).mean()
                        fig_stochastic = go.Figure()
                        fig_stochastic.add_trace(go.Scatter(
                            x=filtered_df['Date'], y=filtered_df['%K'], 
                            mode='lines', name='%K', 
                            line=dict(color='blue')
                        ))
                        fig_stochastic.add_trace(go.Scatter(
                            x=filtered_df['Date'], y=filtered_df['%D'], 
                            mode='lines', name='%D', 
                            line=dict(color='orange', dash='dot')
                        ))
                        fig_stochastic.add_shape(
                            type="line", x0=filtered_df['Date'].min(), y0=80, 
                            x1=filtered_df['Date'].max(), y1=80, 
                            line=dict(color="red", dash="dash")
                        )

                        fig_stochastic.add_shape(
                            type="line", x0=filtered_df['Date'].min(), y0=20, 
                            x1=filtered_df['Date'].max(), y1=20, 
                            line=dict(color="green", dash="dash")
                        )
                        fig_stochastic.update_layout(
                            title=f'BAC Stochastic Oscillator ({selected_time})',
                            xaxis_title='Date',
                            yaxis_title='Stochastic Value',
                            legend=dict(
                                orientation='h',
                                yanchor='bottom', 
                                y=-0.4, 
                                xanchor='center', 
                                x=0.4
                            ),
                            template='plotly_white',
                            hovermode='x unified',
                            shapes=[
                                dict(type='rect', xref='paper', x0=0, x1=1, y0=80, y1=100, 
                                    fillcolor='rgba(255, 0, 0, 0.1)', line_width=0),
                                dict(type='rect', xref='paper', x0=0, x1=1, y0=0, y1=20, 
                                    fillcolor='rgba(0, 255, 0, 0.1)', line_width=0)
                            ]
                        )
                        st.plotly_chart(fig_stochastic)


                with technical_6:
                    with st.container(border=True):
                        # Average True Range (ATR)
                        high_low = filtered_df['High'] - filtered_df['Low']
                        high_close = (filtered_df['High'] - filtered_df['Close'].shift()).abs()
                        low_close = (filtered_df['Low'] - filtered_df['Close'].shift()).abs()
                        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                        filtered_df['ATR'] = true_range.rolling(window=14).mean()
                        fig_atr = go.Figure()
                        fig_atr.add_trace(go.Scatter(
                            x=filtered_df['Date'], 
                            y=filtered_df['ATR'], 
                            mode='lines', 
                            name='ATR', 
                            line=dict(color='purple')
                        ))
                        max_atr = filtered_df.loc[filtered_df['ATR'].idxmax()]
                        latest_atr = filtered_df.iloc[-1]
                        fig_atr.add_annotation(
                            x=max_atr['Date'], y=max_atr['ATR'], 
                            text=f"Max ATR: {max_atr['ATR']:.2f}", 
                            showarrow=True, arrowhead=2, ax=-50, ay=-20,
                            font=dict(color='red', size=12),
                            bgcolor='rgba(255, 255, 255, 0.7)',
                            bordercolor='red',
                            borderwidth=1,
                            borderpad=5
                        )
                        fig_atr.add_shape(
                            type='rect', xref='paper', x0=0, x1=1, y0=max_atr['ATR'] * 0.75, y1=max_atr['ATR'], 
                            fillcolor='rgba(255, 0, 0, 0.1)', line_width=0
                        )
                        fig_atr.add_shape(
                            type='rect', xref='paper', x0=0, x1=1, y0=0, y1=max_atr['ATR'] * 0.25, 
                            fillcolor='rgba(0, 255, 0, 0.1)', line_width=0
                        )
                        fig_atr.update_layout(
                            title='BAC Average True Range (ATR)',
                            xaxis_title='Date',
                            yaxis_title='ATR Value',
                            legend=dict(
                                orientation='h',
                                yanchor='bottom',
                                y=1.02,
                                xanchor='right',
                                x=1
                            ),
                            template='plotly_white',
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig_atr)


            with st.expander("Technical Indicators (Set-03)", expanded = False, icon=":material/candlestick_chart:"):
                technical_7, technical_8, technical_9 = st.columns([1,1,1])
            
                with technical_7:
                    with st.container(border=True):
                        # Average Volume
                        filtered_df['Avg_Volume'] = filtered_df['Volume'].rolling(window=30).mean()
                        fig_avg_volume = go.Figure()
                        fig_avg_volume.add_trace(go.Scatter(
                            x=filtered_df['Date'], 
                            y=filtered_df['Volume'], 
                            mode='lines', 
                            name='Daily Volume',
                            line=dict(color='blue')
                        ))
                        fig_avg_volume.add_trace(go.Scatter(
                            x=filtered_df['Date'], 
                            y=filtered_df['Avg_Volume'], 
                            mode='lines', 
                            name='30-Day Avg Volume',
                            line=dict(color='orange')
                        ))
                        max_volume = filtered_df['Volume'].max()
                        min_volume = filtered_df['Volume'].min()
                        fig_avg_volume.add_annotation(
                            x=filtered_df['Date'][filtered_df['Volume'].idxmax()], 
                            y=max_volume, 
                            text=f"Max Volume: {max_volume:.0f}",
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=-40,
                            bgcolor="rgba(255, 255, 255, 0.8)",
                            bordercolor="green",
                            borderwidth=1,
                            borderpad=4,
                            font=dict(color="green")
                        )

                        fig_avg_volume.add_annotation(
                            x=filtered_df['Date'][filtered_df['Volume'].idxmin()], 
                            y=min_volume, 
                            text=f"Min Volume: {min_volume:.0f}",
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=40,
                            bgcolor="rgba(255, 255, 255, 0.8)",
                            bordercolor="red",
                            borderwidth=1,
                            borderpad=4,
                            font=dict(color="red")
                        )
                        fig_avg_volume.update_layout(
                            title=f'BAC Volume with Average ({selected_time})',
                            xaxis_title='Date',
                            yaxis_title='Volume',
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.4,
                            xanchor="center",
                            x=0.4
                        )
                        )
                        st.plotly_chart(fig_avg_volume)


                with technical_8:
                    with st.container(border=True):
                        # Rate of Change (ROC)
                        filtered_df['ROC'] = filtered_df['Close'].pct_change(periods=12) * 100
                        fig_roc = go.Figure()
                        fig_roc.add_trace(go.Scatter(
                            x=filtered_df['Date'], 
                            y=filtered_df['ROC'], 
                            mode='lines', 
                            name='ROC',
                            line=dict(color='blue')
                        ))
                        max_roc = filtered_df['ROC'].max()
                        min_roc = filtered_df['ROC'].min()
                        fig_roc.add_annotation(
                            x=filtered_df['Date'][filtered_df['ROC'].idxmax()], 
                            y=max_roc, 
                            text=f"Max ROC: {max_roc:.2f}%",
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=-40,
                            bgcolor="rgba(255, 255, 255, 0.8)",
                            bordercolor="green",
                            borderwidth=1,
                            borderpad=4,
                            font=dict(color="green")
                        )
                        fig_roc.add_annotation(
                            x=filtered_df['Date'][filtered_df['ROC'].idxmin()], 
                            y=min_roc, 
                            text=f"Min ROC: {min_roc:.2f}%",
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=40,
                            bgcolor="rgba(255, 255, 255, 0.8)",
                            bordercolor="red",
                            borderwidth=1,
                            borderpad=4,
                            font=dict(color="red")
                        )
                        fig_roc.update_layout(
                            title=f'BAC Rate of Change ({selected_time})',
                            xaxis_title='Date',
                            yaxis_title='ROC (%)'
                        )
                        st.plotly_chart(fig_roc)


                with technical_9:
                    with st.container(border=True):
                        # On-Balance Volume (OBV)
                        filtered_df['Direction'] = np.where(filtered_df['Close'] >= filtered_df['Close'].shift(1), 1, -1)
                        filtered_df['OBV'] = (filtered_df['Volume'] * filtered_df['Direction']).cumsum()
                        fig_obv = go.Figure()
                        fig_obv.add_trace(go.Scatter(
                            x=filtered_df['Date'], 
                            y=filtered_df['OBV'], 
                            mode='lines', 
                            name='OBV',
                            line=dict(color='blue')
                        ))
                        max_obv = filtered_df['OBV'].max()
                        min_obv = filtered_df['OBV'].min()
                        fig_obv.add_annotation(
                            x=filtered_df['Date'][filtered_df['OBV'].idxmax()], 
                            y=max_obv, 
                            text=f"Max OBV: {max_obv:.2f}",
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=-40,
                            bgcolor="rgba(255, 255, 255, 0.8)",
                            bordercolor="green",
                            borderwidth=1,
                            borderpad=4,
                            font=dict(color="green")
                        )
                        fig_obv.add_annotation(
                            x=filtered_df['Date'][filtered_df['OBV'].idxmin()], 
                            y=min_obv, 
                            text=f"Min OBV: {min_obv:.2f}",
                            showarrow=True,
                            arrowhead=2,
                            ax=0,
                            ay=40,
                            bgcolor="rgba(255, 255, 255, 0.8)",
                            bordercolor="red",
                            borderwidth=1,
                            borderpad=4,
                            font=dict(color="red")
                        )
                        fig_obv.update_layout(
                            title=f'BAC On-Balance Volume (OBV) ({selected_time})',
                            xaxis_title='Date',
                            yaxis_title='OBV Value'
                        )
                        st.plotly_chart(fig_obv)

            def convert_shares(value):
                if 'B' in value:
                    return float(value.replace('B', '')) * 1e9
                elif 'M' in value:
                    return float(value.replace('M', '')) * 1e6
                else:
                    return float(value)
            pie_1, pie_2 = st.columns(2)
            with pie_1:
                with st.container(border=True):
                    df_institutional_holders = df_institutional_holders[['Holder', 'Shares']]
                    df_institutional_holders['Shares'] = df_institutional_holders['Shares'].apply(convert_shares)
                    fig = px.pie(
                        df_institutional_holders,
                        names='Holder',
                        values='Shares',
                        title='Top Institutional Holders by Shares',
                        hole=0.4
                    )
                    fig.update_layout(
                    legend=dict(
                        orientation="h",  
                        yanchor="bottom", 
                        y=-0.6,         
                        xanchor="center", 
                        x=0.5            
                    )
                )
                    st.plotly_chart(fig, use_container_width=True)
            
            with pie_2:
                with st.container(border=True):
                    df_mutual_fund_holders = df_mutual_fund_holders[['Holder', 'Shares']]
                    df_mutual_fund_holders['Shares'] = df_mutual_fund_holders['Shares'].apply(convert_shares)
                    fig = px.pie(
                        df_mutual_fund_holders,
                        names='Holder',
                        values='Shares',
                        title='Top Mutual Fund Holders by Shares',
                        hole=0.4
                    )
                    fig.update_layout(
                    legend=dict(
                        orientation="h",  
                        yanchor="bottom", 
                        y=-0.6,         
                        xanchor="right", 
                        x=0.5,
                        bgcolor='rgba(0,0,0,0)'            
                    )
                    )
                    st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No data available for the selected date range.")
    else:
        st.error("Data could not be loaded.")

elif selected_option == "Stock Tickers Comparison":
    stock_tickers = ["BAC", "JPM", "WFC", "C", "GS"]
    with st.container(border=True):
        selected_tickers = st.multiselect("Select Stock Ticker(s) to analyze:", stock_tickers, default=["BAC", "JPM"])
    st.markdown(f"## Stock Comparision for ({', '.join(selected_tickers)})")
    data_sheets = load_data(file_path) 

    def filter_by_tickers(df, tickers):
        """Filter data by selected tickers."""
        if df is not None and 'Ticker' in df.columns:
            return df[df['Ticker'].isin(tickers)]
        return df

    df = filter_by_tickers(data_sheets.get('Stock Data'), selected_tickers)
    df_key_executives = filter_by_tickers(data_sheets.get('Key Executives'), selected_tickers)
    df_institutional_holders = filter_by_tickers(data_sheets.get('Top Institutional Holders'), selected_tickers)
    df_mutual_fund_holders = filter_by_tickers(data_sheets.get('Top Mutual Fund Holders'), selected_tickers)

    if df is not None:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date', ascending=False)
        min_date = df['Date'].min()
        min_date_dummy = pd.to_datetime("2023-10-14")
        max_date = df['Date'].max()
        start_date, end_date = st.date_input(
            "Select Date Range:",
            [min_date_dummy.date(), max_date.date()], 
            max_value=max_date.date(),
        )
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        total_days = (max_date - min_date).days
        total_years = total_days // 365
        if not filtered_df.empty:
            with info:
                with st.popover(" ",icon=":material/info:"):
                    st.write(f"Comparing data for {', '.join(selected_tickers)} from "
            f"{min_date.strftime('%B %d, %Y')} to {max_date.strftime('%B %d, %Y')} "
            f"over a period of {total_years} years.")
            # Line Chart
            major_change_threshold = 0.05 
            fig_line = go.Figure()
            for ticker in selected_tickers:
                ticker_data = filtered_df[filtered_df['Ticker'] == ticker]
                ticker_data = ticker_data.sort_values(by='Date')
                fig_line.add_trace(go.Scatter(x=ticker_data['Date'], y=ticker_data['Close'],
                                            mode='lines', name=ticker, line=dict(width=2)))
                ticker_data['Price_Change'] = ticker_data['Close'].pct_change()
                major_up = ticker_data[ticker_data['Price_Change'] > major_change_threshold]
                major_down = ticker_data[ticker_data['Price_Change'] < -major_change_threshold]
                for index, row in major_up.iterrows():
                    fig_line.add_annotation(
                        x=row['Date'],
                        y=row['Close'],
                        text='Significant Rise<br>+{:.1%}'.format(row['Price_Change']), 
                        showarrow=True,
                        arrowhead=3, 
                        ax=0,
                        ay=-40, 
                        font=dict(color='green', size=12),
                        bgcolor='white', 
                        bordercolor='green', 
                        borderwidth=1, 
                        borderpad=4,
                        align='center'
                    )
                for index, row in major_down.iterrows():
                    fig_line.add_annotation(
                        x=row['Date'],
                        y=row['Close'],
                        text='Significant Drop<br>-{:.1%}'.format(abs(row['Price_Change'])),  # Absolute value for drop
                        showarrow=True,
                        arrowhead=3, 
                        ax=0,
                        ay=40, 
                        font=dict(color='red', size=12),
                        bgcolor='white', 
                        bordercolor='red', 
                        borderwidth=1,
                        borderpad=4, 
                        align='center' 
                    )
            fig_line.update_layout(
                title='Line Chart of Stock Prices',
                xaxis_title='Date',
                yaxis_title='Price',
                margin=dict(l=40, r=40, t=40, b=40) 
            )
            with st.container(border=True):
                st.plotly_chart(fig_line)

            # Candlestick Chart
            fig_candlestick = go.Figure()
            for ticker in selected_tickers:
                ticker_data = filtered_df[filtered_df['Ticker'] == ticker]
                fig_candlestick.add_trace(go.Candlestick(x=ticker_data['Date'],
                                                        open=ticker_data['Open'],
                                                        high=ticker_data['High'],
                                                        low=ticker_data['Low'],
                                                        close=ticker_data['Close'],
                                                        name=ticker))
            fig_candlestick.update_layout(title='Candlestick Chart',
                                        xaxis_title='Date', yaxis_title='Price')
            with st.container(border=True):
                st.plotly_chart(fig_candlestick)

            # Stacked Bar Chart
            bar_data = filtered_df.pivot_table(index='Date', columns='Ticker', values='Volume', aggfunc='sum').fillna(0)
            fig_bar = go.Figure(data=[go.Bar(name=ticker, x=bar_data.index, y=bar_data[ticker]) for ticker in selected_tickers], layout=dict(barcornerradius=15))
            fig_bar.update_layout(title='Stacked Bar Chart of Trading Volume',
                                barmode='stack', xaxis_title='Date', yaxis_title='Volume')
            with st.container(border=True):
                st.plotly_chart(fig_bar)

            # Box Plot for Prices
            fig_box = go.Figure()
            for ticker in selected_tickers:
                ticker_data = filtered_df[filtered_df['Ticker'] == ticker]
                fig_box.add_trace(go.Box(y=ticker_data['Close'], name=ticker))
            fig_box.update_layout(title='Box Plot of Stock Prices', yaxis_title='Price')
            with st.container(border=True):
                st.plotly_chart(fig_box)

            # Percent Change Chart
            percent_change = filtered_df.pivot_table(index='Date', columns='Ticker', values='Close').pct_change().fillna(0)
            fig_percent_change = go.Figure()
            for ticker in selected_tickers:
                fig_percent_change.add_trace(go.Scatter(x=percent_change.index, y=percent_change[ticker], mode='lines', name=ticker))
            fig_percent_change.update_layout(title='Percent Change Chart',
                                            xaxis_title='Date', yaxis_title='Percent Change')
            with st.container(border=True):
                st.plotly_chart(fig_percent_change)

            # Multi-Series Time Series Chart
            fig_multi_series = go.Figure()
            for ticker in selected_tickers:
                ticker_data = filtered_df[filtered_df['Ticker'] == ticker]
                fig_multi_series.add_trace(go.Scatter(x=ticker_data['Date'], y=ticker_data['Close'], mode='lines', name=ticker))
            fig_multi_series.update_layout(title='Multi-Series Time Series Chart',
                                            xaxis_title='Date', yaxis_title='Price')
            with st.container(border=True):
                st.plotly_chart(fig_multi_series)
            
            
        else:
            st.warning("No data available for the selected date range.")
    else:
        st.warning("No data available for the selected ticker(s).")

