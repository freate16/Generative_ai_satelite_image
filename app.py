import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import streamlit as st
import torch
from diffusers import StableDiffusionPipeline, AutoencoderKL, DPMSolverMultistepScheduler

# --- CONFIGURATION ---
model_id = "models/DreamShaper_8_pruned.safetensors"
VAE_PATH = "models/vae-ft-mse-840000-ema-pruned.safetensors"
LORA_PATH = "models/sat-art-generator-10.safetensors" 
TRIGGER_WORD = "satartstyle"
DEFAULT_NEGATIVE_PROMPT = "ugly, tiling, poorly drawn, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted"

# --- MODEL LOADING ---
@st.cache_resource
def load_model():
    print("Loading all components...")
    
    vae = AutoencoderKL.from_single_file(VAE_PATH, torch_dtype=torch.float16)
    
    pipe = StableDiffusionPipeline.from_single_file(
        model_id, 
        vae=vae,
        torch_dtype=torch.float16,
        safety_checker=None, # Disables the safety checker
        requires_safety_checker=False
    )
    
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
    
    pipe.load_lora_weights(LORA_PATH, adapter_name="satart") # Give the LoRA an adapter name
    pipe.to("cuda")
    print("All components loaded successfully.")
    return pipe

# --- USER INTERFACE ---
st.set_page_config(layout="wide")
st.title("🛰️ Satellite Art Generator")
pipe = load_model()

with st.sidebar:
    st.header("Generation Settings")
    lora_strength = st.slider("LoRA Strength:", 0.0, 2.0, 1.0, 0.1)
    num_images = st.slider("Number of images to generate:", 1, 4, 1)
    guidance_scale = st.slider("CFG Scale (Prompt Adherence):", 1.0, 20.0, 7.5, 0.5)
    num_inference_steps = st.slider("Sampling Steps:", 10, 100, 25, 1)

st.header("Enter Your Prompt")
prompt = st.text_area("Prompt:", height=100, placeholder="e.g., a majestic, abstract view of a river delta")
negative_prompt = st.text_area("Negative Prompt:", height=50, value=DEFAULT_NEGATIVE_PROMPT)

if st.button("Generate Image", use_container_width=True):
    if not prompt:
        st.warning("Please enter a prompt to generate an image.")
    else:
        with st.spinner("Generating your satellite art..."):
            
            # Set the LoRA adapter and its strength
            pipe.set_adapters(["satart"], adapter_weights=[lora_strength])
            
            full_prompt = f"{prompt}, {TRIGGER_WORD}"

            generated_images = pipe(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                num_images_per_prompt=num_images,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                width = 768,
                height = 768,
            ).images
            
            # It's good practice to disable adapters when done
            #pipe.disable_lora()
            
            st.header("Your Generated Images")
            cols = st.columns(num_images)
            for i, image in enumerate(generated_images):
                with cols[i]:
                    st.image(image, use_column_width=True)