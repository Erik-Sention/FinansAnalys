# 🤖 AI-Assistent Integration för Finansiellt Dashboard

## Översikt
Integrera en intelligent AI-assistent som kan svara på frågor om finansiell data och grafer i realtid. Assistenten analyserar både rådata från Excel och visuella diagram för att ge kontextuella svar med OpenAI API.

## 🎯 AI-Assistent Funktioner

### Frågetyper som AI:n kan hantera

**Dataanalys Frågor:**
- "Vad var den totala vinsten 2023?"
- "Vilken månad hade högst intäkter?"
- "Hur mycket ökade kostnaderna från 2022 till 2023?"
- "Vilka kategorier presterar bäst?"

**Trendanalys:**
- "Ser du någon säsongsvariation i intäkterna?"
- "Finns det en uppgående trend i vinsterna?"
- "Vilka månader har historiskt bäst resultat?"

**Jämförelsefrågor:**
- "Hur skiljer sig 2023 från 2022?"
- "Vilka kategorier växer snabbast?"
- "Vilken period hade bäst lönsamhet?"

**Grafanalys:**
- "Vad visar heatmapen?"
- "Förklara trenden i linjediagrammet"
- "Vad betyder färgerna i cirkeldiagrammet?"

## 🔧 Teknisk Implementation

### 1. AI Service Klass
```python
import openai
import base64
import json
from io import BytesIO
import plotly.io as pio
import pandas as pd

class FinancialAIAssistant:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.system_prompt = """
        Du är en expert finansanalytiker som hjälper användare att förstå deras finansiella data.
        Du har tillgång till Excel-data och grafer från ett finansiellt dashboard.
        
        Svara alltid på svenska och var konkret och hjälpsam.
        När du analyserar data, fokusera på:
        - Trender och mönster
        - Viktiga insikter
        - Praktiska rekommendationer
        - Förklaringar av graferna
        
        Använd svenska valutan (SEK) och svenska datumformat.
        Var specifik med siffror och hänvisa till konkreta data.
        """
    
    def prepare_data_summary(self, analyzer, sheet_name):
        """
        Förbereder en sammanfattning av data för AI-kontexten
        """
        if sheet_name not in analyzer.data:
            return None
            
        df = analyzer.data[sheet_name]
        
        # Skapa datasammanfattning
        summary = {
            "år": sheet_name,
            "kategorier": df.iloc[:, 0].tolist(),
            "månatlig_data": {},
            "totaler": {},
            "insikter": analyzer.generate_insights(sheet_name)
        }
        
        # Lägg till månadsdata
        month_columns = [col for col in df.columns if any(month in str(col).lower() 
                        for month in ['januari', 'februari', 'mars', 'april', 'maj', 'juni',
                                     'juli', 'augusti', 'september', 'oktober', 'november', 'december'])]
        
        for month in month_columns:
            month_name = month.replace(' 2023', '').replace(' 2024', '').replace(' 2025', '')
            summary["månatlig_data"][month_name] = df[month].tolist()
        
        # Beräkna totaler per kategori
        for idx, row in df.iterrows():
            kategori = row.iloc[0]
            total = sum(pd.to_numeric(row[col], errors='coerce') or 0 for col in month_columns)
            summary["totaler"][kategori] = total
            
        return summary
    
    def encode_chart_image(self, fig):
        """
        Konverterar Plotly-diagram till base64 för AI-analys
        """
        try:
            img_bytes = pio.to_image(fig, format="png", width=800, height=600)
            img_base64 = base64.b64encode(img_bytes).decode()
            return img_base64
        except Exception as e:
            print(f"Fel vid bildkonvertering: {e}")
            return None
    
    def answer_question(self, question, data_summary, chart_images=None):
        """
        Svarar på användarfrågor med OpenAI API
        """
        # Bygg meddelanden för API
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                        Finansiell data: {json.dumps(data_summary, ensure_ascii=False, indent=2)}
                        
                        Användarfråga: {question}
                        
                        Analysera data och svara på frågan på svenska. Var specifik och använd siffror från datan.
                        Om grafer är inkluderade, analysera även dem i ditt svar.
                        """
                    }
                ]
            }
        ]
        
        # Lägg till bilder om tillgängliga
        if chart_images:
            for chart_name, img_base64 in chart_images.items():
                if img_base64:
                    messages[-1]["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}",
                            "detail": "high"
                        }
                    })
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Bästa modellen för bildanalys
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Fel vid AI-analys: {str(e)}"
    
    def get_suggested_questions(self, data_summary):
        """
        Genererar föreslagna frågor baserat på datan
        """
        categories = list(data_summary.get("totaler", {}).keys())
        år = data_summary.get("år", "")
        
        suggestions = [
            f"Vad var det totala resultatet för {år}?",
            f"Vilken kategori hade störst påverkan på resultatet?",
            f"Finns det några trender jag bör vara medveten om?",
            f"Hur presterade {categories[0] if categories else 'intäkterna'} under året?",
            "Vilka månader var starkast/svagast?",
            "Vad rekommenderar du för förbättringar?",
            "Förklara trenden i det senaste diagrammet",
            "Vilka risker ser du i datan?",
            "Hur kan jag förbättra lönsamheten?",
            "Vad visar heatmapen om säsongsmönster?"
        ]
        
        return suggestions

    def generate_strategic_analysis(self, analyzer, selected_years=None):
        """
        Genererar djupgående strategisk analys
        """
        if selected_years:
            combined_data = {}
            for year in selected_years:
                if year in analyzer.data:
                    combined_data[year] = self.prepare_data_summary(analyzer, year)
        else:
            # Använd alla tillgängliga år
            combined_data = {
                year: self.prepare_data_summary(analyzer, year) 
                for year in analyzer.get_available_sheets()
            }
        
        prompt = f"""
        Genomför en strategisk finansiell analys baserat på flera års data:
        
        {json.dumps(combined_data, ensure_ascii=False, indent=2)}
        
        Leverera en omfattande analys som inkluderar:
        1. Övergripande finansiell hälsa
        2. Trender över tid
        3. Tillväxtmönster
        4. Riskområden
        5. Möjligheter för förbättring
        6. Konkreta rekommendationer
        
        Var detaljerad och använd specifika siffror från datan.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Fel vid strategisk analys: {str(e)}"
```

### 2. Streamlit Integration

```python
# Lägg till i dashboard.py

def display_ai_assistant(analyzer, sheet_name):
    """
    Visar AI-assistentens gränssnitt
    """
    st.header("🤖 AI Finansanalytiker")
    st.markdown("*Ställ frågor om dina finanser och få intelligenta svar baserat på data och grafer*")
    
    # Kontrollera API-nyckel
    if "openai_api_key" not in st.session_state:
        with st.expander("⚙️ OpenAI API Konfiguration", expanded=True):
            st.markdown("""
            **För att använda AI-assistenten behöver du en OpenAI API-nyckel:**
            1. Gå till [OpenAI Platform](https://platform.openai.com/api-keys)
            2. Skapa en ny API-nyckel
            3. Klistra in den nedan
            """)
            
            api_key = st.text_input(
                "OpenAI API Nyckel", 
                type="password",
                help="Din API-nyckel sparas endast för denna session"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Spara API Nyckel"):
                    if api_key and api_key.startswith('sk-'):
                        st.session_state.openai_api_key = api_key
                        st.success("✅ API-nyckel sparad!")
                        st.rerun()
                    else:
                        st.error("❌ Ogiltig API-nyckel format")
            
            with col2:
                if st.button("🔗 Hämta API-nyckel"):
                    st.markdown("[Öppna OpenAI Platform](https://platform.openai.com/api-keys)")
        
        return
    
    # Initialisera AI-assistenten
    if "ai_assistant" not in st.session_state:
        try:
            st.session_state.ai_assistant = FinancialAIAssistant(
                st.session_state.openai_api_key
            )
            st.success("🤖 AI-assistent aktiverad!")
        except Exception as e:
            st.error(f"❌ Fel vid initialisering av AI: {str(e)}")
            return
    
    assistant = st.session_state.ai_assistant
    
    # Förbered datakontext
    data_summary = assistant.prepare_data_summary(analyzer, sheet_name)
    
    if not data_summary:
        st.error("❌ Kan inte förbereda data för AI-analys")
        return
    
    # Tabs för olika AI-funktioner
    tab1, tab2, tab3 = st.tabs(["💬 Fråga AI", "🧠 Strategisk Analys", "📝 Chat Historik"])
    
    with tab1:
        # Chat-gränssnitt
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Föreslagna frågor
        st.subheader("💭 Föreslagna Frågor")
        suggested_questions = assistant.get_suggested_questions(data_summary)
        
        # Visa föreslagna frågor i grid
        cols = st.columns(3)
        for i, question in enumerate(suggested_questions[:9]):
            col = cols[i % 3]
            if col.button(
                question, 
                key=f"suggested_{i}",
                help="Klicka för att ställa denna fråga",
                use_container_width=True
            ):
                st.session_state.user_question = question
        
        st.markdown("---")
        
        # Användarfråga
        st.subheader("💬 Ställ en Egen Fråga")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            user_question = st.text_input(
                "Din fråga",
                value=st.session_state.get("user_question", ""),
                placeholder="T.ex. 'Vilken månad hade högst intäkter?' eller 'Förklara trenden i grafen'",
                label_visibility="collapsed"
            )
        
        with col2:
            include_charts = st.checkbox(
                "📊 Inkludera grafer", 
                value=True,
                help="AI analyserar både data och visuella grafer"
            )
        
        if st.button("🚀 Fråga AI", disabled=not user_question, use_container_width=True):
            with st.spinner("🤖 AI analyserar dina finanser..."):
                # Samla grafbilder om inkluderade
                chart_images = {}
                if include_charts and hasattr(st.session_state, 'current_figures'):
                    for chart_name, fig in st.session_state.current_figures.items():
                        if fig:
                            chart_images[chart_name] = assistant.encode_chart_image(fig)
                
                # Få svar från AI
                answer = assistant.answer_question(
                    user_question, 
                    data_summary, 
                    chart_images if include_charts else None
                )
                
                # Lägg till i chatthistorik
                st.session_state.chat_history.append({
                    "question": user_question,
                    "answer": answer,
                    "timestamp": pd.Timestamp.now(),
                    "sheet_name": sheet_name,
                    "included_charts": include_charts
                })
                
                # Visa svaret
                st.success("✅ AI-analys klar!")
                with st.container():
                    st.markdown("### 🎯 AI-svar:")
                    st.markdown(answer)
                
                # Rensa användarfrågan
                st.session_state.user_question = ""
                st.rerun()
    
    with tab2:
        # Strategisk analys
        st.subheader("🧠 Djupgående Strategisk Analys")
        st.markdown("*AI:n analyserar flera års data för strategiska insikter*")
        
        # Välj år för analys
        available_years = analyzer.get_available_sheets()
        selected_years = st.multiselect(
            "Välj år för strategisk analys",
            available_years,
            default=available_years,
            help="Välj vilka år som ska inkluderas i den strategiska analysen"
        )
        
        analysis_type = st.selectbox(
            "Typ av strategisk analys",
            [
                "Övergripande Finansiell Hälsa",
                "Tillväxt och Trender",
                "Riskanalys",
                "Förbättringsmöjligheter"
            ]
        )
        
        if st.button("🔍 Generera Strategisk Analys", disabled=not selected_years):
            with st.spinner("🧠 AI genomför djupgående analys..."):
                strategic_analysis = assistant.generate_strategic_analysis(
                    analyzer, 
                    selected_years
                )
                
                st.success("✅ Strategisk analys klar!")
                with st.container():
                    st.markdown("### 📋 Strategisk AI-Analys:")
                    st.markdown(strategic_analysis)
                
                # Spara analysen
                if "strategic_analyses" not in st.session_state:
                    st.session_state.strategic_analyses = []
                
                st.session_state.strategic_analyses.append({
                    "analysis": strategic_analysis,
                    "years": selected_years,
                    "type": analysis_type,
                    "timestamp": pd.Timestamp.now()
                })
    
    with tab3:
        # Chatthistorik
        st.subheader("📝 Chatthistorik")
        
        if st.session_state.chat_history:
            # Visa chatthistorik
            for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):  # Senaste 10
                with st.expander(
                    f"Q: {chat['question'][:60]}{'...' if len(chat['question']) > 60 else ''}", 
                    expanded=(i == 0)
                ):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Fråga:** {chat['question']}")
                        st.markdown(f"**Svar:** {chat['answer']}")
                    with col2:
                        st.caption(f"📅 {chat['timestamp'].strftime('%Y-%m-%d')}")
                        st.caption(f"🕐 {chat['timestamp'].strftime('%H:%M:%S')}")
                        st.caption(f"📊 {chat['sheet_name']}")
                        if chat.get('included_charts'):
                            st.caption("🖼️ Inkluderade grafer")
            
            # Kontroller för chatthistorik
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 Exportera Chat"):
                    # Skapa export av chatthistorik
                    chat_export = "\n\n".join([
                        f"FRÅGA: {chat['question']}\nSVAR: {chat['answer']}\nTID: {chat['timestamp']}"
                        for chat in st.session_state.chat_history
                    ])
                    st.download_button(
                        "💾 Ladda ner Chat",
                        chat_export,
                        file_name=f"ai_chat_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
            
            with col2:
                if st.button("🗑️ Rensa Historik"):
                    st.session_state.chat_history = []
                    st.success("✅ Chatthistorik rensad!")
                    st.rerun()
        else:
            st.info("💭 Ingen chatthistorik än. Ställ din första fråga ovan!")

# Lägg till i huvudfunktionen för att spara figurer
def save_figure_for_ai(fig, name):
    """
    Sparar figurer för AI-analys
    """
    if 'current_figures' not in st.session_state:
        st.session_state.current_figures = {}
    
    st.session_state.current_figures[name] = fig

# Modifiera befintliga chart-funktioner
def display_dashboard_with_ai(analyzer, sheet_name, options, data_type='financial'):
    """
    Utökad dashboard-funktion med AI-integration
    """
    st.header(f"Analys för: {sheet_name}")
    
    # Rensa tidigare figurer
    st.session_state.current_figures = {}
    
    # Trends chart
    if options['trends']:
        st.subheader("📈 Månadsvis Finansiell Utveckling")
        fig_trends = analyzer.create_financial_trends_by_category(sheet_name)
        if fig_trends:
            st.plotly_chart(fig_trends, use_container_width=True)
            save_figure_for_ai(fig_trends, "trends")
    
    # Distribution chart
    if options['distribution']:
        st.subheader("📊 Kategorifördelning")
        fig_pie = analyzer.create_category_distribution_chart(sheet_name)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
            save_figure_for_ai(fig_pie, "distribution")
    
    # Heatmap
    if options['heatmap']:
        st.subheader("🔥 Aktivitetsheatmap")
        fig_heatmap = analyzer.create_heatmap(sheet_name)
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True)
            save_figure_for_ai(fig_heatmap, "heatmap")
    
    # Top performers
    if options['top_performers']:
        st.subheader("🏆 Bästa/Sämsta Kategorier")
        fig_top = analyzer.create_top_performers_chart(sheet_name)
        if fig_top:
            st.plotly_chart(fig_top, use_container_width=True)
            save_figure_for_ai(fig_top, "top_performers")
    
    # AI-sektion
    if options.get('ai_assistant', True):
        st.markdown("---")
        display_ai_assistant(analyzer, sheet_name)
```

## 🔒 Säkerhet och Konfiguration

### Secrets Management
```toml
# .streamlit/secrets.toml
[auth]
username = "Admin" 
password = "DittSäkraLösenord123!"

[openai]
api_key = "sk-ditt-openai-api-key-här"

[financial]
currency = "SEK"
company_name = "Ditt Företag AB"
```

### Environment Setup
```python
# requirements.txt - lägg till dessa
openai>=1.3.0
pillow>=10.0.0
kaleido>=0.2.1  # För Plotly bildexport
```

### Säker API-hantering
```python
def get_openai_client():
    """
    Hämtar OpenAI-klient på säkert sätt
    """
    # Försök secrets först, sedan session state
    api_key = None
    
    try:
        api_key = st.secrets["openai"]["api_key"]
    except (KeyError, FileNotFoundError):
        api_key = st.session_state.get("openai_api_key")
    
    if not api_key:
        return None
        
    return openai.OpenAI(api_key=api_key)

# Kostnadsövervakning
def track_api_usage():
    """
    Spåra API-användning för kostnadskontroll
    """
    if "api_usage" not in st.session_state:
        st.session_state.api_usage = {
            "requests_today": 0,
            "tokens_used": 0,
            "last_reset": pd.Timestamp.now().date()
        }
    
    # Återställ daglig användning
    if st.session_state.api_usage["last_reset"] != pd.Timestamp.now().date():
        st.session_state.api_usage = {
            "requests_today": 0,
            "tokens_used": 0,
            "last_reset": pd.Timestamp.now().date()
        }
```

## 💡 Exempel på AI-Interaktioner

### Typiska Användarfrågor och AI-svar:

**Fråga:** "Vilken månad hade bäst resultat 2023?"
**AI-svar:** "Baserat på din finansiella data för 2023 hade mars månad det bästa resultatet med en nettovinst på 45,000 SEK. Detta berodde främst på höga intäkter (85,000 SEK) kombinerat med relativt låga kostnader (40,000 SEK). Jag kan se i linjediagrammet att detta följer ett säsongsmönster där Q1 traditionellt presterar starkt."

**Fråga:** "Förklara vad heatmapen visar"
**AI-svar:** "Heatmapen visar intensiteten av finansiell aktivitet över året genom färgkodning. De mörkare blå områdena indikerar månader med hög aktivitet/intäkter, medan ljusare områden visar lägre aktivitet. Jag kan se att intäktskategorin är mest intensiv under mars-maj, vilket tyder på en stark vårperiod för ditt företag. Kostnadskategorin visar mer jämn fördelning, vilket är positivt för cashflow-planering."

**Fråga:** "Vad rekommenderar du för förbättringar?"
**AI-svar:** "Baserat på din data ser jag flera förbättringsområden: 1) Sommarperioden (juni-augusti) visar lägre intäkter - överväg säsongskampanjer. 2) Kostnaderna i november är ovanligt höga - undersök orsaken. 3) Din vinstmarginal på 23% är bra, men kan förbättras genom kostnadsoptimering under Q4. 4) Investeringarna är ojämnt fördelade - överväg att sprida ut dem för bättre cashflow."

## 🚀 Implementation Guide

### Steg 1: Grundläggande Setup
```bash
pip install openai pillow kaleido
```

### Steg 2: Lägg till AI-klassen
Kopiera `FinancialAIAssistant` klassen till din `financial_analyzer.py`

### Steg 3: Integrera i Dashboard
Lägg till AI-funktionerna i din `dashboard.py`

### Steg 4: Konfigurera API
Sätt upp OpenAI API-nyckel i secrets eller session state

### Steg 5: Testa
Starta dashboarden och testa AI-funktionaliteten

## 📊 Avancerade Funktioner

### Multi-Year Analysis
AI:n kan analysera flera år samtidigt för långsiktiga trender

### Strategic Recommendations
Djupgående strategisk analys med konkreta rekommendationer

### Chart Understanding
AI förstår och kan förklara komplexa finansiella visualiseringar

### Context Awareness
AI kommer ihåg tidigare frågor i sessionen för bättre kontext

Med denna AI-integration får du ett intelligent finansiellt analysverktyg som kan svara på naturliga språkfrågor och ge djupa insikter baserat på både rådata och visuella diagram! 🎯
