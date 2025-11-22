"""Agent tools for travel planning."""
import json
import requests
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus


# Initialize database (will be set by agent)
_db_instance = None


def set_db_instance(db):
    """Set the database instance for tools to use."""
    global _db_instance
    _db_instance = db


class WebResourceInput(BaseModel):
    """Input schema for web_resource_tool."""
    url: str = Field(description="The URL of the web page to parse")
    extract_type: str = Field(
        default="general",
        description="Type of content to extract: 'general', 'reddit', 'booking', 'expedia'"
    )


class PlanInput(BaseModel):
    """Input schema for plan_tool."""
    action: str = Field(description="Action to perform: 'create', 'update', 'get', 'list'")
    plan_id: Optional[str] = Field(default=None, description="Plan ID for update/get operations")
    session_id: str = Field(description="Session ID")
    destination: Optional[str] = Field(default=None, description="Travel destination")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    plan_data: Optional[Dict] = Field(default=None, description="Plan data dictionary")


class MapRouteInput(BaseModel):
    """Input schema for map_route_tool."""
    plan_id: str = Field(description="Plan ID to generate route for")
    session_id: str = Field(description="Session ID")


class CommunityLinksInput(BaseModel):
    """Input schema for find_community_links_tool."""
    place_name: str = Field(description="Name of the tourist spot or place")
    city: Optional[str] = Field(default=None, description="City name (optional, helps with search)")
    country: Optional[str] = Field(default=None, description="Country name (optional)")


@tool("web_resource_tool", args_schema=WebResourceInput)
def web_resource_tool(url: str, extract_type: str = "general") -> str:
    """Parse travel content from public web pages (Reddit, Nextdoor, Expedia, Booking, blogs, etc.).
    
    Args:
        url: The URL of the web page to parse
        extract_type: Type of content to extract (general, reddit, booking, expedia)
        
    Returns:
        Extracted and formatted travel content as JSON string
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        extracted_data = {
            "url": url,
            "extract_type": extract_type,
            "title": "",
            "content": "",
            "metadata": {}
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            extracted_data["title"] = title_tag.get_text(strip=True)
        
        # Type-specific extraction
        if extract_type == "reddit":
            # Reddit-specific extraction
            post_content = soup.find('div', {'data-testid': 'post-content'})
            if not post_content:
                post_content = soup.find('div', class_=re.compile('Post'))
            if post_content:
                extracted_data["content"] = post_content.get_text(separator='\n', strip=True)
            
            # Extract comments
            comments = []
            comment_elements = soup.find_all('div', class_=re.compile('Comment'))
            for comment in comment_elements[:10]:  # Limit to 10 comments
                comment_text = comment.get_text(separator='\n', strip=True)
                if comment_text:
                    comments.append(comment_text)
            extracted_data["metadata"]["comments"] = comments
            
        elif extract_type in ["booking", "expedia"]:
            # Hotel/booking site extraction
            hotel_name = soup.find('h1') or soup.find('h2', class_=re.compile('hotel|property'))
            if hotel_name:
                extracted_data["title"] = hotel_name.get_text(strip=True)
            
            # Extract key information
            description = soup.find('div', class_=re.compile('description|overview'))
            if description:
                extracted_data["content"] = description.get_text(separator='\n', strip=True)
            
            # Extract amenities, ratings, etc.
            amenities = []
            amenity_elements = soup.find_all('div', class_=re.compile('amenity|feature'))
            for amenity in amenity_elements[:20]:
                amenity_text = amenity.get_text(strip=True)
                if amenity_text:
                    amenities.append(amenity_text)
            extracted_data["metadata"]["amenities"] = amenities
            
        else:
            # General extraction
            # Try to find main content
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_=re.compile('content|post|article'))
            )
            
            if main_content:
                extracted_data["content"] = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to body text
                body = soup.find('body')
                if body:
                    extracted_data["content"] = body.get_text(separator='\n', strip=True)
        
        # Clean up content (remove excessive whitespace)
        if extracted_data["content"]:
            lines = [line.strip() for line in extracted_data["content"].split('\n') if line.strip()]
            extracted_data["content"] = '\n'.join(lines[:500])  # Limit to 500 lines
        
        return json.dumps(extracted_data, indent=2)
        
    except requests.RequestException as e:
        return json.dumps({
            "error": f"Failed to fetch URL: {str(e)}",
            "url": url
        })
    except Exception as e:
        return json.dumps({
            "error": f"Error parsing content: {str(e)}",
            "url": url
        })


@tool("plan_tool", args_schema=PlanInput)
def plan_tool(
    action: str,
    session_id: str,
    plan_id: Optional[str] = None,
    destination: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    plan_data: Optional[Dict] = None
) -> str:
    """Create and update travel plans via chat.
    
    Args:
        action: Action to perform ('create', 'update', 'get', 'list')
        session_id: Session ID
        plan_id: Plan ID for update/get operations
        destination: Travel destination
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        plan_data: Plan data dictionary containing itinerary, activities, etc.
        
    Returns:
        JSON string with operation result
    """
    if not _db_instance:
        return json.dumps({"error": "Database not initialized"})
    
    try:
        if action == "create":
            if not destination or not start_date or not end_date or not plan_data:
                return json.dumps({
                    "error": "Missing required fields for create: destination, start_date, end_date, plan_data"
                })
            
            new_plan_id = plan_id or str(uuid.uuid4())
            success = _db_instance.save_travel_plan(
                plan_id=new_plan_id,
                session_id=session_id,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                plan_data=plan_data
            )
            
            if success:
                return json.dumps({
                    "success": True,
                    "action": "create",
                    "plan_id": new_plan_id,
                    "message": f"Travel plan created successfully for {destination}"
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": "Failed to create travel plan"
                })
        
        elif action == "update":
            if not plan_id:
                return json.dumps({"error": "plan_id required for update"})
            
            # Get existing plan
            existing = _db_instance.get_travel_plan(plan_id)
            if not existing:
                return json.dumps({"error": f"Plan {plan_id} not found"})
            
            # Merge updates
            updated_data = existing["plan_data"].copy()
            if plan_data:
                updated_data.update(plan_data)
            
            success = _db_instance.save_travel_plan(
                plan_id=plan_id,
                session_id=session_id,
                destination=destination or existing["destination"],
                start_date=start_date or existing["start_date"],
                end_date=end_date or existing["end_date"],
                plan_data=updated_data
            )
            
            if success:
                return json.dumps({
                    "success": True,
                    "action": "update",
                    "plan_id": plan_id,
                    "message": "Travel plan updated successfully"
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": "Failed to update travel plan"
                })
        
        elif action == "get":
            if not plan_id:
                return json.dumps({"error": "plan_id required for get"})
            
            plan = _db_instance.get_travel_plan(plan_id)
            if plan:
                return json.dumps({
                    "success": True,
                    "plan": plan
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Plan {plan_id} not found"
                })
        
        elif action == "list":
            plans = _db_instance.get_session_plans(session_id)
            return json.dumps({
                "success": True,
                "plans": plans,
                "count": len(plans)
            })
        
        else:
            return json.dumps({
                "error": f"Unknown action: {action}. Use 'create', 'update', 'get', or 'list'"
            })
    
    except Exception as e:
        return json.dumps({
            "error": f"Error in plan_tool: {str(e)}"
        })


@tool("map_route_tool", args_schema=MapRouteInput)
def map_route_tool(plan_id: str, session_id: str) -> str:
    """Generate map routes and per-day color labels for the frontend map.
    
    Args:
        plan_id: Plan ID to generate route for
        session_id: Session ID
        
    Returns:
        JSON string with route data including coordinates, waypoints, and per-day color labels
    """
    if not _db_instance:
        return json.dumps({"error": "Database not initialized"})
    
    try:
        plan = _db_instance.get_travel_plan(plan_id)
        if not plan:
            return json.dumps({"error": f"Plan {plan_id} not found"})
        
        plan_data = plan["plan_data"]
        itinerary = plan_data.get("itinerary", [])
        
        if not itinerary:
            return json.dumps({
                "error": "No itinerary found in plan",
                "plan_id": plan_id
            })
        
        # Color palette for different days
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", 
            "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2",
            "#F8B739", "#52BE80", "#EC7063", "#5DADE2"
        ]
        
        route_data = {
            "plan_id": plan_id,
            "destination": plan["destination"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"],
            "days": []
        }
        
        # Process each day in the itinerary
        for day_idx, day_item in enumerate(itinerary):
            day_num = day_idx + 1
            color = colors[day_idx % len(colors)]
            
            day_data = {
                "day": day_num,
                "date": day_item.get("date", ""),
                "color": color,
                "locations": [],
                "route": {
                    "waypoints": [],
                    "polyline": None  # Would be generated by a mapping service
                }
            }
            
            # Extract locations from activities
            activities = day_item.get("activities", [])
            for activity in activities:
                location = activity.get("location") or activity.get("place")
                if location:
                    # In a real implementation, you'd geocode these locations
                    # For now, we'll create placeholder coordinates
                    location_data = {
                        "name": location,
                        "address": activity.get("address", ""),
                        "coordinates": {
                            "lat": None,  # Would be geocoded
                            "lng": None   # Would be geocoded
                        },
                        "activity": activity.get("name", activity.get("description", "")),
                        "time": activity.get("time", "")
                    }
                    day_data["locations"].append(location_data)
                    day_data["route"]["waypoints"].append(location)
            
            route_data["days"].append(day_data)
        
        # Generate a simple route summary
        route_data["summary"] = {
            "total_days": len(route_data["days"]),
            "total_locations": sum(len(day["locations"]) for day in route_data["days"]),
            "route_type": "multi_day" if len(route_data["days"]) > 1 else "single_day"
        }
        
        return json.dumps(route_data, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": f"Error generating map route: {str(e)}"
        })


@tool("find_community_links_tool", args_schema=CommunityLinksInput)
def find_community_links_tool(place_name: str, city: Optional[str] = None, country: Optional[str] = None) -> str:
    """Find community links (Xiaohongshu, Reddit, Nextdoor) for a tourist spot.
    
    This tool constructs search URLs and finds relevant community discussions about a place.
    
    Args:
        place_name: Name of the tourist spot or place
        city: City name (optional, helps with search)
        country: Country name (optional)
        
    Returns:
        JSON string with community links and search URLs
    """
    try:
        # Construct search query
        search_query = place_name
        if city:
            search_query += f" {city}"
        if country:
            search_query += f" {country}"
        
        # URL encode the search terms
        encoded_query = quote_plus(search_query)
        encoded_place = quote_plus(place_name)
        encoded_city = quote_plus(city) if city else ""
        
        # Construct community links
        community_links = {
            "place_name": place_name,
            "city": city,
            "country": country,
            "search_query": search_query,
            "links": {
                "xiaohongshu": {
                    "search_url": f"https://www.xiaohongshu.com/search_result?keyword={encoded_query}",
                    "description": "Xiaohongshu (小红书) - Chinese social media platform with travel tips and photos",
                    "notes": "Search for travel guides, photos, and tips from Chinese users"
                },
                "reddit": {
                    "search_url": f"https://www.reddit.com/r/travel/search/?q={encoded_query}&restrict_sr=1",
                    "travel_subreddit": f"https://www.reddit.com/r/travel/search/?q={encoded_query}",
                    "city_subreddit": f"https://www.reddit.com/r/{encoded_city.lower().replace(' ', '')}/search/?q={encoded_place}" if city else None,
                    "description": "Reddit - Travel discussions and honest reviews",
                    "notes": "Search r/travel and city-specific subreddits for local insights"
                },
                "nextdoor": {
                    "search_url": f"https://nextdoor.com/search/?query={encoded_query}",
                    "description": "Nextdoor - Local neighborhood insights and practical tips",
                    "notes": "Find local recommendations, safety tips, and neighborhood updates"
                }
            },
            "recommended_searches": [
                f"{place_name} travel guide",
                f"{place_name} review",
                f"{place_name} tips" if city else f"{place_name} {city} tips",
                f"best time to visit {place_name}",
                f"{place_name} local recommendations"
            ]
        }
        
        # Add city-specific Reddit subreddit suggestions
        if city:
            city_variations = [
                city.lower().replace(' ', ''),
                city.lower().replace(' ', '_'),
                city.lower().replace(' ', '-')
            ]
            community_links["links"]["reddit"]["city_subreddits"] = [
                f"https://www.reddit.com/r/{var}/" for var in city_variations
            ]
        
        return json.dumps(community_links, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error finding community links: {str(e)}",
            "place_name": place_name
        })


