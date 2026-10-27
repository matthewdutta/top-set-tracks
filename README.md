# Top Set Tracks

One song a day for your hardest sets.

## How it works
- `index.html`: the whole site (design, player, archive).
- `tracks.json`: the song catalog. **This is the only file that changes day to day.**
- `manifest.webmanifest`, `sw.js`, `icons/`: make the site installable as a home-screen app.

Each track has a `date` (YYYY-MM-DD). The newest track whose date is today or earlier
is the Top Set Track of the Day; older ones appear in The Rack. Tracks with future
dates go live automatically at midnight in each visitor's time zone.

Moods: `Good Vibes`, `Lock-In Mode`, `Aggressive`, `Warm-Up Builder`.

## Track format
```json
{
  "id": "t001",
  "date": "2026-10-27",
  "title": "Song title",
  "artist": "Artist",
  "year": 2002,
  "genre": "Hip-hop",
  "mood": "Aggressive",
  "tagline": "Short caption.",
  "description": "Why it's today's pick.",
  "links": {
    "spotify": "https://open.spotify.com/track/...",
    "apple": "https://music.apple.com/...",
    "youtube": "https://www.youtube.com/watch?v=..."
  }
}
```

## Writing style
- Taglines: short, plain and direct. Not corny, no puns. Example: "Good vibes to keep the lift fun."
- Descriptions: one or two plain sentences on what the song sounds like and when to play it in a session.

## Links
The "Fill in song links" GitHub Action adds the exact Apple Music link and 30-second preview
for each new track. Spotify and YouTube buttons open a search for the song unless an exact
link is added to `links.spotify` / `links.youtube` by hand.
