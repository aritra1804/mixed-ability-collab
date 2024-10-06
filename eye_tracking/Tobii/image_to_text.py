import requests
from PIL import Image
# import logging
import warnings
# from transformers import logging as hf_logging

# hf_logging.set_verbosity_error()
warnings.filterwarnings("ignore")

from transformers import BlipProcessor, BlipForConditionalGeneration



def caption_image(image_path=None, img_url=None, caption_text="a photography of "):


    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large",cache_dir="./model_cache")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large",cache_dir="./model_cache")

    img_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg' 
    #raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')
    raw_image = Image.open(image_path)

    # a photography of a woman in a hat and a blue shirt
    #a close up of a person ' s profile on a resume

    # conditional image captioning
    text = caption_text
    inputs = processor(raw_image, text, return_tensors="pt")

    out = model.generate(**inputs)
    print(processor.decode(out[0], skip_special_tokens=True))

    # unconditional image captioning
    inputs = processor(raw_image, return_tensors="pt")

    out = model.generate(**inputs)
    print(processor.decode(out[0], skip_special_tokens=True))


