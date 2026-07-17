import requests
import re

channels = {
    "bizimkiler": "https://catcast.tv/fanatikprimebizimkiler"
}

m3u_content = "#EXTM3U\n\n"

for name, url in channels.items():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    
    print(f"--- HATA AYIKLAMA: {name} ---")
    print(f"Status Code: {response.status_code}")
    # Sayfadan gelen içeriğin ilk 500 karakterini loga yazdır
    print(f"Content snippet: {response.text[:500]}...") 
    
    # regex'i daha esnek hale getirelim
    # Linkin tamamını değil, sadece ID'yi arayalım
    match = re.search(r'/content/(\d+)/index\.m3u8', response.text)
    
    if match:
        channel_id = match.group(1)
        print(f"BAŞARILI: ID bulundu -> {channel_id}")
        stream_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8"
        safe_url = f"{stream_url}|Referer=https://catcast.tv/&User-Agent=Mozilla/5.0"
        m3u_content += f'#EXTINF:-1, {name.capitalize()}\n{safe_url}\n\n'
    else:
        print("HATA: Regex eşleşme sağlamadı. Sayfa kaynağında link bulunamadı.")

with open("channels.m3u", "w") as f:
    f.write(m3u_content)
