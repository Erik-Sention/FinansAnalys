# 📊 Finansiell Dashboard - Projektspecifikation

## Översikt

Detta dokument beskriver hur man bygger ett finansiellt dashboard baserat på det befintliga medlemskapsanalyssystemet. Dashboarden ska analysera finansiell data från Excel-filer med flera flikar och presentera data via Streamlit med interaktiva diagram och djupgående analyser.

## 🎯 Projektmål

Skapa ett komplett finansiellt analysverktyg som:
- Automatiskt läser in Excel-filer med flera flikar (antal flikar bestäms av datafilen)
- Presenterar finansiell data genom interaktiva visualiseringar
- Möjliggör jämförelser mellan olika flikar/år/perioder
- Genererar automatiska insikter och trender
- Exporterar analyser till Excel

## 🏗️ Arkitektur

### Filstruktur
```
financial_dashboard/
├── dashboard.py              # Huvud-Streamlit applikation
├── streamlit_app.py         # Entry point för deployment
├── financial_analyzer.py    # Kärnanalysmotor
├── requirements.txt         # Python dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit konfiguration
│   └── secrets.toml         # Autentisering (ej i Git)
├── README.md               # Projektdokumentation
└── data.xlsx               # Finansiell data (auto-laddar)
```

### Huvudkomponenter

1. **financial_analyzer.py** - Kärnklassen som hanterar:
   - Datainläsning från Excel
   - Datarengöring och standardisering
   - Skapande av visualiseringar
   - Generering av insikter
   - Export av data

2. **dashboard.py** - Streamlit-applikationen som tillhandahåller:
   - Användarautentisering
   - UI för datavisning
   - Interaktiva kontroller
   - Flera analyslägen

## 📋 Dataformat och Struktur

### Excel-filens format
- **Filnamn**: Systemet letar automatiskt efter filer med namn som:
  - `data.xlsx`
  - `financial_data.xlsx`
  - `finances.xlsx`
  - `ekonomi.xlsx`

### Flikstruktur
Varje flik ska representera ett år eller en period:
- `Ekonomi 2019`
- `Ekonomi 2020`
- `Ekonomi 2021`
- `Ekonomi 2022`
- `Ekonomi 2023`
- ... (antal flikar bestäms av din Excel-fil)

### Kolumnstruktur per flik
```
Kategori          | Jan 2023 | Feb 2023 | Mar 2023 | ... | Dec 2023 | Totalt | Procent
------------------|----------|----------|----------|-----|----------|--------|--------
Intäkter          |    25000 |    27000 |    23000 | ... |    28000 |  320000|   45.2%
Kostnader         |   -15000 |   -16000 |   -14000 | ... |   -17000 | -195000|  -27.6%
Investeringar     |    -5000 |        0 |   -10000 | ... |        0 |  -45000|   -6.4%
```

**Kolumnkrav:**
- Första kolumnen: Finansiella kategorier (Intäkter, Kostnader, etc.)
- Månadskolumner: `Januari 2023`, `Februari 2023`, etc.
- Totalt-kolumn: Ignoreras av systemet (beräknas automatiskt)
- Procent-kolumn: Ignoreras av systemet

## 🔧 Teknisk Implementation

### Huvudklasser

#### FinancialAnalyzer
```python
class FinancialAnalyzer:
    def __init__(self, excel_file_path, data_type='financial'):
        """
        Initialiserar analysatorn med Excel-fil
        """
        
    def load_data(self):
        """Läser in alla flikar från Excel-filen"""
        
    def clean_and_standardize_data(self):
        """Rengör och standardiserar dataformatet"""
        
    def create_financial_trends_by_category(self, sheet_name):
        """Skapar linjediagram för månadsvis utveckling per kategori"""
        
    def create_category_distribution_chart(self, sheet_name):
        """Skapar cirkeldiagram för fördelning av kategorier"""
        
    def create_heatmap(self, sheet_name):
        """Skapar heatmap för aktivitet per kategori och månad"""
        
    def create_top_performers_chart(self, sheet_name):
        """Skapar stapeldiagram för bästa/sämsta kategorier"""
        
    def generate_insights(self, sheet_name):
        """Genererar automatiska finansiella insikter"""
        
    def create_year_comparison_summary(self):
        """Skapar jämförelse mellan alla år"""
```

### Nyckelmetoder för Visualisering

#### 1. Månadsvis Trendanalys
```python
def create_financial_trends_by_category(self, sheet_name):
    """
    Skapar interaktiva linjediagram som visar:
    - Utveckling av intäkter över månader
    - Kostnadstrender
    - Nettoresultat per månad
    - Separata linjer för varje finansiell kategori
    """
```

#### 2. Kategorifördelning
```python
def create_category_distribution_chart(self, sheet_name):
    """
    Visar procentuell fördelning av:
    - Intäkter per typ
    - Kostnader per kategori
    - Som cirkeldiagram eller stapeldiagram
    """
```

#### 3. Finansiell Heatmap
```python
def create_heatmap(self, sheet_name):
    """
    Visar intensitet av finansiell aktivitet:
    - Månader på x-axeln
    - Kategorier på y-axeln
    - Färgintensitet baserat på belopp
    """
```

#### 4. Prestationsanalys
```python
def create_top_performers_chart(self, sheet_name):
    """
    Identifierar och visar:
    - Mest lönsamma kategorier
    - Största kostnadsposter
    - Snabbast växande intäktskällor
    """
```

## 🖥️ Streamlit Dashboard Features

### Autentisering
```python
def check_password():
    """
    Säker inloggning med:
    - Användarnamn och lösenord
    - Session timeout (30 minuter)
    - Hashade lösenord
    - Automatisk utloggning
    """
```

### Analyslägen

#### 1. Enskild Årsanalys
- Djupdykning i ett specifikt år
- Alla standarddiagram och insikter
- Detaljerad månadsvis analys

#### 2. Två-års Jämförelse
- Sida-vid-sida jämförelse av 2 år
- Flexibla layoutalternativ (horisontell/vertikal)
- Head-to-head prestationsanalys
- Tillväxtanalys

#### 3. Flera-års Översikt
- Jämför alla tillgängliga år samtidigt
- Totala intäkter/kostnader ranking
- Månatlig prestationsöverlagring
- Tillväxtanalys över tid
- Sammanfattande statistiktabell

### UI-kontroller

#### Sidebar Navigation
```python
# År-väljare
selected_year = st.sidebar.selectbox(
    "Välj År att Analysera",
    available_years
)

# Analysläge
analysis_mode = st.sidebar.radio(
    "Välj Analystyp",
    ["Enskild Årsanalys", "Två-års Jämförelse", "Flera-års Översikt"]
)

# Kategorifilter
selected_categories = st.sidebar.multiselect(
    "Filtrera Finansiella Kategorier",
    all_categories,
    default=all_categories
)

# Visualiseringsalternativ
show_trends = st.sidebar.checkbox("Månadsvis Utveckling", True)
show_distribution = st.sidebar.checkbox("Kategorifördelning", True)
show_heatmap = st.sidebar.checkbox("Aktivitetsheatmap", True)
show_insights = st.sidebar.checkbox("Automatiska Insikter", True)
```

## 📊 Automatiska Insikter

Systemet ska generera följande typer av insikter:

### Grundläggande Statistik
```python
insights = [
    f"💰 Totala intäkter: {total_revenue:,.0f} SEK",
    f"💸 Totala kostnader: {total_costs:,.0f} SEK", 
    f"📈 Nettoresultat: {net_result:,.0f} SEK",
    f"📊 Vinstmarginal: {profit_margin:.1f}%"
]
```

### Trendanalys
```python
# Tillväxtanalys
growth_insights = [
    f"📈 Bästa intäktsmånad: {best_month} ({best_amount:,.0f} SEK)",
    f"📉 Sämsta månad: {worst_month} ({worst_amount:,.0f} SEK)",
    f"🔄 Tillväxttrend: {growth_trend:.1f}% (första vs andra halvåret)"
]
```

### Kategorianalys
```python
category_insights = [
    f"🏆 Största intäktskälla: {top_revenue_category} ({amount:,.0f} SEK)",
    f"⚠️ Största kostnadspost: {top_cost_category} ({amount:,.0f} SEK)",
    f"🎯 Mest volatila kategori: {most_volatile_category}"
]
```

### Jämförelseanalys (för flera år)
```python
comparison_insights = [
    f"🏅 Bästa år: {best_year} ({best_result:,.0f} SEK nettoresultat)",
    f"📊 Genomsnittlig årlig tillväxt: {avg_growth:.1f}%",
    f"📈 Mest förbättrade kategori: {improved_category} (+{improvement:.1f}%)",
    f"📉 Mest försämrade kategori: {declined_category} (-{decline:.1f}%)"
]
```

## 🎨 Visualiseringsdetaljer

### Färgscheman
```python
# Finansiella färger
REVENUE_COLOR = '#2E8B57'    # Grön för intäkter
COST_COLOR = '#DC143C'       # Röd för kostnader  
PROFIT_COLOR = '#4169E1'     # Blå för vinst
NEUTRAL_COLOR = '#708090'    # Grå för neutralt

# Plotly färgpaletter
color_sequences = {
    'categorical': px.colors.qualitative.Set3,
    'sequential': px.colors.sequential.Blues,
    'diverging': px.colors.diverging.RdYlGn
}
```

### Diagramkonfiguration
```python
# Standardkonfiguration för alla diagram
chart_config = {
    'height': 600,
    'template': 'plotly_white',
    'font_family': 'Arial',
    'title_font_size': 16,
    'margin': dict(t=80, b=80, l=60, r=60)
}
```

## 🔒 Säkerhet och Deployment

### Lokala Secrets
```toml
# .streamlit/secrets.toml
[auth]
username = "Admin"
password = "DittSäkraLösenord123!"

[financial]
currency = "SEK"
company_name = "Ditt Företag AB"
```

### Deployment på Streamlit Cloud
1. Pusha kod till GitHub (secrets.toml ignoreras automatiskt)
2. Koppla repository på share.streamlit.io
3. Konfigurera secrets i Streamlit Cloud interface
4. Deploy med `streamlit_app.py` som main file

### Environment Variables
```python
# För produktion
STREAMLIT_AUTH_USERNAME = os.getenv('STREAMLIT_AUTH_USERNAME', 'admin')
STREAMLIT_AUTH_PASSWORD = os.getenv('STREAMLIT_AUTH_PASSWORD')
CURRENCY = os.getenv('CURRENCY', 'SEK')
```

## 📱 Responsiv Design

### CSS Customization
```python
st.markdown("""
<style>
    .financial-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
    }
    .profit-metric {
        background: linear-gradient(90deg, #2E8B57, #32CD32);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .loss-metric {
        background: linear-gradient(90deg, #DC143C, #FF6347);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .insight-box {
        background-color: #F0F8FF;
        border-left: 4px solid #4169E1;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)
```

## 📤 Export och Rapporter

### Excel Export
```python
def export_financial_summary(self, output_file='financial_analysis.xlsx'):
    """
    Exporterar:
    - Rådata från alla år
    - Sammanfattande statistik
    - Jämförelsetabeller
    - Automatiska insikter
    """
```

### PDF Rapporter (framtida utbyggnad)
```python
def generate_pdf_report(self, year=None):
    """
    Genererar PDF-rapport med:
    - Executive summary
    - Nyckeldiagram
    - Insikter och rekommendationer
    """
```

## 🚀 Utvecklingsprocess

### 1. Sätta upp projektet
```bash
# Skapa projektmapp
mkdir financial_dashboard
cd financial_dashboard

# Installera dependencies
pip install streamlit pandas plotly openpyxl numpy

# Skapa filstruktur
touch dashboard.py financial_analyzer.py streamlit_app.py
mkdir .streamlit
touch .streamlit/config.toml .streamlit/secrets.toml
```

### 2. Utvecklingsordning
1. **financial_analyzer.py** - Börja med datainläsning och grundläggande analys
2. **Basic visualizations** - Implementera core charts
3. **dashboard.py** - Bygg Streamlit UI steg för steg
4. **Authentication** - Lägg till säkerhet
5. **Advanced features** - Jämförelser och export
6. **Polish** - CSS styling och responsive design

### 3. Testing och Validering
```python
# Test med sample data
sample_data = {
    'Kategori': ['Intäkter', 'Kostnader', 'Investeringar'],
    'Januari 2023': [100000, -50000, -10000],
    'Februari 2023': [120000, -55000, -5000],
    # ... fortsätt för alla månader
}
```

## 📈 Funktionalitetschecklista

### Grundfunktioner ✅
- [ ] Excel-inläsning med dynamiskt antal flikar
- [ ] Datarengöring och validering
- [ ] Månadsvis trendvisualisering
- [ ] Kategorifördelningsdiagram
- [ ] Finansiell heatmap
- [ ] Automatiska insikter

### Jämförelsefunktioner ✅
- [ ] Två-års jämförelse med flexibel layout
- [ ] Flera-års översikt
- [ ] Tillväxtanalys
- [ ] Prestationsgaps
- [ ] Year-over-year trender

### UI/UX ✅
- [ ] Responsiv design
- [ ] Svensk översättning
- [ ] Intuitive navigation
- [ ] Professional styling
- [ ] Error handling

### Säkerhet ✅
- [ ] Användarautentisering
- [ ] Session management
- [ ] Säker secrets hantering
- [ ] Input validation

### Export/Rapporter ✅
- [ ] Excel export
- [ ] Sammanfattande rapporter
- [ ] Datanedladdning
- [ ] Delningsfunktioner

## 🎯 Slutresultat

När projektet är klart ska du ha:

1. **Ett komplett finansiellt dashboard** som automatiskt läser din Excel-fil
2. **Interaktiva visualiseringar** som visar finansiella trender och mönster
3. **Automatiska insikter** som hjälper dig förstå din finansiella prestanda
4. **Jämförelsemöjligheter** mellan olika år och perioder
5. **Professionell presentation** av finansiell data
6. **Export-funktionalitet** för rapporter och analyser

Dashboarden kommer att vara helt anpassad till dina behov och automatiskt hantera det antal flikar du har i din Excel-fil, från 19 till vilket antal som helst.

---

*Denna specifikation ger dig allt du behöver för att bygga ett kraftfullt finansiellt analysverktyg baserat på den beprövade arkitekturen från medlemskapsanalyssystemet.*
