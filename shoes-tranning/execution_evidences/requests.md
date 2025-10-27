# Evidencias execucao

## api

![api.png](api.png)

## app

![app.png](app.png)


## prompt

```
A professional product photo of black casual shoes on white background, high quality, product photography
```

## request base
```bash
curl -X 'POST' \
  'http://localhost:8011/api/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model_name": "lora_casual_shoes_3000steps_full/checkpoint-500",
  "prompt": "A professional product photo of black casual shoes on white background, high quality, product photography",
  "num_images": 1,
  "num_inference_steps": 50,
  "guidance_scale": 7.5,
  "seed": 0
}'

```


### model Stable Diffusion 1.5 (Base)

![base_20251027_141712_seed1035338254.png](base_20251027_141712_seed1035338254.png)

### model Stable Diffusion 1.5 (Base)
![lora_casual_shoes_3000steps_full_checkpoint-500_20251027_142558_seed3531931392.png](lora_casual_shoes_3000steps_full_checkpoint-500_20251027_142558_seed3531931392.png)

### Watermelon

![img.png](watermelon/img.png)

![lora_casual_shoes_3000steps_final_20251027_182402_seed2222329210.png](watermelon/lora_casual_shoes_3000steps_final_20251027_182402_seed2222329210.png)


![lora_casual_shoes_3000steps_final_20251027_182641_seed2222329215.png](watermelon/lora_casual_shoes_3000steps_final_20251027_182641_seed2222329215.png)