"""
Finansiell Analyzer - CLEAN VERSION - Endast dataläsning från Excel
"""
import pandas as pd
import os

class FinancialAnalyzer:
    def __init__(self, excel_file_path=None, data_type='financial'):
        """
        Initialiserar analysatorn med Excel-fil
        """
        self.data_type = data_type
        self.excel_file_path = excel_file_path
        self.data = {}
        self.processed_data = {}
        self.available_sheets = []
        
        # Ingen kategoridatabas behövs för denna enkla version
        
        # Ladda data från Excel
        if self.excel_file_path:
            self.load_data()
        else:
            # Try to find financial file automatically
            found_file = self._find_financial_file()
            if found_file:
                self.excel_file_path = found_file
                self.load_data()

    def _find_financial_file(self):
        """Hittar Excel-fil automatiskt"""
        possible_files = [
            'Finansiell Data.xlsx',
            'finansiell_data.xlsx', 
            'data.xlsx'
        ]
        
        for filename in possible_files:
            if os.path.exists(filename):
                print(f"✅ Hittade Excel-fil: {filename}")
                return filename

        return None

    def load_data(self):
        """Läser in alla flikar från Excel-filen"""
        if not self.excel_file_path or not os.path.exists(self.excel_file_path):
            raise Exception(f"Excel-fil hittades inte: {self.excel_file_path}")
        
        try:
            excel_file = pd.ExcelFile(self.excel_file_path)
            self.available_sheets = excel_file.sheet_names
            
            for sheet_name in self.available_sheets:
                # Leta efter rätt header-rad (KONTO/BESKRIVNING)
                df_temp = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
                header_row = None
                
                for i, row in df_temp.iterrows():
                    if 'KONTO/BESKRIVNING' in str(row.iloc[0]):
                        header_row = i
                        break
                
                if header_row is not None:
                    # Läs data med rätt header
                    df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name, header=header_row)
                    # Sätt korrekta kolumnnamn
                    expected_months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 
                                     'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec', 'Totalt']
                    new_columns = ['Kategori']
                    
                    # Lägg till månadsnamn för de faktiska datakolumnerna  
                    for i, col in enumerate(df.columns[1:]):
                        if i < len(expected_months):
                            new_columns.append(expected_months[i])
                        else:
                            new_columns.append(str(col))
                    
                    df.columns = new_columns
                else:
                    # Fallback till standardformat
                    df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
                
                self.data[sheet_name] = df
                
            self.clean_and_standardize_data()
            print(f"✅ Laddade data från {len(self.available_sheets)} flikar: {self.available_sheets}")
            
        except Exception as e:
            raise Exception(f"Fel vid inläsning av Excel-fil: {str(e)}")

    def clean_and_standardize_data(self):
        """Rengör och standardiserar dataformatet"""
        for sheet_name, df in self.data.items():
            try:
                # Rensa tomma rader
                df = df.dropna(how='all')
                
                # Rensa rader där första kolumnen är tom
                df = df.dropna(subset=[df.columns[0]])
                
                # Sätt första kolumnen som index
                df = df.set_index(df.columns[0])
                
                # Konvertera svenska decimalformat (komma -> punkt) för beräkningar
                for col in df.columns:
                    if col != 'Kategori':
                        # Konvertera komma till punkt för svenska tal
                        df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                        # Konvertera till nummer
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                self.processed_data[sheet_name] = df
                print(f"  ✅ Bearbetade {sheet_name}: {df.shape[0]} rader, {df.shape[1]} kolumner")
                
            except Exception as e:
                print(f"  ⚠️ Kunde inte bearbeta {sheet_name}: {e}")
                continue
            
    def get_raw_data(self, sheet_name):
        """Returnerar rå data från Excel för en specifik flik"""
        if sheet_name in self.data:
            return self.data[sheet_name]
        return None

    def get_processed_data(self, sheet_name):
        """Returnerar bearbetad data för en specifik flik"""
        if sheet_name in self.processed_data:
            return self.processed_data[sheet_name]
        return None

    def print_data_summary(self):
        """Skriver ut en sammanfattning av inläst data"""
        print(f"\n📊 DATASAMMANFATTNING:")
        print(f"Excel-fil: {self.excel_file_path}")
        print(f"Antal flikar: {len(self.available_sheets)}")
        
        for sheet_name in self.available_sheets:
            if sheet_name in self.processed_data:
                df = self.processed_data[sheet_name]
                print(f"\n🔹 {sheet_name}:")
                print(f"  Storlek: {df.shape[0]} rader × {df.shape[1]} kolumner")
                print(f"  Kategorier: {list(df.index[:5])}{'...' if len(df.index) > 5 else ''}")
                print(f"  Kolumner: {list(df.columns)}")
                
                # Visa några exempel på data
                print(f"  Exempel på data:")
                for i, (category, row) in enumerate(df.head(3).iterrows()):
                    print(f"    {category}: {dict(row)}")
                    if i >= 2:
                        break