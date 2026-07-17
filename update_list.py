# Kanal ID'lerini buraya eklemen yeterli. 
# Yeni bir kanal bulursan sadece "isim": "ID" şeklinde ekle.
channels = {
    "bizimkiler": "50840"
}

m3u_content = "#EXTM3U\n\n"

for name, channel_id in channels.items():
    # Sizin belirttiğiniz kesin formatı oluşturuyoruz
    stream_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8"
    
    # Televizo'nun korumayı aşması için gerekli boru (|) formatı
    safe_url = f"{stream_url}|Referer=https://catcast.tv/&User-Agent=Mozilla/5.0"
    
    # Televizo listesine ekle
    m3u_content += f'#EXTINF:-1 tvg-name="{name.capitalize()}", {name.capitalize()}\n'
    m3u_content += f'{safe_url}\n\n'

# Dosyayı kaydet
with open("channels.m3u", "w") as f:
    f.write(m3u_content)
