"""
Professional Business Dashboard - Finansiell Analys
"""
import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    st.error("❌ Plotly är inte installerat. Installera med: pip install plotly")
    PLOTLY_AVAILABLE = False
    
import sys
import os

# Add current directory to Python path for deployment compatibility
try:
    # When running as a script, __file__ is available
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # When running with exec() or in some deployment contexts
    current_dir = os.getcwd()

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from financial_analyzer import FinancialAnalyzer

# Konfiguration för professionell look
st.set_page_config(
    page_title="Finansiell Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS för business look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        border-left: 5px solid #1f4e79;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f4e79;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: 500;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f4e79;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    """Secure password check using Streamlit secrets"""
    def password_entered():
        # Hämta användarnamn och lösenord från secrets (med fallback för lokal utveckling)
        try:
            correct_username = st.secrets["auth"]["username"]
            correct_password = st.secrets["auth"]["password"]
        except:
            # Fallback för lokal utveckling
            correct_username = "Admin"
            correct_password = "Sention1!"
        
        entered_username = st.session_state.get("username_input", "").strip()
        entered_password = st.session_state.get("password_input", "")
        
        if entered_username == correct_username and entered_password == correct_password:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_username"] = entered_username
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("## 🔐 Inloggning")
        st.text_input("Användarnamn", key="username_input", placeholder="Ange användarnamn")
        st.text_input("Lösenord", type="password", on_change=password_entered, key="password_input")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("## 🔐 Inloggning")
        st.text_input("Användarnamn", key="username_input", placeholder="Ange användarnamn")
        st.text_input("Lösenord", type="password", on_change=password_entered, key="password_input")
        st.error("❌ Felaktigt användarnamn eller lösenord")
        return False
    else:
        return True

def load_financial_data():
    """Laddar finansiell data"""
    try:
        analyzer = FinancialAnalyzer()
        return analyzer
    except Exception as e:
        st.error(f"Fel vid laddning av data: {e}")
        return None

def convert_excel_value(value):
    """Konverterar Excel-värde till nummer - hanterar svenska format"""
    if pd.isna(value) or value == "None" or value == "":
        return 0
    try:
        # Konvertera till string
        val_str = str(value).strip()
        
        # Ta bort eventuella mellanslag (tusentalseparatorer)
        val_str = val_str.replace(' ', '')
        
        # Ersätt komma med punkt för decimaler
        val_str = val_str.replace(',', '.')
        
        return float(val_str)
    except:
        return 0

def get_monthly_data(analyzer, sheet_name):
    """Hämtar månadsdata DIREKT från SUMMA-raderna och BERÄKNAT RESULTAT från Excel"""
    raw_data = analyzer.get_raw_data(sheet_name)
    if raw_data is None:
        return None, None, None
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    monthly_revenue = []
    monthly_expenses = []
    monthly_net_result = []
    
    # Hitta relevanta rader
    revenue_row = None
    expense_row = None
    net_result_row = None
    
    for idx, row in raw_data.iterrows():
        category = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
        
        # Hitta intäktsraden - flexibel matchning
        if any(keyword in category.upper() for keyword in ['SUMMA RÖRELSENS INTÄKTER', 'SUMMA NETTOOMSÄTTNING']):
            revenue_row = row
        elif 'SUMMA RÖRELSENS KOSTNADER' in category:
            expense_row = row
        elif 'BERÄKNAT RESULTAT' in category:
            net_result_row = row
    
    # Läs månadsdata från raderna
    for month in months:
        # Hitta månadskolumn
        month_col_idx = None
        for col_idx, col_name in enumerate(raw_data.columns):
            if str(col_name).strip() == month:
                month_col_idx = col_idx
                break
        
        if month_col_idx is not None:
            # Läs från SUMMA RÖRELSENS INTÄKTER (alltid positivt)
            if revenue_row is not None:
                revenue_val = convert_excel_value(revenue_row.iloc[month_col_idx])
                monthly_revenue.append(abs(revenue_val))
            else:
                monthly_revenue.append(0)
            
            # Läs från SUMMA RÖRELSENS KOSTNADER (behåll negativt tecken)
            if expense_row is not None:
                expense_val = convert_excel_value(expense_row.iloc[month_col_idx])
                monthly_expenses.append(expense_val)
            else:
                monthly_expenses.append(0)
            
            # Läs från BERÄKNAT RESULTAT (direkt från Excel)
            if net_result_row is not None:
                net_val = convert_excel_value(net_result_row.iloc[month_col_idx])
                monthly_net_result.append(net_val)
        else:
            monthly_net_result.append(0)
    else:
            monthly_revenue.append(0)
            monthly_expenses.append(0)
            monthly_net_result.append(0)
    
    return monthly_revenue, monthly_expenses, monthly_net_result

def create_multi_company_comparison(analyzer, selected_sheets):
    """Skapar jämförelsediagram för flera företag"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    fig = go.Figure()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, sheet in enumerate(selected_sheets):
        monthly_revenue, monthly_expenses, monthly_net_result = get_monthly_data(analyzer, sheet)
        
        if monthly_revenue is None:
            continue
            
        color = colors[i % len(colors)]
        
        # Lägg till nettoresultat för varje företag
        fig.add_trace(go.Scatter(
            x=months,
            y=monthly_net_result,
            mode='lines+markers',
            name=f'{sheet} - Nettoresultat',
            line=dict(color=color, width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{sheet}</b><br>%{{x}}<br>Nettoresultat: %{{y:,.1f}} tSEK<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(text=f'Nettoresultat Jämförelse - {len(selected_sheets)} Företag', font=dict(size=20, color='#1f4e79')),
        xaxis_title='Månad',
        yaxis_title='Nettoresultat (tSEK)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def get_yearly_totals_from_excel(analyzer, sheet_name):
    """Hämtar årssummor DIREKT från Excel's SUMMA-kolumn - ENKEL och ROBUST"""
    raw_data = analyzer.get_raw_data(sheet_name)
    if raw_data is None:
        return 0, 0, 0
    
    # Hitta Totalt-kolumnen
    summa_col_idx = None
    for col_idx, col_name in enumerate(raw_data.columns):
        if str(col_name).strip() == 'Totalt':
            summa_col_idx = col_idx
            break
    
    if summa_col_idx is None:
        summa_col_idx = len(raw_data.columns) - 1
    
    # Hitta rader med ENKEL matching
    revenue_total = 0
    expense_total = 0
    net_result_total = 0
    
    for idx, row in raw_data.iterrows():
        category = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
        
        # Flexibel matchning för intäkter - hitta rätt rad oberoende av format
        if any(keyword in category.upper() for keyword in ['SUMMA RÖRELSENS INTÄKTER', 'SUMMA NETTOOMSÄTTNING']):
            revenue_total = convert_excel_value(row.iloc[summa_col_idx])
        elif 'SUMMA RÖRELSENS KOSTNADER' in category:
            expense_total = convert_excel_value(row.iloc[summa_col_idx])
        elif 'BERÄKNAT RESULTAT' in category:
            net_result_total = convert_excel_value(row.iloc[summa_col_idx])
    
    return revenue_total, expense_total, net_result_total

def create_multi_company_bar_chart(analyzer, selected_sheets):
    """Skapar stapeldiagram för flera företag"""
    import plotly.graph_objects as go
    
    companies = []
    revenues = []
    expenses = []
    net_results = []
    
    for sheet in selected_sheets:
        # Läs DIREKT från Excel's SUMMA-kolumn
        total_revenue, total_expenses, net_result = get_yearly_totals_from_excel(analyzer, sheet)
        
        # Acceptera alla företag, även de med 0-värden
        companies.append(sheet)
        revenues.append(total_revenue if total_revenue is not None else 0)
        expenses.append(total_expenses if total_expenses is not None else 0)
        net_results.append(net_result if net_result is not None else 0)
    
    if not companies:
        return None
    
    fig = go.Figure()
    
    # Intäkter (positiva staplar)
    fig.add_trace(go.Bar(
        x=companies,
        y=revenues,
        name='Intäkter',
        marker_color='#28a745',
        hovertemplate='<b>%{x}</b><br>Intäkter: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    # Kostnader (negativa staplar)
    fig.add_trace(go.Bar(
        x=companies,
        y=expenses,
        name='Kostnader',
        marker_color='#dc3545',
        hovertemplate='<b>%{x}</b><br>Kostnader: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    # Nettoresultat (blå staplar)
    fig.add_trace(go.Bar(
        x=companies,
        y=net_results,
        name='Nettoresultat',
        marker_color='#007bff',
        hovertemplate='<b>%{x}</b><br>Nettoresultat: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Företagsjämförelse - Finansiell Översikt', font=dict(size=20, color='#1f4e79')),
        xaxis_title='Företag/År',
        yaxis_title='Belopp (tSEK)',
        barmode='group',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def display_multi_company_kpis(analyzer, selected_sheets):
    """Visar KPI-sammanfattning för flera företag"""
    st.markdown('<div class="section-header">📋 KPI Sammanfattning</div>', unsafe_allow_html=True)
    
    company_data = []
    
    for sheet in selected_sheets:
        # Läs DIREKT från Excel's SUMMA-kolumn
        total_revenue, total_expenses, net_result = get_yearly_totals_from_excel(analyzer, sheet)
        
        # Inkludera alla företag, även de med 0-värden för att visa alla
            
        # Säkerställ rätt tecken
        total_revenue = abs(total_revenue) if total_revenue else 0
        total_expenses = total_expenses if total_expenses else 0  # Behåll negativt från Excel
        net_result = net_result if net_result else 0
        
        profit_margin = (net_result / total_revenue * 100) if total_revenue > 0 else 0
        
        company_data.append({
            'Företag/År': sheet,
            'Totala Intäkter (tSEK)': f"{total_revenue:,.1f}",
            'Totala Kostnader (tSEK)': f"{total_expenses:,.1f}",
            'Nettoresultat (tSEK)': f"{net_result:,.1f}",
            'Vinstmarginal (%)': f"{profit_margin:.1f}%"
        })
    
    if company_data:
        df = pd.DataFrame(company_data)
        st.dataframe(df, use_container_width=True)

def create_monthly_line_chart(monthly_revenue, monthly_expenses, monthly_net_result):
    """Skapar månadsvis linjediagram"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    
    fig = go.Figure()
    
    # Intäkter
    fig.add_trace(go.Scatter(
        x=months,
        y=monthly_revenue,
        mode='lines+markers',
        name='Intäkter',
        line=dict(color='#28a745', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Intäkter: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    # Kostnader
    fig.add_trace(go.Scatter(
        x=months,
        y=monthly_expenses,
        mode='lines+markers',
        name='Kostnader',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Kostnader: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    # Nettoresultat (direkt från Excel BERÄKNAT RESULTAT)
    fig.add_trace(go.Scatter(
        x=months,
        y=monthly_net_result,
        mode='lines+markers',
        name='Nettoresultat',
        line=dict(color='#007bff', width=3, dash='dot'),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Nettoresultat: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Månadsvis Finansiell Utveckling', font=dict(size=20, color='#1f4e79')),
        xaxis_title='Månad',
        yaxis_title='Belopp (tSEK)',
        template='plotly_white',
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_monthly_bar_chart(monthly_revenue, monthly_expenses, monthly_net_result):
    """Skapar stapeldiagram för månadsöversikt"""
    import plotly.graph_objects as go
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    
    fig = go.Figure()
    
    # Intäkter (positiva staplar)
    fig.add_trace(go.Bar(
        x=months,
        y=monthly_revenue,
        name='Intäkter',
        marker_color='#28a745',
        hovertemplate='<b>%{x}</b><br>Intäkter: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    # Kostnader (negativa staplar)
    fig.add_trace(go.Bar(
        x=months,
        y=monthly_expenses,
        name='Kostnader',
        marker_color='#dc3545',
        hovertemplate='<b>%{x}</b><br>Kostnader: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    # Nettoresultat (blå staplar)
    fig.add_trace(go.Bar(
        x=months,
        y=monthly_net_result,
        name='Nettoresultat',
        marker_color='#007bff',
        hovertemplate='<b>%{x}</b><br>Nettoresultat: %{y:,.1f} tSEK<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Månadsvis Finansiell Översikt', font=dict(size=20, color='#1f4e79')),
        xaxis_title='Månad',
        yaxis_title='Belopp (tSEK)',
        barmode='group',
        template='plotly_white',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_revenue_detail_chart(analyzer, sheet_name):
    """Skapar detaljerat diagram för intäktskategorier"""
    import plotly.graph_objects as go
    
    raw_data = analyzer.get_raw_data(sheet_name)
    if raw_data is None:
        return None
    
    # Hitta intäktskategorier (rader som inte är SUMMA och har positiva värden)
    revenue_categories = []
    revenue_totals = []
    
    # Hitta SUMMA-kolumnen
    summa_col_idx = len(raw_data.columns) - 1
    
    # Innan SUMMA RÖRELSENS INTÄKTER = intäkter, efter = kostnader
    found_revenue_summa = False
    
    for idx, row in raw_data.iterrows():
        category = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
        
        # Kolla om vi hittat intäktsraden (flexibel matchning)
        if any(keyword in category.upper() for keyword in ['SUMMA RÖRELSENS INTÄKTER', 'SUMMA NETTOOMSÄTTNING']):
            found_revenue_summa = True
            continue
            
        # Skippa SUMMA-rader och tomma kategorier
        if 'SUMMA' in category.upper() or 'BERÄKNAT' in category.upper() or category.strip() == "":
            continue
            
        # Läs värdet från SUMMA-kolumnen
        total_val = convert_excel_value(row.iloc[summa_col_idx])
        
        # Bara intäkter (innan SUMMA RÖRELSENS INTÄKTER och positiva värden)
        if not found_revenue_summa and total_val > 10:  # Bara kategorier över 10 tSEK
            # Rensa och förkorta kategorinamnet
            clean_category = category.strip()[:40]  # Lite längre för bättre läsbarhet
            revenue_categories.append(clean_category)
            revenue_totals.append(total_val)
    
    if not revenue_categories:
        return None
    
    # Sortera efter storlek
    sorted_data = sorted(zip(revenue_categories, revenue_totals), key=lambda x: x[1], reverse=True)
    revenue_categories, revenue_totals = zip(*sorted_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=revenue_categories,
        x=revenue_totals,
        orientation='h',
        marker_color='#28a745',
        hovertemplate='<b>%{y}</b><br>Intäkt: %{x:,.1f} tSEK<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Intäktskategorier', font=dict(size=18, color='#1f4e79')),
        xaxis_title='Belopp (tSEK)',
        yaxis_title='Kategori',
        template='plotly_white',
        height=400,
        margin=dict(l=150)
    )
    
    return fig

def create_expense_detail_chart(analyzer, sheet_name):
    """Skapar detaljerat diagram för kostnadskategorier"""
    import plotly.graph_objects as go
    
    raw_data = analyzer.get_raw_data(sheet_name)
    if raw_data is None:
        return None
    
    # Hitta kostnadskategorier (rader som inte är SUMMA och har negativa värden)
    expense_categories = []
    expense_totals = []
    
    # Hitta SUMMA-kolumnen
    summa_col_idx = len(raw_data.columns) - 1
    
    # Efter SUMMA RÖRELSENS INTÄKTER och innan BERÄKNAT RESULTAT = kostnader
    found_revenue_summa = False
    found_result = False
    
    for idx, row in raw_data.iterrows():
        category = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
        
        # Kolla om vi hittat intäktsraden (flexibel matchning)
        if any(keyword in category.upper() for keyword in ['SUMMA RÖRELSENS INTÄKTER', 'SUMMA NETTOOMSÄTTNING']):
            found_revenue_summa = True
            continue
        
        # Kolla om vi hittat BERÄKNAT RESULTAT (slutar kostnader)
        if 'BERÄKNAT RESULTAT' in category.upper():
            found_result = True
            continue
            
        # Skippa SUMMA-rader och tomma kategorier
        if 'SUMMA' in category.upper() or category.strip() == "":
            continue
        
        # Läs värdet från SUMMA-kolumnen
        total_val = convert_excel_value(row.iloc[summa_col_idx])
        
        # Bara kostnader (efter SUMMA RÖRELSENS INTÄKTER och innan BERÄKNAT RESULTAT)
        if found_revenue_summa and not found_result and abs(total_val) > 10:  # Bara kategorier över 10 tSEK
            # Rensa och förkorta kategorinamnet
            clean_category = category.strip()[:40]  # Lite längre för bättre läsbarhet
            expense_categories.append(clean_category)
            expense_totals.append(abs(total_val))  # Visa som positiva värden för bättre visualisering
    
    if not expense_categories:
        return None
    
    # Sortera efter storlek
    sorted_data = sorted(zip(expense_categories, expense_totals), key=lambda x: x[1], reverse=True)
    expense_categories, expense_totals = zip(*sorted_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=expense_categories,
        x=expense_totals,
        orientation='h',
        marker_color='#dc3545',
        hovertemplate='<b>%{y}</b><br>Kostnad: %{x:,.1f} tSEK<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Kostnadskategorier', font=dict(size=18, color='#1f4e79')),
        xaxis_title='Belopp (tSEK)',
        yaxis_title='Kategori',
        template='plotly_white',
        height=400,
        margin=dict(l=150)
    )
    
    return fig

def create_category_pie_chart(analyzer, sheet_name):
    """Skapar cirkeldiagram för kategorier"""
    raw_data = analyzer.get_raw_data(sheet_name)
    if raw_data is None:
        return None
    
    categories = []
    values = []
    
    revenue_keywords = ['Nettoomsättning', 'Försäljning', 'Membership', 'Intäkter']
    
    for idx, row in raw_data.iterrows():
        if idx == 0:
            continue
            
        category = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
        
        # Hitta Total-kolumn
        total_value = 0
        for col_idx, col_name in enumerate(raw_data.columns):
            if 'total' in str(col_name).lower():
                total_value = convert_excel_value(row.iloc[col_idx])
                break
        
        # Bara visa intäktskategorier med värde > 0
        is_revenue = any(keyword.lower() in category.lower() for keyword in revenue_keywords)
        if is_revenue and total_value > 0:
            categories.append(category)
            values.append(total_value)
    
    if not categories:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        textposition='outside',
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title=dict(text='Intäktsfördelning per Kategori', font=dict(size=20, color='#1f4e79')),
        height=500,
        showlegend=True
    )
    
    return fig

def create_heatmap(monthly_revenue, monthly_expenses):
    """Skapar heatmap för aktivitet"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    
    # Skapa data för heatmap
    data = [
        monthly_revenue,
        monthly_expenses,
        [rev - exp for rev, exp in zip(monthly_revenue, monthly_expenses)]
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=months,
        y=['Intäkter', 'Kostnader', 'Nettoresultat'],
        colorscale='RdYlGn',
        text=[[f'{val:,.0f}' for val in row] for row in data],
        texttemplate='%{text} SEK',
        textfont={"size": 12},
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:,.0f} SEK<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Finansiell Aktivitetsheatmap', font=dict(size=20, color='#1f4e79')),
        height=400
    )
    
    return fig

def display_kpi_cards(analyzer, sheet_name):
    """Visar KPI-kort - läser direkt från Excel's SUMMA-kolumn"""
    # Läs DIREKT från Excel's SUMMA-kolumn
    total_revenue, total_expenses, net_result = get_yearly_totals_from_excel(analyzer, sheet_name)
    
    if total_revenue is None:
        total_revenue, total_expenses, net_result = 0, 0, 0
    
    profit_margin = (net_result / total_revenue * 100) if total_revenue > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_revenue:,.1f} tSEK</div>
            <div class="metric-label">Totala Intäkter</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_expenses:,.1f} tSEK</div>
            <div class="metric-label">Totala Kostnader</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = "#28a745" if net_result >= 0 else "#dc3545"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {color}">{net_result:,.1f} tSEK</div>
            <div class="metric-label">Nettoresultat</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{profit_margin:.1f}%</div>
            <div class="metric-label">Vinstmarginal</div>
        </div>
        """, unsafe_allow_html=True)

def display_raw_data_editor(analyzer, sheet_name):
    """Visar rådata från Excel med redigeringsmöjligheter"""
    st.markdown('<div class="section-header">📊 Rådata Viewer & Editor</div>', unsafe_allow_html=True)
    
    raw_data = analyzer.get_raw_data(sheet_name)
    if raw_data is None:
        st.error("❌ Kunde inte ladda rådata för vald analys.")
        return
    
    st.markdown(f"**Visar data för:** {sheet_name}")
    
    # Skapa en kopia av data för redigering
    if f'edited_data_{sheet_name}' not in st.session_state:
        st.session_state[f'edited_data_{sheet_name}'] = raw_data.copy()
        # Lägg till kolumner för redigering
        st.session_state[f'edited_data_{sheet_name}']['Typ'] = 'Auto'
        st.session_state[f'edited_data_{sheet_name}']['Exkludera'] = False
        
        # Automatisk kategorisering baserat på Excel-struktur
        auto_categorize_rows(st.session_state[f'edited_data_{sheet_name}'])
    
    edited_data = st.session_state[f'edited_data_{sheet_name}']
    
    # Filter och kontroller
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        show_all = st.checkbox("Visa alla rader", value=True, key=f"show_all_{sheet_name}")
        
    with col2:
        filter_type = st.selectbox(
            "Filtrera efter typ:",
            ["Alla", "Intäkt", "Kostnad", "Exkluderade"],
            key=f"filter_type_{sheet_name}"
        )
    
    with col3:
        if st.button("🔄 Återställ ändringar", key=f"reset_{sheet_name}"):
            st.session_state[f'edited_data_{sheet_name}'] = raw_data.copy()
            st.session_state[f'edited_data_{sheet_name}']['Typ'] = 'Auto'
            st.session_state[f'edited_data_{sheet_name}']['Exkludera'] = False
            # Automatisk kategorisering baserat på Excel-struktur
            auto_categorize_rows(st.session_state[f'edited_data_{sheet_name}'])
            st.rerun()
    
    # Filtrera data baserat på val
    display_data = edited_data.copy()
    
    if not show_all:
        # Visa endast rader med numeriska värden i månaderna
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
        mask = False
        for month in months:
            if month in display_data.columns:
                mask |= (pd.to_numeric(display_data[month], errors='coerce').fillna(0) != 0)
        display_data = display_data[mask]
    
    if filter_type == "Intäkt":
        display_data = display_data[display_data['Typ'] == 'Intäkt']
    elif filter_type == "Kostnad":
        display_data = display_data[display_data['Typ'] == 'Kostnad']
    elif filter_type == "Exkluderade":
        display_data = display_data[display_data['Exkludera'] == True]
    
    st.markdown(f"**Visar {len(display_data)} av {len(edited_data)} rader**")
    
    # Visa data med redigeringsmöjligheter
    if len(display_data) > 0:
        # Konfigurera kolumner för data editor
        column_config = {}
        
        # Konfigurera Typ-kolumnen
        column_config["Typ"] = st.column_config.SelectboxColumn(
            "Typ",
            help="Ändra om posten är intäkt eller kostnad",
            options=["Auto", "Intäkt", "Kostnad"],
            required=True,
        )
        
        # Konfigurera Exkludera-kolumnen
        column_config["Exkludera"] = st.column_config.CheckboxColumn(
            "Exkludera",
            help="Markera för att exkludera från beräkningar",
            default=False,
        )
        
        # Konfigurera numeriska kolumner - visa som text för att bevara exakt Excel-format
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec', 'Totalt']
        for month in months:
            if month in display_data.columns:
                column_config[month] = st.column_config.TextColumn(
                    month,
                    help=f"Värde för {month} (exakt som i Excel)",
                )
        
        # Data editor
        edited_df = st.data_editor(
            display_data,
            column_config=column_config,
            use_container_width=True,
            num_rows="dynamic",
            disabled=["Kategori"] if "Kategori" in display_data.columns else [],
            key=f"data_editor_{sheet_name}"
        )
        
        # Uppdatera session state med ändringar
        for idx in edited_df.index:
            if idx in st.session_state[f'edited_data_{sheet_name}'].index:
                st.session_state[f'edited_data_{sheet_name}'].loc[idx] = edited_df.loc[idx]
        
        # Visa sammanfattning av ändringar
        st.markdown('<div class="section-header">📋 Ändringar Sammanfattning</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            intakt_count = len(edited_df[edited_df['Typ'] == 'Intäkt'])
            st.metric("Markerade som Intäkt", intakt_count)
        
        with col2:
            kostnad_count = len(edited_df[edited_df['Typ'] == 'Kostnad'])
            st.metric("Markerade som Kostnad", kostnad_count)
        
        with col3:
            excluded_count = len(edited_df[edited_df['Exkludera'] == True])
            st.metric("Exkluderade", excluded_count)
        
        # Export funktionalitet
        if st.button("💾 Exportera ändringar", key=f"export_{sheet_name}"):
            # Här kan vi lägga till export-funktionalitet i framtiden
            st.success("✅ Export-funktionalitet kommer snart!")
    
    else:
        st.info("Inga rader att visa med aktuella filter.")

def auto_categorize_rows(data):
    """Automatisk kategorisering av rader baserat på Excel-struktur"""
    found_revenue_summa = False
    found_result = False
    
    for idx, row in data.iterrows():
        category = str(row.iloc[0]) if not pd.isna(row.iloc[0]) else ""
        
        # Kolla om vi hittat intäktsraden (flexibel matchning)
        if any(keyword in category.upper() for keyword in ['SUMMA RÖRELSENS INTÄKTER', 'SUMMA NETTOOMSÄTTNING']):
            found_revenue_summa = True
            data.loc[idx, 'Typ'] = 'Auto'
            continue
        
        # Kolla om vi hittat BERÄKNAT RESULTAT (slutar kostnader)
        if 'BERÄKNAT RESULTAT' in category.upper():
            found_result = True
            data.loc[idx, 'Typ'] = 'Auto'
            continue
        
        # Skippa SUMMA-rader och tomma kategorier
        if 'SUMMA' in category.upper() or category.strip() == "":
            data.loc[idx, 'Typ'] = 'Auto'
            continue
        
        # Automatisk kategorisering
        if not found_revenue_summa:
            # Innan intäktsumman = intäkter
            data.loc[idx, 'Typ'] = 'Intäkt'
        elif found_revenue_summa and not found_result:
            # Efter intäktsumman och innan resultat = kostnader
            data.loc[idx, 'Typ'] = 'Kostnad'
        else:
            # Efter resultat
            data.loc[idx, 'Typ'] = 'Auto'

def get_editable_data_summary(analyzer, sheet_name):
    """Hämtar sammanfattning av redigerad data"""
    if f'edited_data_{sheet_name}' not in st.session_state:
        return None
    
    edited_data = st.session_state[f'edited_data_{sheet_name}']
    
    # Filtrera bort exkluderade rader
    active_data = edited_data[edited_data['Exkludera'] == False]
    
    # Räkna intäkter och kostnader baserat på användarens markeringar
    revenue_data = active_data[active_data['Typ'] == 'Intäkt']
    expense_data = active_data[active_data['Typ'] == 'Kostnad']
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    
    monthly_revenue = []
    monthly_expenses = []
    
    for month in months:
        if month in active_data.columns:
            # Summera intäkter
            month_revenue = revenue_data[month].apply(convert_excel_value).sum()
            monthly_revenue.append(abs(month_revenue))
            
            # Summera kostnader
            month_expense = expense_data[month].apply(convert_excel_value).sum()
            monthly_expenses.append(month_expense)
        else:
            monthly_revenue.append(0)
            monthly_expenses.append(0)
    
    return monthly_revenue, monthly_expenses

def main():
    """Huvudfunktion för business dashboard"""
    
    # Kontrollera autentisering
    if not check_password():
        return
    
    # Header
    st.markdown('<div class="main-header">📊 Finansiell Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f"**Välkommen, {st.session_state.get('authenticated_username', 'Admin')}!** 👋")
    
    # Ladda data
    with st.spinner("Laddar finansiell data..."):
        analyzer = load_financial_data()
    
    if not analyzer:
        st.error("❌ Kunde inte ladda finansiell data.")
        return
    
    # Sidebar
    st.sidebar.markdown("## 🧭 Navigation")
    st.sidebar.markdown("### 📈 Välj Analystyp")
    
    # Analys typ
    analysis_type = st.sidebar.radio(
        "Välj analystyp:",
        ["Enskilt företag", "Jämför företag", "Alla företag", "Rådata & Redigering"]
    )
    
    if analysis_type == "Enskilt företag":
        selected_sheet = st.sidebar.selectbox(
            "Välj analys:",
            analyzer.available_sheets,
            help="Välj vilket företag och år du vill analysera"
        )
        selected_sheets = [selected_sheet]
        
    elif analysis_type == "Jämför företag":
        st.sidebar.markdown("**Välj företag och år att jämföra:**")
        selected_sheets = []
        
        # Skapa checkboxes för varje företag/år
        for sheet in analyzer.available_sheets:
            if st.sidebar.checkbox(sheet, key=f"compare_{sheet}"):
                selected_sheets.append(sheet)
        
        if len(selected_sheets) < 2:
            st.sidebar.warning("⚠️ Välj minst 2 företag/år för jämförelse")
            selected_sheets = []
    
    elif analysis_type == "Rådata & Redigering":
        selected_sheet = st.sidebar.selectbox(
            "Välj företag/år för redigering:",
            analyzer.available_sheets,
            help="Välj vilket företag och år du vill se och redigera rådata för"
        )
        selected_sheets = [selected_sheet]
            
    else:  # Alla företag
        selected_sheets = analyzer.available_sheets
        st.sidebar.info(f"📊 Visar alla {len(selected_sheets)} företag/år")
    
    # Kontrollera att vi har data att visa
    if not selected_sheets:
        st.info("👈 Välj företag och år i sidomenyn för att se analys")
        return
    
    # Hämta data för valt/valda företag
    if analysis_type == "Enskilt företag":
        monthly_revenue, monthly_expenses, monthly_net_result = get_monthly_data(analyzer, selected_sheets[0])
        
        if monthly_revenue is None:
            st.error("❌ Kunde inte hämta data för vald analys.")
            return
        
        # KPI Cards
        display_kpi_cards(analyzer, selected_sheets[0])
        
        # Diagram i kolumner
        st.markdown('<div class="section-header">📊 Finansiella Diagram</div>', unsafe_allow_html=True)
        
        # Linjediagram (full bredd)
        line_chart = create_monthly_line_chart(monthly_revenue, monthly_expenses, monthly_net_result)
        st.plotly_chart(line_chart, use_container_width=True)
        
        # Stapeldiagram för översikt
        bar_chart = create_monthly_bar_chart(monthly_revenue, monthly_expenses, monthly_net_result)
        st.plotly_chart(bar_chart, use_container_width=True)
        
        # Detaljerade intäkter och utgifter
        col1, col2 = st.columns(2)
        
        with col1:
            revenue_detail_chart = create_revenue_detail_chart(analyzer, selected_sheets[0])
            if revenue_detail_chart:
                st.plotly_chart(revenue_detail_chart, use_container_width=True)
        
        with col2:
            expense_detail_chart = create_expense_detail_chart(analyzer, selected_sheets[0])
            if expense_detail_chart:
                st.plotly_chart(expense_detail_chart, use_container_width=True)
        
        # Datatabell
        st.markdown('<div class="section-header">📋 Månadsdata</div>', unsafe_allow_html=True)
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
        
        # Säkerställ att alla listor har samma längd (12 månader)
        while len(monthly_revenue) < 12:
            monthly_revenue.append(0)
        while len(monthly_expenses) < 12:
            monthly_expenses.append(0)
        while len(monthly_net_result) < 12:
            monthly_net_result.append(0)
        
        # Trimma till 12 månader om de är längre
        monthly_revenue = monthly_revenue[:12]
        monthly_expenses = monthly_expenses[:12]
        monthly_net_result = monthly_net_result[:12]
        
        data_table = pd.DataFrame({
            'Månad': months,
            'Intäkter': [f"{val:,.1f} tSEK" for val in monthly_revenue],
            'Kostnader': [f"{val:,.1f} tSEK" for val in monthly_expenses],
            'Nettoresultat': [f"{net:,.1f} tSEK" for net in monthly_net_result]
        })
        
        st.dataframe(data_table, use_container_width=True)
    
    elif analysis_type == "Rådata & Redigering":
        # Rådata viewer och editor
        display_raw_data_editor(analyzer, selected_sheets[0])
        
        # Visa även uppdaterad analys baserat på ändringar
        if f'edited_data_{selected_sheets[0]}' in st.session_state:
            editable_summary = get_editable_data_summary(analyzer, selected_sheets[0])
            if editable_summary:
                monthly_revenue, monthly_expenses = editable_summary
                monthly_net_result = [rev + exp for rev, exp in zip(monthly_revenue, monthly_expenses)]  # exp är redan negativ
                
                st.markdown('<div class="section-header">📊 Uppdaterad Analys (Baserat på Dina Ändringar)</div>', unsafe_allow_html=True)
                
                # Visa uppdaterade diagram
                updated_line_chart = create_monthly_line_chart(monthly_revenue, monthly_expenses, monthly_net_result)
                st.plotly_chart(updated_line_chart, use_container_width=True)
                
                # Visa uppdaterad datatabell
                st.markdown('<div class="section-header">📋 Uppdaterad Månadsdata</div>', unsafe_allow_html=True)
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
                
                updated_data_table = pd.DataFrame({
                    'Månad': months,
                    'Intäkter': [f"{val:,.1f} tSEK" for val in monthly_revenue],
                    'Kostnader': [f"{val:,.1f} tSEK" for val in monthly_expenses],
                    'Nettoresultat': [f"{net:,.1f} tSEK" for net in monthly_net_result]
                })
                
                st.dataframe(updated_data_table, use_container_width=True)
    
    else:
        # Multi-företag analys
        st.markdown('<div class="section-header">📊 Jämförelse av Företag</div>', unsafe_allow_html=True)
        
        # Skapa jämförelsediagram
        comparison_chart = create_multi_company_comparison(analyzer, selected_sheets)
        if comparison_chart:
            st.plotly_chart(comparison_chart, use_container_width=True)
        
        # KPI sammanfattning för alla företag
        display_multi_company_kpis(analyzer, selected_sheets)
        
        # Diagram för multi-företag
        st.markdown('<div class="section-header">📊 Finansiella Diagram</div>', unsafe_allow_html=True)
        
        # Multi-företag stapeldiagram
        multi_bar_chart = create_multi_company_bar_chart(analyzer, selected_sheets)
        if multi_bar_chart:
            st.plotly_chart(multi_bar_chart, use_container_width=True)
        
        # Detaljerade kategorier - visa alla företag i kolumner
        st.markdown('<div class="section-header">🔍 Detaljerade Kategorier</div>', unsafe_allow_html=True)
        if len(selected_sheets) > 9:
            st.info(f"📊 Visar detaljerade kategorier för alla {len(selected_sheets)} företag/år. Scrolla ner för att se alla.")
        
        # Visa alla företag i grupper för bättre layout
        display_companies = selected_sheets  # Visa alla valda företag
        
        # Skapa kolumner för layout - max 3 per rad
        if len(display_companies) <= 3:
            cols = st.columns(len(display_companies))
            rows_needed = 1
        else:
            cols = st.columns(3)
            rows_needed = (len(display_companies) + 2) // 3  # Räkna ut antal rader
        
        for i, sheet in enumerate(display_companies):
            col_idx = i % len(cols)
            with cols[col_idx]:
                st.markdown(f"#### {sheet}")
                
                # Intäktskategorier
                revenue_chart = create_revenue_detail_chart(analyzer, sheet)
                if revenue_chart:
                    revenue_chart.update_layout(height=300, title=f"Intäkter")
                    st.plotly_chart(revenue_chart, use_container_width=True)
                
                # Kostnadskategorier  
                expense_chart = create_expense_detail_chart(analyzer, sheet)
                if expense_chart:
                    expense_chart.update_layout(height=300, title=f"Kostnader")
                    st.plotly_chart(expense_chart, use_container_width=True)
    
    # Logout knapp
    if st.sidebar.button("🚪 Logga ut"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
