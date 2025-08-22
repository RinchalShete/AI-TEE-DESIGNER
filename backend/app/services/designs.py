from app.supabase_client import supabase

def save_design(user_id: str, front_img_url: str, back_img_url: str, color: str):
    response = supabase.table("designs").insert({
        "user_id": user_id,
        "front_img_url": front_img_url,
        "back_img_url": back_img_url,
        "color": color
    }).execute()

    if not response.data:
        raise Exception(f"Failed to save design. Response: {response}")

    return response.data

