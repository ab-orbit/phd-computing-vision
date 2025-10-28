# Evidencias execucao
## Aula: 25/10/2025 (sábado)
## Registro primeira geracao: 27/10/2025 (segunda)
```
Steps:  49%|███████████████████████████████                                | 1234/2500 [4:46:52<4:58:36, 14.15s/it, epoch=13, loss=0.0702, lr=4.34e-5]
```

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

### 1000
![lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_221543_seed3894493778.png](black/lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_221543_seed3894493778.png)

![lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_221618_seed3894493779.png](black/lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_221618_seed3894493779.png)

### 1500

![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_221732_seed3898295219.png](black/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_221732_seed3898295219.png)

![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_221802_seed3898295220.png](black/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_221802_seed3898295220.png)




### Watermelon
```
A professional product photo of yellow casual shoes on watermelon background, high quality, product photography
```

![img.png](watermelon/img.png)

![lora_casual_shoes_3000steps_final_20251027_182402_seed2222329210.png](watermelon/lora_casual_shoes_3000steps_final_20251027_182402_seed2222329210.png)


![lora_casual_shoes_3000steps_final_20251027_182641_seed2222329215.png](watermelon/lora_casual_shoes_3000steps_final_20251027_182641_seed2222329215.png)

![lora_casual_shoes_3000steps_full_checkpoint-500_20251027_184041_seed2753453725.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-500_20251027_184041_seed2753453725.png)

![lora_casual_shoes_3000steps_full_checkpoint-500_20251027_184109_seed2753453726.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-500_20251027_184109_seed2753453726.png)

![lora_casual_shoes_3000steps_full_checkpoint-500_20251027_184136_seed2753453727.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-500_20251027_184136_seed2753453727.png)

### 1000
![lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222441_seed285875781.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222441_seed285875781.png)
![lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222510_seed285875782.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222510_seed285875782.png)
![lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222538_seed285875783.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222538_seed285875783.png)
![lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222606_seed285875784.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1000_20251027_222606_seed285875784.png)


### 1500

![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222048_seed3549761581.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222048_seed3549761581.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222116_seed3549761582.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222116_seed3549761582.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222142_seed3549761583.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222142_seed3549761583.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222209_seed3549761584.png](watermelon/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_222209_seed3549761584.png)


```
A professional product photo of gray casual shoes with white sole on white background, modern design, product photography
```
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224720_seed2784716826.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224720_seed2784716826.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224754_seed2784716827.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224754_seed2784716827.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224824_seed2784716828.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224824_seed2784716828.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224857_seed2784716829.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224857_seed2784716829.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224924_seed2784716830.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224924_seed2784716830.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224953_seed2784716831.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224953_seed2784716831.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225028_seed2784716832.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225028_seed2784716832.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225059_seed2784716833.png](grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225059_seed2784716833.png)



```
 A professional product photo of sculptural avant-garde heels inspired by organic shapes on white background, conceptual footwear, product photography
```
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225552_seed974209925.png](sculptural/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225552_seed974209925.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225618_seed974209926.png](sculptural/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225618_seed974209926.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225647_seed974209927.png](sculptural/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225647_seed974209927.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225720_seed974209928.png](sculptural/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225720_seed974209928.png)

NANO BANANA

![Gemini_Generated_Image_2ovqc82ovqc82ovq.png](sculptural/Gemini_Generated_Image_2ovqc82ovqc82ovq.png)

```
A professional product photo of brown leather casual oxford shoes on white background, classic design, product photography
```

![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230636_seed3101469424.png](brown_lether/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230636_seed3101469424.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230706_seed3101469425.png](brown_lether/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230706_seed3101469425.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230738_seed3101469426.png](brown_lether/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230738_seed3101469426.png)
![lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230811_seed3101469427.png](brown_lether/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230811_seed3101469427.png)

NANO BANANA

![Gemini_Generated_Image_ifcgxtifcgxtifcg.png](brown_lether/Gemini_Generated_Image_ifcgxtifcgxtifcg.png)
