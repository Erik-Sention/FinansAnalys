#!/bin/bash

# Finansiell Dashboard - Snabbstart
echo "🚀 Startar Finansiell Dashboard..."
echo "📊 Detta kan ta några sekunder..."
echo ""

# Kontrollera att vi är i rätt katalog
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Fel: streamlit_app.py hittades inte!"
    echo "Kör detta script från FinansAnalys-mappen"
    exit 1
fi

# Kontrollera Excel-fil
if [ ! -f "Finansiell Data.xlsx" ]; then
    echo "⚠️ Varning: Finansiell Data.xlsx hittades inte!"
    echo "Se till att din Excel-fil finns i denna mapp"
fi

echo "✅ Startar dashboard på http://localhost:8501"
echo "💡 Logga in med: användarnamn='admin', lösenord='FinansAnalys2024!'"
echo ""
echo "🛑 Tryck Ctrl+C för att stoppa servern"
echo ""

# Starta Streamlit med python3
python3 -m streamlit run streamlit_app.py
