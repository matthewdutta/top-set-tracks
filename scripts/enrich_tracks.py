"""Fill in exact listening links and 30-second previews for tracks.json.

For every track, looks the song up on Apple's public iTunes Search API to get the
exact Apple Music link and preview audio, then asks song.link (Odesli) for the
matching Spotify and YouTube links. Only fills fields that are empty, so any link
added by hand is never overwritten. Runs in GitHub Actions on every change to
tracks.json.
"""
import json, re, sys, time, urllib.parse, urllib.request

PATH = "tracks.json"
UA = {"User-Agent": "TopSetTracks/1.0 (+https://top-set-tracks.pages.dev)"}


def get_json(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  request failed: {url[:80]}... ({e}); retry {i + 1}/{tries}")
            time.sleep(6 * (i + 1))
    return None


def norm(s):
    s = re.sub(r"\(.*?\)|\[.*?\]", "", str(s or "").lower())
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def lead_artist(a):
    return re.split(r" ft\.| feat\.| featuring | & | x | and ", a, flags=re.I)[0].strip()


def itunes(track):
    lead = lead_artist(track["artist"])
    q = urllib.parse.urlencode({"term": f"{lead} {track['title']}", "media": "music",
                                "entity": "song", "limit": 25, "country": "CA"})
    data = get_json("https://itunes.apple.com/search?" + q) or {}
    want, who = norm(track["title"]), norm(lead)
    bad = re.compile(r"originally performed|made famous|in the style of|tribute|karaoke|cover|instrumental|lullaby|piano version|8.?bit", re.I)
    results = [r for r in data.get("results", [])
               if r.get("previewUrl")
               and not bad.search(f"{r.get('trackName','')} {r.get('collectionName','')} {r.get('artistName','')}")
               and (norm(r.get("artistName")) == who or norm(r.get("artistName")).startswith(who + " ") or norm(r.get("artistName")).startswith(who))]
    print(f"  itunes: {len(data.get('results', []))} results, {len(results)} by {lead}")
    def score(r):
        t, a = norm(r.get("trackName")), norm(r.get("artistName"))
        s = 0
        if t == want: s += 4
        elif t.startswith(want): s += 2
        if who and who in a: s += 3
        if "live" in t.split() and "live" not in want.split(): s -= 2
        if "remix" in t or "instrumental" in t or "karaoke" in t: s -= 3
        if track.get("year") and str(r.get("releaseDate", ""))[:4] == str(track["year"]): s += 1
        return s
    results.sort(key=score, reverse=True)
    if results and score(results[0]) >= 5:
        return results[0]
    return None


def songlink(apple_url):
    q = urllib.parse.urlencode({"url": apple_url, "userCountry": "CA"})
    data = get_json("https://api.song.link/v1-alpha.1/links?" + q, tries=1)
    if data is None:
        print("  song.link: no response")
        data = {}
    elif "linksByPlatform" not in data:
        print(f"  song.link: unexpected reply {str(data)[:200]}")
    p = data.get("linksByPlatform", {})
    return {
        "spotify": (p.get("spotify") or {}).get("url"),
        "youtube": (p.get("youtube") or p.get("youtubeMusic") or {}).get("url"),
        "songlink": data.get("pageUrl"),
    }


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    changed = False
    for t in data.get("tracks", []):
        links = t.setdefault("links", {})
        need_apple = not t.get("preview") or not links.get("apple")
        need_other = False  # song.link now requires a paid API key; Spotify/YouTube buttons use search
        if not (need_apple or need_other):
            continue
        print(f"- {t['title']} — {t['artist']}")
        apple_url = links.get("apple")
        if need_apple:
            hit = itunes(t)
            time.sleep(3)
            if hit:
                apple_url = apple_url or hit["trackViewUrl"].split("?uo=")[0].replace("&uo=4", "")
                if not links.get("apple"):
                    links["apple"] = apple_url; changed = True
                if not t.get("preview"):
                    t["preview"] = hit["previewUrl"]; changed = True
                if not t.get("artwork") and hit.get("artworkUrl100"):
                    t["artwork"] = hit["artworkUrl100"].replace("100x100bb", "600x600bb"); changed = True
                print(f"  apple: {apple_url}")
            else:
                print("  apple: no confident match, left blank")
        if apple_url and need_other:
            sl = songlink(apple_url)
            time.sleep(7)  # song.link allows ~10 requests a minute
            for k in ("spotify", "youtube"):
                if not links.get(k) and sl.get(k):
                    links[k] = sl[k]; changed = True
                    print(f"  {k}: {sl[k]}")
    if changed:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("tracks.json updated")
    else:
        print("nothing to fill")


if __name__ == "__main__":
    main()
