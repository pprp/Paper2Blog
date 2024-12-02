from PIL import Image
import io
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch

class VLMHandler:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load the model and processor
        self.model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        
        self.model.to(self.device)

    async def generate_caption(self, image_data: bytes) -> str:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Prepare image for the model
        pixel_values = self.feature_extractor(image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device)

        # Generate caption
        output_ids = self.model.generate(
            pixel_values,
            max_length=16,
            num_beams=4,
            return_dict_in_generate=True,
            early_stopping=True
        )

        # Decode the generated caption
        caption = self.tokenizer.decode(output_ids.sequences[0], skip_special_tokens=True)
        
        return caption
