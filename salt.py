from datasets import get_dataset_config_names, get_dataset_split_names, load_dataset, Audio
import os
from scipy.io.wavfile import write
import numpy as np

DATASET_NAME = "Sunbird/salt"
BASE_DIR = "sunbird_salt_all"

os.makedirs(BASE_DIR, exist_ok=True)

# Get all configs
print("🔍 Fetching configs...")
configs = get_dataset_config_names(DATASET_NAME)
print(f"🧩 Found {len(configs)} configs: {configs}")

for config in configs:
    print(f"\n📥 Downloading config: {config}")
    try:
        # Get available splits (usually 'train', possibly 'validation', 'test')
        splits = get_dataset_split_names(DATASET_NAME, config)
    except Exception as e:
        print(f"❌ Could not get splits for config '{config}': {e}")
        continue

    for split in splits:
        print(f"  ➤ Loading split: {split}")
        try:
            dataset = load_dataset(DATASET_NAME, config, split=split)

            # Save Hugging Face dataset format
            split_dir = os.path.join(BASE_DIR, config.replace("-", "_"), split)
            os.makedirs(split_dir, exist_ok=True)
            dataset.save_to_disk(os.path.join(split_dir, "hf_dataset"))

            # If it has audio, save audio and text files
            if "audio" in dataset.column_names:
                print(f"    🎧 Saving audio and metadata...")

                # Cast to Audio
                dataset = dataset.cast_column("audio", Audio())
                audio_dir = os.path.join(split_dir, "audio")
                meta_path = os.path.join(split_dir, "metadata.tsv")
                os.makedirs(audio_dir, exist_ok=True)

                with open(meta_path, "w", encoding="utf-8") as meta_file:
                    meta_file.write("filename\ttranscription\n")
                    for i, example in enumerate(dataset):
                        audio = example["audio"]
                        text = example.get("transcription", "N/A")
                        filename = f"{i:06d}.wav"
                        filepath = os.path.join(audio_dir, filename)

                        # Save audio as 16-bit WAV
                        write(filepath, audio["sampling_rate"], np.int16(audio["array"] * 32767))

                        # Save transcription
                        meta_file.write(f"{filename}\t{text}\n")

                print(f"    ✅ Saved {len(dataset)} audio files and metadata.")
            else:
                print(f"    ⚠️ No audio in split '{split}', skipping audio export.")

        except Exception as e:
            print(f"    ❌ Failed to load split '{split}': {e}")
