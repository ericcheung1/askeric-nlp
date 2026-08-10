from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTOptimizer
from optimum.onnxruntime.configuration import OptimizationConfig
from transformers import AutoTokenizer

# Script to convert Distilbert to .onnx

model_id = "distilbert-base-uncased-finetuned-sst-2-english"
save_dir = "./distilbert_fp16_onnx"

model = ORTModelForSequenceClassification.from_pretrained(model_id, export=True)

optimizer = ORTOptimizer.from_pretrained(model)

opt_config = OptimizationConfig(
    optimization_level=99, # Enables all fusions (LayerNorm, Attention, etc.)
    fp16=True             
)
tokenizer = AutoTokenizer.from_pretrained(model_id)

optimizer.optimize(save_dir=save_dir, optimization_config=opt_config)

# Save the exported model
model.save_pretrained(save_dir)
tokenizer.save_pretrained(save_dir)
