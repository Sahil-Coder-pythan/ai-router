# ==============================================================================
# ALL SUPPORTED AI MODELS LIST (COMPLETE & UPDATED)
# ==============================================================================

SUPPORTED_MODELS = [
    # -------------------------------------------------------------
    # 1. CURRENT GOOGLE / GEMINI / GEMMA
    # -------------------------------------------------------------
    "gemini-3.8-flash",
    "gemini-3.8-live",
    "gemini-3.8-live-extended-thinking",
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-live-preview",
    "gemini-3.1-flash-tts-preview",
    "gemini-3.1-flash-image",
    "gemini-3-pro-image",
    "gemini-omni-1.1-flash",
    "gemini-3.5-transcribe",
    "gemini-3.5-transcribe-live",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash-image",
    "gemini-2.5-flash-native-audio-preview-12-2025",
    "gemini-2.5-flash-preview-tts",
    "gemini-2.5-pro-preview-tts",
    "gemini-embedding-001",
    "gemini-embedding-2-preview",
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",

    # -------------------------------------------------------------
    # 2. GOOGLE SPECIALIZED / AGENT / MEDIA
    # -------------------------------------------------------------
    "deep-research-preview-04-2026",
    "deep-research-max-preview-04-2026",
    "antigravity-preview-09-2026",
    "gemini-robotics-er-2-preview",
    "gemini-robotics-er-1.6-preview",
    "veo-3.1-generate-preview",
    "veo-3.1-lite-generate-preview",
    "lyria-3.5",
    "lyria-3-clip-preview",
    "lyria-3-pro-preview",
    "lyria-realtime-exp",

    # -------------------------------------------------------------
    # 3. OPENAI OPEN-WEIGHT & STANDARD
    # -------------------------------------------------------------
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-safeguard-20b",
    "gpt-oss-120b",
    "gpt-oss-20b",
    "gpt-4o",
    "gpt-4o-mini",
    "o1",
    "o1-mini",
    "o3-mini",
    "gpt-4-turbo",
    "gpt-3.5-turbo",

    # -------------------------------------------------------------
    # 4. GROQ CURRENT / PRODUCTION / PREVIEW
    # -------------------------------------------------------------
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "whisper-large-v3",
    "whisper-large-v3-turbo",
    "llama-prompt-guard-2-22m",
    "llama-prompt-guard-2-86m",
    "minimaxai/minimax-m2.7",
    "qwen/qwen3.8-27b",
    "canopylabs/orpheus-arabic-saudi",
    "canopylabs/orpheus-v1-english",

    # -------------------------------------------------------------
    # 5. META LLAMA 4 / NEWER FAMILIES
    # -------------------------------------------------------------
    "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
    "meta-llama/Llama-3.2-90B-Vision-Instruct",
    "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.2-1B-Instruct",
    "meta-llama/Llama-3.1-405B-Instruct",
    "meta-llama/Llama-3.1-70B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "meta-llama/Llama-Guard-3-8B",
    "meta-llama/Llama-Guard-3-11B-Vision",
    "meta-llama/Llama-Prompt-Guard-2-22M",
    "meta-llama/Llama-Prompt-Guard-2-86M",

    # -------------------------------------------------------------
    # 6. QWEN / ALIBABA
    # -------------------------------------------------------------
    "Qwen/Qwen3-235B-A22B",
    "Qwen/Qwen3-32B",
    "Qwen/Qwen3-30B-A3B",
    "Qwen/Qwen3-14B",
    "Qwen/Qwen3-8B",
    "Qwen/Qwen3-4B",
    "Qwen/Qwen3-1.7B",
    "Qwen/Qwen3-0.6B",
    "Qwen/Qwen3-Coder-480B-A35B-Instruct",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "Qwen/Qwen3-Coder-Next",
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "Qwen/Qwen2.5-14B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen2.5-Coder-14B-Instruct",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "Qwen/Qwen2.5-Coder-3B-Instruct",
    "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Qwen/Qwen2.5-VL-32B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-Omni-7B",
    "Qwen/QwQ-32B",

    # -------------------------------------------------------------
    # 7. DEEPSEEK
    # -------------------------------------------------------------
    "deepseek-ai/DeepSeek-R1",
    "deepseek-ai/DeepSeek-R1-0528",
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-V3-0324",
    "deepseek-ai/DeepSeek-V2.5",
    "deepseek-ai/DeepSeek-Coder-V2-Instruct",
    "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
    "deepseek-ai/DeepSeek-Coder-33B-Instruct",
    "deepseek-ai/DeepSeek-Math-7B-Instruct",
    "deepseek-ai/DeepSeek-VL2",
    "deepseek-ai/DeepSeek-VL2-Small",
    "deepseek-ai/DeepSeek-VL2-Tiny",
    "deepseek-chat",
    "deepseek-reasoner",

    # -------------------------------------------------------------
    # 8. MISTRAL / MIXTRAL / PIXTRAL
    # -------------------------------------------------------------
    "mistralai/Mistral-Large-Instruct-2411",
    "mistralai/Mistral-Small-24B-Instruct-2501",
    "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
    "mistralai/Mistral-Nemo-Instruct-2407",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "mistralai/Mixtral-8x22B-Instruct-v0.1",
    "mistralai/Codestral-22B-v0.1",
    "mistralai/Codestral-25.01",
    "mistralai/Pixtral-12B-2409",
    "mistralai/Pixtral-Large-Instruct-2411",
    "mistralai/Ministral-3-3B-Instruct",
    "mistralai/Ministral-3-8B-Instruct",
    "mistralai/Ministral-3-14B-Instruct",
    "mistralai/Devstral-Small-2505",
    "mistralai/Devstral-Small-2507",

    # -------------------------------------------------------------
    # 9. MICROSOFT PHI
    # -------------------------------------------------------------
    "microsoft/phi-4",
    "microsoft/Phi-4-mini-instruct",
    "microsoft/Phi-4-mini-reasoning",
    "microsoft/Phi-4-reasoning",
    "microsoft/Phi-4-multimodal-instruct",
    "microsoft/Phi-3.5-mini-instruct",
    "microsoft/Phi-3.5-MoE-instruct",
    "microsoft/Phi-3.5-vision-instruct",
    "microsoft/Phi-3-mini-4k-instruct",
    "microsoft/Phi-3-mini-128k-instruct",
    "microsoft/Phi-3-small-8k-instruct",
    "microsoft/Phi-3-small-128k-instruct",
    "microsoft/Phi-3-medium-4k-instruct",
    "microsoft/Phi-3-medium-128k-instruct",

    # -------------------------------------------------------------
    # 10. IBM GRANITE
    # -------------------------------------------------------------
    "ibm-granite/granite-4.2-30b",
    "ibm-granite/granite-4.2-8b",
    "ibm-granite/granite-4.2-3b",
    "ibm-granite/granite-4.0-h-small",
    "ibm-granite/granite-3.3-8b-instruct",
    "ibm-granite/granite-3.2-8b-instruct",
    "ibm-granite/granite-3.1-8b-instruct",
    "ibm-granite/granite-3.0-8b-instruct",
    "ibm-granite/granite-3.0-2b-instruct",
    "ibm-granite/granite-3.0-1b-a400m-instruct",
    "ibm-granite/granite-vision-3.2-2b",
    "ibm-granite/granite-embedding-30m-english",
    "ibm-granite/granite-embedding-278m-multilingual",

    # -------------------------------------------------------------
    # 11. NVIDIA NEMOTRON
    # -------------------------------------------------------------
    "nvidia/NVIDIA-Nemotron-4-340B-Instruct",
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
    "nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16",
    "nvidia/Llama-3.1-Nemotron-Ultra-253B-v1",
    "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
    "nvidia/Llama-3.1-Nemotron-Nano-8B-v1",
    "nvidia/Llama-3.1-Nemotron-Nano-VL-8B-V1",
    "nvidia/NVIDIA-Nemotron-4-Mini-Hindi-4B",

    # -------------------------------------------------------------
    # 12. COHERE
    # -------------------------------------------------------------
    "CohereForAI/aya-expanse-32b",
    "CohereForAI/aya-expanse-8b",
    "CohereForAI/c4ai-command-r7b-12-2024",
    "CohereForAI/c4ai-command-r-plus",
    "CohereForAI/c4ai-command-r-v01",
    "command-r-plus",
    "command-r",
    "command-r7b-12-2024",
    "embed-english-v3.0",
    "embed-multilingual-v3.0",
    "rerank-english-v3.0",
    "rerank-multilingual-v3.0",

    # -------------------------------------------------------------
    # 13. HUGGING FACE / OPEN SOURCE FAMILIES
    # -------------------------------------------------------------
    "tiiuae/Falcon3-1B-Instruct",
    "tiiuae/Falcon3-3B-Instruct",
    "tiiuae/Falcon3-7B-Instruct",
    "tiiuae/Falcon3-10B-Instruct",
    "tiiuae/falcon-180B-chat",
    "tiiuae/falcon-40b-instruct",
    "tiiuae/falcon-7b-instruct",
    "bigscience/bloom-560m",
    "bigscience/bloom-1b7",
    "bigscience/bloom-3b",
    "bigscience/bloom-7b1",
    "bigcode/starcoder",
    "bigcode/starcoder2-3b",
    "bigcode/starcoder2-7b",
    "bigcode/starcoder2-15b",
    "EleutherAI/pythia-160m",
    "EleutherAI/pythia-410m",
    "EleutherAI/pythia-1b",
    "EleutherAI/pythia-2.8b",
    "EleutherAI/pythia-6.9b",
    "EleutherAI/pythia-12b",
    "mosaicml/mpt-7b-instruct",
    "mosaicml/mpt-30b-instruct",
    "databricks/dbrx-instruct",
    "01-ai/Yi-6B-Chat",
    "01-ai/Yi-34B-Chat",
    "01-ai/Yi-1.5-6B-Chat",
    "01-ai/Yi-1.5-9B-Chat",
    "01-ai/Yi-1.5-34B-Chat",
    "baichuan-inc/Baichuan2-7B-Chat",
    "baichuan-inc/Baichuan2-13B-Chat",
    "THUDM/chatglm3-6b",
    "THUDM/GLM-4-9B-Chat",
    "THUDM/GLM-4-9B-Chat-1M",
    "internlm/internlm2.5-7b-chat",
    "internlm/internlm2.5-20b-chat",
    "internlm/internlm3-8b-instruct",
    "allenai/OLMo-7B-Instruct",
    "allenai/OLMo-2-1124-7B-Instruct",
    "allenai/OLMo-2-0325-32B-Instruct",
    "allenai/OLMoE-1B-7B-0924",

    # -------------------------------------------------------------
    # 14. MULTIMODAL / VISION / SMALL / AUDIO / SAFETY
    # -------------------------------------------------------------
    "google/gemma-3-27b-it",
    "google/gemma-3-12b-it",
    "google/gemma-3-4b-it",
    "google/gemma-3-1b-it",
    "llava-hf/llava-v1.6-mistral-7b-hf",
    "llava-hf/llava-v1.6-vicuna-13b-hf",
    "HuggingFaceM4/idefics2-8b",
    "HuggingFaceM4/Idefics3-8B-Llama3",
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
    "mistral-embed",
    "amazon.titan-embed-text-v2:0",
    "cohere-embed-v4.0",
    "whisper-1",
    "openai/whisper-large-v3",
    "openai/whisper-large-v3-turbo"
]


def is_model_supported(model_name: str) -> bool:
    """
    चेक करता है कि मॉडल लिस्ट में है या नहीं।
    साथ ही Prefix Match चेक करता है ताकि भविष्य के वर्जन्स अपने आप पास हों।
    """
    if not model_name:
        return False

    clean_model = model_name.strip().lower()

    # Exact Match Check
    for m in SUPPORTED_MODELS:
        if m.lower() == clean_model:
            return True

    # Prefix Check — covers almost every major company model family
    common_prefixes = [
        "gpt-", "o1-", "o3-", "o4-", "chatgpt-", 
        "gemini-", "gemma-", 
        "llama-", "meta-llama/", "meta/",
        "claude-", "anthropic/",
        "deepseek", "deepseek-",
        "mistral", "mixtral", "codestral", "pixtral", "ministral", "devstral",
        "qwen", "qwen2", "qwen3", "qwq-",
        "phi-", "microsoft/",
        "granite", "ibm-",
        "openai/", "whisper", 
        "command-", "command-r", "aya-", "cohere",
        "grok-", "xai/",
        "sonar-", "perplexity",
        "yi-", "01-ai/",
        "falcon", "bloom", "starcoder", "pythia", "mpt-", "dbrx",
        "baichuan", "chatglm", "glm-", "internlm", "olmo",
        "nemotron", "nvidia/",
        "minimax", "moonshot", "kimi", "reka-", "step-",
        "veo-", "lyria-", "imagen-",
    ]
    for prefix in common_prefixes:
        if clean_model.startswith(prefix):
            return True

    return False
