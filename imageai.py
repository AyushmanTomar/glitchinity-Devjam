from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image

model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

model.eval()

def load_image(image_path):
    image = Image.open(image_path).convert("RGB")
    return image

def preprocess_image(image):
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
    return pixel_values


def generate_caption(image_path):
    image = load_image(image_path)
    pixel_values = preprocess_image(image)
    with torch.no_grad():
        generated_ids = model.generate(pixel_values, max_length=16, num_beams=4, return_dict_in_generate=True).sequences
    caption = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return caption

def get_caption(path):
    image_path = path
    caption = generate_caption(image_path)
    return caption