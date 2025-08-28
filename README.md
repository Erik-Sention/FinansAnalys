# 📊 Finansiell Dashboard

Ett kraftfullt finansiellt analysverktyg byggt med Streamlit som automatiskt läser Excel-filer och skapar interaktiva visualiseringar och insikter.

## 🚀 Funktioner

- **Automatisk Excel-inläsning**: Läser in finansiell data från flera flikar
- **Interaktiva visualiseringar**: Trendanalyser, cirkeldiagram, heatmaps och prestationsdiagram
- **Automatiska insikter**: AI-genererade finansiella analysresultat
- **Jämförelsefunktioner**: Jämför mellan olika år och perioder
- **Säker autentisering**: Lösenordsskyddad åtkomst
- **Export till Excel**: Spara analyser och rapporter
- **Responsiv design**: Fungerar på alla enheter

## 📋 Krav

```bash
streamlit==1.28.1
pandas==2.0.3
plotly==5.17.0
openpyxl==3.1.2
numpy==1.24.3
```

## 🛠️ Installation

1. **Klona eller ladda ner projektet**
```bash
cd FinansAnalys
```

2. **Installera dependencies**
```bash
pip install -r requirements.txt
```

3. **Förbered din Excel-fil**
   - Placera din Excel-fil i projektmappen
   - Accepterade filnamn: `Finansiell Data.xlsx`, `data.xlsx`, `financial_data.xlsx`, `finances.xlsx`, `ekonomi.xlsx`
   - Varje flik ska representera ett år (t.ex. "Ekonomi 2022", "Ekonomi 2023")

## 🏃‍♂️ Köra Applikationen

```bash
streamlit run streamlit_app.py
```

Eller direkt:
```bash
streamlit run dashboard.py
```

Applikationen öppnas automatiskt i din webbläsare på `http://localhost:8501`

## 🔐 Inloggning

**Standard inloggningsuppgifter:**
- Användarnamn: `admin`
- Lösenord: `FinansAnalys2024!`

För att ändra inloggningsuppgifter, redigera `.streamlit/secrets.toml`

## 📊 Dataformat

### Excel-filstruktur
Din Excel-fil ska ha följande struktur:

**Flikar:** Varje flik representerar ett år
- `Ekonomi 2019`
- `Ekonomi 2020`
- `Ekonomi 2021`
- osv...

**Kolumner per flik:**
```
Kategori          | Jan 2023 | Feb 2023 | Mar 2023 | ... | Dec 2023 | Totalt | Procent
------------------|----------|----------|----------|-----|----------|--------|--------
Intäkter          |    25000 |    27000 |    23000 | ... |    28000 |  320000|   45.2%
Kostnader         |   -15000 |   -16000 |   -14000 | ... |   -17000 | -195000|  -27.6%
Investeringar     |    -5000 |        0 |   -10000 | ... |        0 |  -45000|   -6.4%
```

**Viktigt:**
- Första kolumnen: Finansiella kategorier
- Månadskolumner: `Januari 2023`, `Februari 2023`, etc.
- Totalt och Procent kolumner ignoreras (beräknas automatiskt)

## 🎯 Analyslägen

### 1. Enskild Årsanalys
- Djupgående analys av ett specifikt år
- Månadsvis trendanalys
- Kategorifördelning
- Aktivitetsheatmap
- Prestationsanalys
- Automatiska insikter

### 2. Två-års Jämförelse
- Sida-vid-sida jämförelse
- Flexibla layoutalternativ
- Prestationsjämförelse
- Tillväxtanalys

### 3. Flera-års Översikt
- Jämför alla tillgängliga år
- Totala intäkter/kostnader ranking
- Långsiktig trendanalys
- Sammanfattande statistik

## 📱 Responsiv Design

Dashboarden är optimerad för:
- Desktop (full funktionalitet)
- Tablets (anpassad layout)
- Mobila enheter (förenklad vy)

## 🔒 Säkerhet

- Hashade lösenord
- Session timeout (30 minuter)
- Automatisk utloggning
- Säker secrets hantering

## 📤 Export

- **Excel-export**: Kompletta analyser med rådata
- **Sammanfattande rapporter**: Nyckelinsikter för alla år
- **Datanedladdning**: Processad data för extern analys

## 🛠️ Teknisk Arkitektur

```
financial_dashboard/
├── dashboard.py              # Huvud-Streamlit applikation
├── streamlit_app.py         # Entry point för deployment
├── financial_analyzer.py    # Kärnanalysmotor
├── requirements.txt         # Python dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit konfiguration
│   └── secrets.toml         # Autentisering
├── README.md               # Denna fil
└── Finansiell Data.xlsx    # Din finansiella data
```

## 🚀 Deployment

### Streamlit Cloud
1. Pusha kod till GitHub
2. Koppla repository på share.streamlit.io
3. Konfigurera secrets i Streamlit Cloud interface
4. Deploy med `streamlit_app.py` som main file

### Lokal deployment
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🎨 Anpassning

### Färgschema
Redigera `dashboard.py` för att ändra färger:
```python
self.colors = {
    'revenue': '#2E8B57',    # Grön för intäkter
    'cost': '#DC143C',       # Röd för kostnader  
    'profit': '#4169E1',     # Blå för vinst
    'neutral': '#708090'     # Grå för neutralt
}
```

### Språk
Alla texter är på svenska. För att ändra språk, redigera strängarna i `dashboard.py` och `financial_analyzer.py`.

## 🐛 Felsökning

### Vanliga problem:

1. **"Excel-fil hittades inte"**
   - Kontrollera att Excel-filen finns i projektmappen
   - Kontrollera filnamnet (se accepterade namn ovan)

2. **"Inga giltiga flikar hittades"**
   - Kontrollera att flikarna har rätt format
   - Se till att data finns i flikarna

3. **Visualiseringar visas inte**
   - Kontrollera att månadskolumner har rätt format
   - Se till att data är numerisk

4. **Inloggning fungerar inte**
   - Kontrollera `.streamlit/secrets.toml`
   - Använd standard: admin/FinansAnalys2024!

## 📞 Support

För support och frågor, kontakta utvecklaren eller skapa en issue i projektet.

## 📄 Licens

Detta projekt är skapat för intern användning. Alla rättigheter förbehålls.

---

**Byggd med ❤️ för finansiell analys**
