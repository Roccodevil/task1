import torch
from peft import PeftModel
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration


class LocalVLMProcessor:
    def __init__(self):
        self.base_model_id = "Qwen/Qwen2-VL-2B-Instruct"
        self.adapter_path = "models/custom_vlm_adapter"

        print("Loading local VLM processor and model into CPU...")
        self.processor = AutoProcessor.from_pretrained(self.base_model_id)

        self.base_model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.base_model_id,
            device_map="cpu",
            torch_dtype=torch.float32
        )

        self.model = PeftModel.from_pretrained(self.base_model, self.adapter_path)
        self.model.eval()

    def analyze_image(self, image_path, question="Extract all data points and relationships from this diagram."):
        """Processes a single image and returns the text description/data."""
        try:
            image = Image.open(image_path).convert("RGB")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": f"Analyze this chart and answer: {question}"}
                    ]
                }
            ]

            text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.processor(
                text=[text],
                images=[image],
                padding=True,
                return_tensors="pt"
            )

            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_new_tokens=256)

            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )

            return output_text[0]
        except Exception as e:
            return f"Error analyzing image {image_path}: {str(e)}"
