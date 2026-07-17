import yt_dlp

channels = {
    "bizimkiler": "https://catcast.tv/fanatikprimebizimkiler"
}

m3u_content = "#EXTM3U\n\n"
for name, url in channels.items():
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info.get('url')
        if stream_url:
            # Boru işaretini ekleyerek Televizo uyumlu hale getiriyoruz
            safe_url = f"{stream_url}|Referer=https://catcast.tv/&User-Agent=Mozilla/5.0"
            m3u_content += f'#EXTINF:-1, {name.capitalize()}\n{safe_url}\n\n'

with open("channels.m3u", "w") as f:
    f.write(m3u_content)
