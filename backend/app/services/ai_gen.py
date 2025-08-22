import httpx
import base64
import asyncio
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

#Use the A1111 service name from docker-compose
A1111_URL = "http://a1111:7860/sdapi/v1/txt2img"

# Gemini AI Pro API URL and key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Get absolute project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp_images")

# Ensure folder exists
os.makedirs(TEMP_DIR, exist_ok=True)


async def generate_design_image(prompt: str, sampler: str = "Euler a") -> str:
    """
    Generate image from prompt using A1111 txt2img.
    Saves image temporarily inside project/temp_images, returns file path.
    The sampler can be specified (default: Euler a).
    """

    # Print the prompt being used
    print(f"[INFO] Prompt passed to model: {prompt}")
    print(f"[INFO] Using sampler: {sampler}")

    payload = {
        "prompt": prompt,
        "steps": 20,
        "width": 512,
        "height": 512,
        "cfg_scale": 9,
        "sampler_name": sampler
    }

    async with httpx.AsyncClient(timeout=720.0) as client:
        response = await client.post(A1111_URL, json=payload)
        response.raise_for_status()
        result = response.json()

    # Get the first image (base64 string) from response
    try:
        b64_image = result["images"][0]
        img_bytes = base64.b64decode(b64_image)
    except Exception as e:
        print(f"[ERROR] Failed to decode image from response: {e}")
        raise

    # Save as temp file
    file_name = f"{uuid.uuid4().hex}.png"
    file_path = os.path.join(TEMP_DIR, file_name)
    try:
        with open(file_path, "wb") as f:
            f.write(img_bytes)
    except Exception as e:
        print(f"[ERROR] Failed to save image: {e}")
        raise

    # Print saved path
    print(f"[INFO] Image saved at: {file_path}")

    return file_path


async def modify_prompt(prompt: str) -> str:
    # instructions = (
    #     "Always generate prompts for T-shirt designs using this exact format: "
    #     "[main subject], [style or mood], [shape if any], T shirt design, TShirtDesignAF. "
    #     "Never skip 'T shirt design, TshirtDesignAF' at the end, because they are trigger words "
    #     "for the LoRA and must always be included. Keep prompts short, clear, and focused "
    #     "on the subject + style + shape. "
    #     "For example: If the natural description is 'A cozy calm evening at the beach,' "
    #     "then the rewritten prompt should be: 'Beach, cozy, calm, circular, T shirt design, TShirtDesignAF'."
    # )

    instructions = (
        "Always generate prompts for T-shirt designs in keyword format only. "
        "Convert any descriptive input into short, atomic keywords — never full sentences. "
        "Do not remove or simplify details; every visual element in the description must be preserved as keywords. "
        "The structure must always end with: 'T shirt design, TShirtDesignAF'. "
        "If applicable, also include shapes (like circular, square, etc.) as keywords. "
        "For example: If the natural description is 'A magical floating island with a huge tree at its center. "
        "Glowing lanterns dangle from its branches, and soft clouds surround the island as tiny birds fly nearby. "
        "The dreamy and surreal design fits perfectly within a circular T-shirt layout,' "
        "then the rewritten prompt should be: "
        "'magical floating island, huge tree center, glowing lanterns, soft clouds, tiny birds flying, dreamy, surreal, circular layout, T shirt design, TShirtDesignAF'."
    )

    payload = {
        "contents": [{
            "parts": [{
                "text": f"{instructions}\nUser prompt: {prompt}"
            }]
        }]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()

    # Gemini responses nest text under candidates -> content -> parts
    try:
        modified_prompt = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        modified_prompt = prompt  # fallback

    return modified_prompt
