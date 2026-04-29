import json
import os

# State file'ı mevcut dosyanın bulunduğu dizinde (ingestion/) saklayalım
STATE_FILE = os.path.join(os.path.dirname(__file__), "ingestion_state.json")

def load_state(source: str):
    """
    Belirtilen kaynak (source) için kayıtlı olan en son durumu (state) getirir.
    Eğer dosya yoksa veya kaynak bulunamadıysa None döner.
    """
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(source)
    except json.JSONDecodeError:
        return None

def save_state(source: str, state_value):
    """
    Belirtilen kaynak (source) için yeni durumu JSON dosyasına kaydeder.
    """
    data = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass # Eğer dosya bozuksa sıfırdan başlar
            
    data[source] = state_value
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
