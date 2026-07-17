# Buraya sadece kanal isimlerini ve ID'lerini yazıyoruz. 
# Bu yöntem %100 çalışır çünkü sayfayı kazımaya çalışıp hata almaz.
channels = {
    "bizimkiler": "50840",
    # "kurtlarvadisi": "BURAYA_DIGER_ID_GELECEK"
}

m3u_content = "#EXTM3U\n\n"

for name, channel_id in channels.items():
    # Catcast'in istediği referer ve user-agent'ı ekliyoruz
    # Televizo bu formatı doğrudan anlar
    safe_url = f"https://v2.catcast.tv/content/{channel_id}/index.m3u8|Referer=https://catcast.tv/&User-Agent=Mozilla/5.0"
    
    m3u_content += f'#EXTINF:-1 tvg-name="{name.capitalize()}", {name.capitalize()}\n'
    m3u_content += f'{safe_url}\n\n'

with open("channels.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)
