# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from app.services import ai_gen, designs
# from app.utils import storage
# from app.api.auth import get_current_user
# import clip
# import torch
# from PIL import Image

# router = APIRouter()

# class DesignRequest(BaseModel):
#     prompt_type_front: str  # 'template', 'modified_template', 'written_prompt'
#     prompt_front: str
#     prompt_type_back: str
#     prompt_back: str
#     color: str

# LORA_TAG = "<lora:TShirtDesignRedmond1-5V:0.8>"

# # Load CLIP once (outside the endpoint) for efficiency
# device = "cpu"  # or "cuda" if GPU is available
# clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

# @router.post("/generate-design")
# async def generate_design(data: DesignRequest, current_user: dict = Depends(get_current_user)):
#     try:
#         # ---------------- FRONT PROMPT ----------------
#         if data.prompt_type_front in ["template", "modified_template"]:
#             front_final_prompt = data.prompt_front
#         else:  # written_prompt
#             front_final_prompt = await ai_gen.modify_prompt(data.prompt_front)

#         # Append LoRA tag
#         front_final_prompt += f" {LORA_TAG}"

#         # Generate front image and print info
#         front_path = await ai_gen.generate_design_image(front_final_prompt, sampler="Euler a")

#         # ---------------- BACK PROMPT ----------------
#         if data.prompt_type_back in ["template", "modified_template"]:
#             back_final_prompt = data.prompt_back
#         else:  # written_prompt
#             back_final_prompt = await ai_gen.modify_prompt(data.prompt_back)

#         # Append LoRA tag
#         back_final_prompt += f" {LORA_TAG}"

#         # Generate back image and print info
#         back_path = await ai_gen.generate_design_image(back_final_prompt, sampler="Euler a")

#         # ---------------- CLIP SCORE LOGGING ----------------
#         def log_clip_score(image_path: str, prompt: str, side: str):
#             image = Image.open(image_path)
#             image_input = clip_preprocess(image).unsqueeze(0).to(device)
#             text_input = clip.tokenize([prompt]).to(device)
#             with torch.no_grad():
#                 image_features = clip_model.encode_image(image_input)
#                 text_features = clip_model.encode_text(text_input)
#                 image_features /= image_features.norm(dim=-1, keepdim=True)
#                 text_features /= text_features.norm(dim=-1, keepdim=True)
#                 similarity = (image_features @ text_features.T).item()
#             return similarity

#         front_clip = log_clip_score(front_path, front_final_prompt, "front")
#         back_clip = log_clip_score(back_path, back_final_prompt, "back")

#         # ---------------- UPLOAD TO CLOUD ----------------
#         front_url = storage.upload_image_to_cloudinary(front_path)
#         back_url = storage.upload_image_to_cloudinary(back_path)

#         # ---------------- SAVE DESIGN ----------------
#         designs.save_design(current_user["sub"], front_url, back_url, data.color)

#         return {
#             "front_design_url": front_url,
#             "back_design_url": back_url,
#             "color": data.color,
#             "front_clip_score": front_clip,
#             "back_clip_score": back_clip,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

















from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services import ai_gen, designs
from app.utils import storage
from app.api.auth import get_current_user
import clip
import torch
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

BLANK_URL = os.getenv("BLANK_URL")  # Fetch BLANK_URL from .env

router = APIRouter()

class DesignRequest(BaseModel):
    prompt_type_front: str  # 'template', 'modified_template', 'written_prompt'
    prompt_front: str
    prompt_type_back: str
    prompt_back: str
    color: str

LORA_TAG = "<lora:TShirtDesignRedmond1-5V:0.8>"

# Flags to check if front/back should be generated
front_NoDesign = False
back_NoDesign = False

# Load CLIP once (outside the endpoint) for efficiency
device = "cpu"  # or "cuda" if GPU is available
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

def is_design(prompt: str) -> bool:
    return prompt == "None"

@router.post("/generate-design")
async def generate_design(data: DesignRequest, current_user: dict = Depends(get_current_user)):
    global front_NoDesign, back_NoDesign
    try:
        front_path = None
        back_path = None
        front_final_prompt = None
        back_final_prompt = None
        front_clip = None
        back_clip = None
        front_url = BLANK_URL
        back_url = BLANK_URL
        # ---------------- FRONT PROMPT ----------------
        front_NoDesign = is_design(data.prompt_front)
        if not front_NoDesign:
            if data.prompt_type_front in ["template", "modified_template"]:
                front_final_prompt = data.prompt_front
            else:  # written_prompt
                front_final_prompt = await ai_gen.modify_prompt(data.prompt_front)

            # Append LoRA tag
            front_final_prompt += f" {LORA_TAG}"

            # Generate front image
            front_path = await ai_gen.generate_design_image(front_final_prompt, sampler="Euler a")
        else:
            front_url = BLANK_URL  # placeholder from .env

        # ---------------- BACK PROMPT ----------------
        back_NoDesign = is_design(data.prompt_back)
        if not back_NoDesign:
            if data.prompt_type_back in ["template", "modified_template"]:
                back_final_prompt = data.prompt_back
            else:  # written_prompt
                back_final_prompt = await ai_gen.modify_prompt(data.prompt_back)

            # Append LoRA tag
            back_final_prompt += f" {LORA_TAG}"

            # Generate back image
            back_path = await ai_gen.generate_design_image(back_final_prompt, sampler="Euler a")
        else:
            back_url = BLANK_URL  # placeholder from .env

        # ---------------- CLIP SCORE LOGGING ----------------
        def log_clip_score(image_path: str, prompt: str, side: str):
            image = Image.open(image_path)
            image_input = clip_preprocess(image).unsqueeze(0).to(device)
            text_input = clip.tokenize([prompt]).to(device)
            with torch.no_grad():
                image_features = clip_model.encode_image(image_input)
                text_features = clip_model.encode_text(text_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                similarity = (image_features @ text_features.T).item()
            return similarity

        front_clip = log_clip_score(front_path, front_final_prompt, "front") if not front_NoDesign else None
        back_clip = log_clip_score(back_path, back_final_prompt, "back") if not back_NoDesign else None

        # ---------------- UPLOAD TO CLOUD ----------------
        if not front_NoDesign:
            front_url = storage.upload_image_to_cloudinary(front_path)
        if not back_NoDesign:
            back_url = storage.upload_image_to_cloudinary(back_path)

        # ---------------- SAVE DESIGN ----------------
        designs.save_design(current_user["sub"], front_url, back_url, data.color)

        return {
            "front_design_url": front_url,
            "back_design_url": back_url,
            "color": data.color,
            "front_clip_score": front_clip,
            "back_clip_score": back_clip,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
