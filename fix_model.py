import json
import os

# Path to your config file
config_path = "./lora_model/adapter_config.json"

print(f"Checking {config_path}...")

if os.path.exists(config_path):
    with open(config_path, "r") as f:
        data = json.load(f)
    
    # 1. REMOVE QUANTIZATION SETTINGS
    # This is the part that is demanding 'bitsandbytes'
    if "quantization_config" in data:
        print("Found GPU restriction (quantization_config). Removing it...")
        del data["quantization_config"]
        
    # 2. Save the "Clean" version
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)
        
    print("✅ SUCCESS! The model is now patched for CPU mode.")
    print("You can now run 'streamlit run app.py' again.")
else:
    print("❌ Error: Could not find './lora_model/adapter_config.json'.")
    print("Make sure you are running this script in the same folder as your 'lora_model' folder.")