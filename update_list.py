import streamlink
import sys
import os
import json
import traceback
import requests
import re

def get_catcast_m3u8(url):
    # Siteye gerçek bir tarayıcıdan giriyormuşuz gibi görünmek için başlık (header) ekliyoruz
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        match = re.search(r'(https?://[^\s"\'<>]+?\.m3u8)', response.text)
        
        if match:
            return match.group(1)
        else:
            return None
            
    except Exception as e:
        print(f"  ❌ Catcast bağlantı hatası: {e}")
        return None

def info_to_text(stream_info, url):
    text = '#EXT-X-STREAM-INF:'
    if stream_info.program_id:
        text = text + 'PROGRAM-ID=' + str(stream_info.program_id) + ','
    if stream_info.bandwidth:
        text = text + 'BANDWIDTH=' + str(stream_info.bandwidth) + ','
    if stream_info.codecs:
        text = text + 'CODECS="'
        codecs = stream_info.codecs
        for i in range(0, len(codecs)):
            text = text + codecs[i]
            if len(codecs) - 1 != i:
                text = text + ','
        text = text + '",'
    if stream_info.resolution.width:
        text = text + 'RESOLUTION=' + str(stream_info.resolution.width) + 'x' + str(stream_info.resolution.height) 

    text = text + "\n" + url + "\n"
    return text

def main():
    print("=== Starting stream processing ===")
    
    # Loading config file
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    print(f"Loading config from: {config_file}")
    
    try:
        f = open(config_file, "r")
        config = json.load(f)
        f.close()
    except Exception as e:
        print(f"❌ ERROR loading config file: {e}")
        sys.exit(1)

    # Getting output options and creating folders
    folder_name = config["output"]["folder"]
    best_folder_name = config["output"]["bestFolder"]
    master_folder_name = config["output"]["masterFolder"]
    current_dir = os.getcwd()
    root_folder = os.path.join(current_dir, folder_name)
    best_folder = os.path.join(root_folder, best_folder_name)
    master_folder = os.path.join(root_folder, master_folder_name)
    
    print(f"Creating folders:")
    print(f"  Root: {root_folder}")
    print(f"  Best: {best_folder}")
    print(f"  Master: {master_folder}")
    
    os.makedirs(best_folder, exist_ok=True)
    os.makedirs(master_folder, exist_ok=True)

    channels = config["channels"]
    print(f"\n=== Processing {len(channels)} channels ===\n")
    
    success_count = 0
    fail_count = 0

    for idx, channel in enumerate(channels, 1):
        slug = channel.get("slug", "unknown")
        url = channel.get("url", "")
        
        print(f"[{idx}/{len(channels)}] Processing: {slug}")
        print(f"  URL: {url}")
        
        # --- CATCAST KONTROLÜ BURADA BAŞLIYOR ---
        if "catcast.tv" in url and ".m3u8" not in url:
            extracted_url = get_catcast_m3u8(url)
            if extracted_url:
                url = extracted_url
                print(f"  🔗 Catcast linki çözüldü: {url}")
            else:
                print(f"  ⚠️ Catcast m3u8 linki bulunamadı, atlanıyor...")
                fail_count += 1
                continue
        # --- CATCAST KONTROLÜ BURADA BİTİYOR ---
        
        try:
            # Get streams and playlists
            streams = streamlink.streams(url)
            
            if not streams:
                print(f"  ⚠️  No streams found for {slug}")
                fail_count += 1
                continue
                
            if 'best' not in streams:
                print(f"  ⚠️  No 'best' stream found for {slug}")
                print(f"  Available streams: {list(streams.keys())}")
                fail_count += 1
                continue
            
            playlists = streams['best'].multivariant.playlists

            # Text preparation
            previous_res_height = 0
            master_text = ''
            best_text = ''

            # Check http/https options
            http_flag = False
            if url.startswith("http://") and "catcast.tv" not in url: 
                # Catcast linkleri m3u8 olarak geldiğinde plugin'e girip hata vermemesi için koruma
                try:
                    plugin_name, plugin_type, given_url = streamlink.session.Streamlink().resolve_url(url)
                    http_flag = True
                except:
                    pass

            for playlist in playlists:
                uri = playlist.uri
                info = playlist.stream_info
                # Sorting sub-playlist based on resolution
                if info.video != "audio_only": 
                    sub_text = info_to_text(info, uri)
                    if info.resolution.height > previous_res_height:
                        master_text = sub_text + master_text
                        best_text = sub_text
                    else:
                        master_text = master_text + sub_text
                    previous_res_height = info.resolution.height
            
            # Necessary values for HLS
            if master_text:
                if streams['best'].multivariant.version:
                    master_text = '#EXT-X-VERSION:' + str(streams['best'].multivariant.version) + "\n" + master_text
                    best_text = '#EXT-X-VERSION:' + str(streams['best'].multivariant.version) + "\n" + best_text
                master_text = '#EXTM3U\n' + master_text
                best_text = '#EXTM3U\n' + best_text

            # HTTPS -> HTTP for cinergroup plugin
            if http_flag:
                if plugin_name == "cinergroup":
                    master_text = master_text.replace("https://", "http://")
                    best_text = best_text.replace("https://", "http://")

            # File operations
            master_file_path = os.path.join(master_folder, channel["slug"] + ".m3u8")
            best_file_path = os.path.join(best_folder, channel["slug"] + ".m3u8")

            if master_text:
                with open(master_file_path, "w+") as master_file:
                    master_file.write(master_text)

                with open(best_file_path, "w+") as best_file:
                    best_file.write(best_text)
                
                print(f"  ✅ Success - Files created")
                success_count += 1
            else:
                print(f"  ⚠️  No content generated for {slug}")
                if os.path.isfile(master_file_path):
                    os.remove(master_file_path)
                if os.path.isfile(best_file_path):
                    os.remove(best_file_path)
                fail_count += 1
                
        except Exception as e:
            print(f"  ❌ ERROR processing {slug}: {str(e)}")
            print(f"  {traceback.format_exc()}")
            
            master_file_path = os.path.join(master_folder, channel["slug"] + ".m3u8")
            best_file_path = os.path.join(best_folder, channel["slug"] + ".m3u8")
            if os.path.isfile(master_file_path):
                os.remove(master_file_path)
            if os.path.isfile(best_file_path):
                os.remove(best_file_path)
            fail_count += 1
    
    print(f"\n=== Summary ===")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"Total: {len(channels)}")

if __name__=="__main__": 
    main()
