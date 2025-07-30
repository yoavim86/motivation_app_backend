from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth.firebase import verify_firebase_token
from app.core import get_spotify_client_id, get_spotify_client_secret
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging

router = APIRouter()

# Fallback track to return when Spotify search fails or returns no results
FALLBACK_TRACK = {
    "name": "Weightless",
    "artists": ["Marconi Union"],
    "album": "Weightless",
    "album_art": "https://i.scdn.co/image/ab67616d0000b2738b3dbf6e41eecbeecf9fbb99",
    "track_id": "4pbJqGIASGPr0ZpGpnWkDn",
    "spotify_url": "https://open.spotify.com/track/4pbJqGIASGPr0ZpGpnWkDn",
    "preview_url": None,
    "duration_ms": 480800
}

def get_spotify_track_info(track_name: str, artist_name: str, market: str = "US") -> dict | None:
    """
    Search Spotify for the given track and artist, return a JSON object
    for the top match (limit=1), including its full Spotify URL.
    """
    client_id = get_spotify_client_id()
    client_secret = get_spotify_client_secret()
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Spotify credentials not configured. Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET env variables")

    try:
        # Create Spotify client
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        ))

        # Use filters for more accurate match: note the space between tags
        q = f'track:{track_name} artist:{artist_name}'
        results = sp.search(q=q, type="track", market=market, limit=1)
        items = results.get("tracks", {}).get("items", [])
        
        if not items:
            return None

        track = items[0]
        return {
            "name": track["name"],
            "artists": [artist["name"] for artist in track["artists"]],
            "album": track["album"]["name"],
            "album_art": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            "track_id": track["id"],
            "spotify_url": track["external_urls"]["spotify"],
            "preview_url": track.get("preview_url"),
            "duration_ms": track.get("duration_ms")
        }
    except Exception as e:
        logging.error(f"Error searching Spotify: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search Spotify: {str(e)}")

@router.get("/spotify/track")
async def spotify_song(
    song_name: str = Query(..., description="The name of the song to search for"),
    artist_name: str = Query(..., description="The name of the artist"),
    market: str = Query("US", description="The market (country code) for the search"),
    user=Depends(verify_firebase_token)
):
    """
    Search for a song on Spotify and return track information.
    
    This endpoint searches Spotify for a track using the provided song name and artist name.
    If the track is found, it returns structured track information.
    If no track is found or if the Spotify API fails, it returns a fallback track.
    """
    try:
        # Search for the track
        track_info = get_spotify_track_info(song_name, artist_name, market)
        
        if track_info:
            logging.info(f"Found Spotify track: {track_info['name']} by {', '.join(track_info['artists'])}")
            return {
                "success": True,
                "track": track_info
            }
        else:
            # No tracks found, return fallback
            logging.info(f"No Spotify tracks found for query: track:{song_name} artist:{artist_name}")
            return {
                "success": True,
                "fallback_used": True,
                "track": FALLBACK_TRACK,
                "message": "No tracks found for the given search criteria"
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions (like auth failures)
        raise
    except Exception as e:
        # Unexpected error, return fallback
        logging.error(f"Unexpected error in Spotify search: {e}")
        return {
            "success": True,
            "fallback_used": True,
            "track": FALLBACK_TRACK,
            "error": {
                "message": f"Unexpected error: {str(e)}"
            }
        } 