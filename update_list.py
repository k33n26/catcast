import requests
import re

# Kanal isimleri ve kaynak linkleri
channels = {
    "bizimkiler": "https://catcast.tv/fanatikprimebizimkiler"
}

m3u_content = "#EXTM3U\n\n"

for name, url in channels.items():
    try:
        # Siteye bir tarayıcı gibi davranarak istek atıyoruz
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        
        # Sayfa içeriğinde şu kalıbı arıyoruz: v2.catcast.tv/content/50840/index.m3u8
        # Regex ile sadece o ID numarasını çekiyoruz
        match = re.search(r'v2\.catcast\.tv/content/(\d+)/index\.m3u8', response.text)
        
        if match:
            channel_id = match.group(1)
            stream_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8"
            
            # Televizo'nun korumayı aşması için boru (|) formatı
            safe_url = f"{stream_url}|Referer=https://catcast.tv/&User-Agent=Mozilla/5.0"
            m3u_content += f'#EXTINF:-1, {name.capitalize()}\n{safe_url}\n\n'
        else:
            print(f"HATA: {name} için yayın linki bulunamadı (Sayfa yapısı değişmiş olabilir).")
            
    except Exception as e:
        print(f"HATA: {e}")

with open("channels.m3u", "w") as f:
    f.write(m3u_content)
