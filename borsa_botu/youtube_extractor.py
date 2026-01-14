import yt_dlp
import asyncio
import re

def strip_ansi(text):
    # Düzgün bir şekilde hem hexadecimal hem de literal ANSI escape karakterlerini temizleyen regex
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

async def extract_channel_videos(channel_url, sort_by='new'):
    """
    Kanal linkinden tum video URL'lerini ve basliklarini ceker.
    @handle formatini otomatik olarak full URL'ye cevirir.
    sort_by: 'new' (En Yeniler) veya 'popular' (En Popülerler)
    """
    if channel_url.startswith('@'):
        channel_base = f"https://www.youtube.com/{channel_url}"
    elif "youtube.com/channel/" in channel_url or "youtube.com/c/" in channel_url or "youtube.com/@" in channel_url:
        channel_base = channel_url.split('/videos')[0].split('?')[0]
    else:
        channel_base = channel_url

    if sort_by == 'popular':
        # En popüler videolar için YouTube'un kullandığı URL formatı
        channel_url = f"{channel_base}/videos?view=0&sort=p"
    else:
        channel_url = f"{channel_base}/videos"
    
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'playlist_items': '1-50',  # Test amaciyla son 50 videoyu alalim
        'nocolor': True,
    }
    
    try:
        # yt-dlp'yi asenkron calistirmak icin loop.run_in_executor kullanilabilir 
        # veya dogrudan bu sekilde basit tutulabilir (kisa listeler icin)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' in info:
                videos = []
                for entry in info['entries']:
                    if entry:
                        videos.append({
                            'title': entry.get('title'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'id': entry.get('id')
                        })
                return {'channel_title': info.get('title'), 'videos': videos}
            return {'error': 'Kanal bilgisi alınamadı veya liste boş.'}
    except Exception as e:
        error_msg = strip_ansi(str(e))
        if "404" in error_msg:
            return {'error': "YouTube kanalı bulunamadı. Lütfen URL'yi kontrol edin (Örn: @KanalAdi)."}
        return {'error': f"Analiz Hatası: {error_msg}"}

if __name__ == "__main__":
    # Test
    url = "https://www.youtube.com/@Deepverify"
    result = asyncio.run(extract_channel_videos(url))
    print(f"Kanal: {result.get('channel_title')}")
    print(f"Toplam Video: {len(result.get('videos', []))}")
