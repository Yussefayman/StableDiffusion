#Requriement setup
#!pip install diffusers transformers huggingface_hub gradio
from huggingface_hub import login
from diffusers import DiffusionPipeline
import torch

login()

pipe = DiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, use_safetensors=True
)
pipe = pipe.to("cuda")
scheduler_names = [scheduler.__name__ for scheduler in pipe.scheduler.compatibles]
scheduler_hashmap = {scheduler.__name__:scheduler for scheduler in pipe.scheduler.compatibles}

def import_scheduler(scheduler_name):
  library_name = "diffusers"
  class_name = scheduler_name

  try:
      module = __import__(library_name, fromlist=[class_name])
      imported_class = getattr(module, class_name)
      print(f"Successfully imported {class_name} from {library_name}")
  except ImportError:
      print(f"Failed to import {class_name} from {library_name}")

def inference(prompt="write something first",negative_prompt="",scheduler_name='KDPM2AncestralDiscreteScheduler', num_inf_steps=50, guidance_scale=7.5):
  global pipe
  import_scheduler(scheduler_name)
  pipe.scheduler = scheduler_hashmap[scheduler_name].from_config(pipe.scheduler.config)
  pipe = pipe.to("cuda") if torch.cuda.is_available() else pipe.to("cpu")
  return pipe(prompt = prompt , negative_prompt = negative_prompt,num_inference_steps = num_inf_steps,  guidance_scale= guidance_scale).images[0]


interface = gr.Interface(
    fn=inference,
    inputs=[
        gr.inputs.Textbox(label="Enter a Prompt",default= "astroboy 3D, High definition"),
        gr.inputs.Textbox(label="Enter a Negative Prompt",default = 'High saturation'),
        gr.Dropdown(
            scheduler_names, label="Schedulers",value = 'KDPM2AncestralDiscreteScheduler'
        ),
        gr.Slider(1, 100, value=50,step = 1, label="Sampling Steps"),
        gr.Slider(1, 15, value=7.5, label="Guidance Scale")
    ],
    outputs='image',
    allow_flagging = 'never'
)

interface.launch()



