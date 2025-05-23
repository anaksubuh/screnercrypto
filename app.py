from streamlit_option_menu import option_menu
import streamlit as st
import json
import os

SETTINGS_FILE = "settings.json"

st.set_page_config(
    page_title='SCRENNER CRYPTO',
    page_icon='bitcoin.png',
    layout='wide',  
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': 'https://www.extremelycoolapp.com/bug',
         'About': '# This is a header. This is an *extremely* cool app!'
    }
)

# Fungsi load/save settings
def load_settings():
    default_settings = {
        "col_count": 2,
        "ban_count": 10,
        "interval": "60",
        "show_details": True,
        "show_calendar": True,
        "show_hotlist": True,
        "indicators": [],
        "selected_brokers": [],
        "selected_types": [],
        "current_page": 1
    }
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            loaded = json.load(f)
        # Merge default dengan loaded, loaded lebih prioritas
        for key, val in default_settings.items():
            if key not in loaded:
                loaded[key] = val
        return loaded
    return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# Initialize session state
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()
    st.session_state.temp_settings = load_settings().copy()  # Untuk menyimpan sementara perubahan

# Load setting dari session state
settings = st.session_state.settings
temp_settings = st.session_state.temp_settings

with st.sidebar:

    selected = option_menu('Menu', ['All','Spesifik'], icons=['house','book','list','chat','gear'], menu_icon="cast", default_index=0)

# Baca coin.txt dan ekstrak broker dan jenis yang unik
@st.cache_data
def load_coin_data():
    with open("coin.txt", "r", encoding="utf-8") as f:
        coin_list = [line.strip() for line in f if line.strip()]
    
    # Ekstrak semua broker dan jenis yang tersedia
    all_brokers = set()
    all_types = set()
    filtered_coins = []

    for coin in coin_list:
        parts = coin.split(":::")
        if len(parts) >= 4:
            filtered_coins.append(coin)
            all_brokers.add(parts[3])
            all_types.add(parts[2])

    return filtered_coins, sorted(all_brokers), sorted(all_types)

coin_list, all_brokers, all_types = load_coin_data()

# Sidebar pengaturan
st.sidebar.header("⚙️ Pengaturan Tampilan")
# Simpan perubahan ke temp_settings tanpa langsung mempengaruhi tampilan
temp_settings["col_count"] = st.sidebar.selectbox(
    "Jumlah Kolom", [1, 2, 3, 4, 5], 
    index=[1, 2, 3, 4, 5].index(temp_settings["col_count"])
)
temp_settings["ban_count"] = st.sidebar.selectbox(
    "Jumlah Kolom", 
    options=list(range(1, 26)),  # Angka 1 sampai 25
    index=temp_settings.get("ban_count", 1) - 1  # Default ke 1 jika tidak ada
)
temp_settings["interval"] = st.sidebar.selectbox(
    "Interval", ["1", "5", "15", "30", "60", "120", "D", "W", "M"], 
    index=["1", "5", "15", "30", "60", "120", "D", "W", "M"].index(temp_settings["interval"])
)
temp_settings["show_details"] = st.sidebar.checkbox(
    "Tampilkan Detail", 
    value=temp_settings["show_details"]
)
temp_settings["show_calendar"] = st.sidebar.checkbox(
    "Tampilkan Kalender", 
    value=temp_settings["show_calendar"]
)
temp_settings["show_hotlist"] = st.sidebar.checkbox(
    "Tampilkan Hotlist", 
    value=temp_settings["show_hotlist"]
)
# Filter broker dan jenis (disimpan di temp_settings)
temp_settings["selected_brokers"] = st.sidebar.multiselect(
    "Filter Broker:",
    options=all_brokers,
    default=temp_settings["selected_brokers"]
)
temp_settings["selected_types"] = st.sidebar.multiselect(
    "Filter Jenis:",
    options=all_types,
    default=temp_settings["selected_types"]
)
indicator_options = {
    "RSI": "RSI@tv-basicstudies",
    "MACD": "MACD@tv-basicstudies",
    "EMA": "MAExp@tv-basicstudies",
    "SMA": "MASimple@tv-basicstudies",
    "Bollinger Bands": "BollingerBands@tv-basicstudies",
    "Volume": "Volume@tv-basicstudies"
}
temp_settings["indicators"] = [indicator_options[i] for i in st.sidebar.multiselect(
    "Indikator yang digunakan:",
    options=list(indicator_options.keys()),
    default=[k for k, v in indicator_options.items() if v in temp_settings["indicators"]]
)]

if selected == 'All':
    #st.set_page_config(layout="wide")
    st.title("📊 Chart Crypto Otomatis + Setting Persisten")

    st.sidebar.markdown("---")

    # Tombol Simpan dan Terapkan
    col1, col2 = st.sidebar.columns(2)
    if col1.button("💾 Simpan Setting"):
        settings.update(temp_settings)
        save_settings(settings)
        st.session_state.settings = settings.copy()
        st.session_state.temp_settings = settings.copy()
        st.sidebar.success("✅ Setting berhasil disimpan!")

    if col2.button("🔄 Terapkan Filter"):
        settings.update(temp_settings)
        st.session_state.settings = settings.copy()
        st.session_state.temp_settings = settings.copy()
        st.sidebar.success("✅ Filter diterapkan!")

    # Filter coin berdasarkan broker dan jenis yang dipilih
    filtered_coin_list = []
    for coin in coin_list:
        parts = coin.split(":::")
        if len(parts) >= 4:
            namacoin = parts[0]
            namapanjang = parts[1]
            jenis = parts[2]
            broker = parts[3]
            
            # Filter berdasarkan broker dan jenis
            broker_match = not settings["selected_brokers"] or broker in settings["selected_brokers"]
            type_match = not settings["selected_types"] or jenis in settings["selected_types"]
            
            if broker_match and type_match:
                filtered_coin_list.append(coin)

    # Pagination
    coins_per_page = 10
    total_pages = max(1, (len(filtered_coin_list) + coins_per_page - 1) // coins_per_page)

    # Input halaman dengan callback untuk update current_page
    def update_current_page():
        temp_settings["current_page"] = st.session_state.current_page_input

    current_page = st.sidebar.number_input(
        "Halaman ke:", 
        min_value=1, 
        max_value=total_pages, 
        value=settings["current_page"], 
        step=1,
        key="current_page_input",
        on_change=update_current_page
    )

    # Update current_page di settings jika diubah
    if temp_settings["current_page"] != settings["current_page"]:
        settings["current_page"] = temp_settings["current_page"]
        st.session_state.settings = settings.copy()

    # Tentukan coin yang ditampilkan
    start_idx = (settings["current_page"] - 1) * coins_per_page
    end_idx = min(start_idx + coins_per_page, len(filtered_coin_list))
    current_coins = filtered_coin_list[start_idx:end_idx]

    # Render chart sesuai setting
    for i in range(0, len(current_coins), settings["col_count"]):
        cols = st.columns(settings["col_count"])
        for j in range(settings["col_count"]):
            if i + j < len(current_coins):
                symbol = current_coins[i + j]
                
                symbol = symbol.split(":::")
                namacoin = symbol[0]
                namapanjang = symbol[1]
                jennis = symbol[2]
                broker = symbol[3]

                unique_id = f"tv_{broker+'_'+namacoin}"
                
                studies_json = json.dumps(settings["indicators"])

                chart_html = f"""
                <div class="tradingview-widget-container">
                <div id="{unique_id}"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                    "width": "100%",
                    "height": 650,
                    "symbol": "{namacoin}",
                    "interval": "{settings['interval']}",
                    "timezone": "Asia/Jakarta",
                    "theme": "dark",
                    "style": "1",
                    "locale": "id",
                    "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false,
                    "allow_symbol_change": true,
                    "container_id": "{unique_id}",
                    "studies": {studies_json},
                    "withdateranges": true,
                    "hide_side_toolbar": false,
                    "details": {str(settings['show_details']).lower()},
                    "hotlist": {str(settings['show_hotlist']).lower()},
                    "calendar": {str(settings['show_calendar']).lower()},
                    "hide_volume": false,
                    "support_host": "https://www.tradingview.com"
                }});
                </script>
                </div>
                """

                with cols[j]:
                    st.subheader(f'{namacoin} | {namapanjang} | {jennis} | {broker}')
                    st.components.v1.html(chart_html, height=670)

if selected == 'Spesifik':
    search_term = st.text_input("Cari koin (nama, broker, atau jenis):", "").upper()

    # Filter coin berdasarkan pencarian
    filtered_coins = []
    for coin in coin_list:
        parts = coin.split(":::")
        if len(parts) >= 4:
            namacoin = parts[0]
            namapanjang = parts[1]
            jenis = parts[2]
            broker = parts[3]
            
            # Cari di semua field
            if (search_term in namacoin.upper() or 
                search_term in namapanjang.upper() or 
                search_term in jenis.upper() or 
                search_term in broker.upper()):
                filtered_coins.append(coin)

    # Tampilkan hasil pencarian
    if search_term:
        if not filtered_coins:
            st.warning("Tidak ditemukan koin yang sesuai")
        else:
            # Pagination - maksimal 10 coin per halaman
            coins_per_page = 10
            total_pages = max(1, (len(filtered_coins) + coins_per_page - 1) // coins_per_page)
            
            # Buat selectbox untuk pagination
            if 'search_page' not in st.session_state:
                st.session_state.search_page = 1
                
            current_page = st.sidebar.number_input(
                "Halaman:",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.search_page,
                key='search_page_input'
            )
            
            # Update session state jika page berubah
            if current_page != st.session_state.search_page:
                st.session_state.search_page = current_page
                st.experimental_rerun()
            
            # Hitung coin yang akan ditampilkan
            start_idx = (st.session_state.search_page - 1) * coins_per_page
            end_idx = min(start_idx + coins_per_page, len(filtered_coins))
            current_coins = filtered_coins[start_idx:end_idx]
            
            # Info pagination
            st.caption(f"Menampilkan {start_idx + 1}-{end_idx} dari {len(filtered_coins)} hasil")
            
            # Render hasil pencarian (maksimal 10 per halaman)
            for i in range(0, len(current_coins), settings["col_count"]):
                cols = st.columns(settings["col_count"])
                for j in range(settings["col_count"]):
                    if i + j < len(current_coins):
                        symbol = current_coins[i + j]
                        
                        symbol = symbol.split(":::")
                        namacoin = symbol[0]
                        namapanjang = symbol[1]
                        jennis = symbol[2]
                        broker = symbol[3]

                        unique_id = f"tv_spec_{broker+'_'+namacoin}_{i+j}"
                        
                        studies_json = json.dumps(settings["indicators"])

                        chart_html = f"""
                        <div class="tradingview-widget-container">
                        <div id="{unique_id}"></div>
                        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                        <script type="text/javascript">
                        new TradingView.widget({{
                            "width": "100%",
                            "height": 500,
                            "symbol": "{namacoin}",
                            "interval": "{settings['interval']}",
                            "timezone": "Asia/Jakarta",
                            "theme": "dark",
                            "style": "1",
                            "locale": "id",
                            "toolbar_bg": "#f1f3f6",
                            "enable_publishing": false,
                            "allow_symbol_change": true,
                            "container_id": "{unique_id}",
                            "studies": {studies_json},
                            "withdateranges": true,
                            "hide_side_toolbar": false,
                            "details": {str(settings['show_details']).lower()},
                            "hotlist": {str(settings['show_hotlist']).lower()},
                            "calendar": {str(settings['show_calendar']).lower()},
                            "hide_volume": false,
                            "support_host": "https://www.tradingview.com"
                        }});
                        </script>
                        </div>
                        """

                        with cols[j]:
                            st.subheader(f'{namacoin} | {namapanjang} | {jennis} | {broker}')
                            st.components.v1.html(chart_html, height=520)
    else:
        st.info("Masukkan kata kunci pencarian di atas (contoh: BTC, Binance, dll)")