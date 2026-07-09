"""
generator.py - CPU-Based LLM Generator for Sanskrit Document RAG System
=========================================================================
Wraps CPU-based LLM inference with two backends:
  - Backend A (Ollama): Connects to local Ollama server
  - Backend B (Transformers): Uses HuggingFace transformers directly
"""

import os
import json
import time
import urllib.request
import urllib.error


class Generator:
    """
    CPU-based text generator with Ollama and HuggingFace Transformers backends.
    """

    def __init__(self, backend="ollama", model_name=None):
        """
        Initialize the generator.

        Args:
            backend (str): 'ollama' or 'transformers'.
            model_name (str): Model name. Defaults to 'qwen2.5:0.5b' for Ollama
                              or 'Qwen/Qwen2.5-0.5B-Instruct' for Transformers.
        """
        self.active_backend = None
        self.ollama_url = "http://localhost:11434"
        self.model = None
        self.tokenizer = None

        if backend == "ollama":
            self.ollama_model = model_name or "qwen2.5:0.5b"
            if self._check_ollama():
                self.active_backend = "ollama"
                print(f"[Generator] Using Ollama backend with model: {self.ollama_model}")
            else:
                print("[Generator] Ollama not available. Falling back to transformers...")
                self._load_transformers(model_name)
        else:
            self._load_transformers(model_name)

    def _check_ollama(self):
        """Check if Ollama server is running and accessible."""
        try:
            req = urllib.request.Request(
                f"{self.ollama_url}/api/tags",
                headers={"User-Agent": "SanskritRAG/1.0"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                print(f"[Generator] Ollama available. Models: {models}")
                return True
        except Exception:
            return False

    def _load_transformers(self, model_name=None):
        """Load HuggingFace Transformers model on CPU."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            hf_model = model_name or "Qwen/Qwen2.5-0.5B-Instruct"
            print(f"[Generator] Loading HuggingFace model: {hf_model} (CPU)...")
            print("[Generator] This may take a few minutes on first run...")

            self.tokenizer = AutoTokenizer.from_pretrained(
                hf_model, trust_remote_code=True
            )

            # Use accelerate when available; otherwise, load the model and move it to CPU.
            try:
                import accelerate  # noqa: F401
                device_map = "cpu"
                print("[Generator] accelerate is available; using device_map='cpu'.")
            except ImportError:
                device_map = None
                print("[Generator] accelerate not installed; loading model normally on CPU.")

            load_kwargs = {
                "torch_dtype": torch.float32,
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }
            if device_map is not None:
                load_kwargs["device_map"] = device_map

            self.model = AutoModelForCausalLM.from_pretrained(
                hf_model,
                **load_kwargs,
            )

            if device_map is None:
                self.model.to("cpu")
            self.active_backend = "transformers"
            print(f"[Generator] Transformers model loaded successfully on CPU.")

        except ImportError:
            print("[Generator] ERROR: torch/transformers not installed.")
            print("  Install with: pip install torch transformers")
            self.active_backend = "none"
        except Exception as e:
            print(f"[Generator] ERROR loading model: {e}")
            self.active_backend = "none"

    def build_prompt(self, query, context_chunks):
        """
        Build a RAG prompt with retrieved context.

        Args:
            query (str): The user's question.
            context_chunks (list[dict]): Retrieved verse dictionaries.

        Returns:
            str: The complete prompt string.
        """
        system_msg = (
            "You are a knowledgeable scholar of Sanskrit texts, especially the "
            "Bhagavad Gita. Answer the user's question based on the provided context "
            "from the Gita verses. Include relevant Sanskrit verses and their meanings "
            "in your response. If the context doesn't contain enough information, "
            "say so honestly."
        )

        # Format context
        context_parts = []
        for i, verse in enumerate(context_chunks):
            ch = verse.get("chapter_number", "?")
            vn = verse.get("verse_number", "?")
            parts = [f"[Verse {i+1}: Chapter {ch}, Verse {vn}]"]
            if verse.get("text"):
                parts.append(f"Sanskrit: {verse['text']}")
            if verse.get("transliteration"):
                parts.append(f"Transliteration: {verse['transliteration']}")
            if verse.get("word_meanings"):
                parts.append(f"Word Meanings: {verse['word_meanings']}")
            if verse.get("english_translation"):
                parts.append(f"Translation: {verse['english_translation']}")
            context_parts.append("\n".join(parts))

        context_text = "\n\n".join(context_parts)

        prompt = (
            f"System: {system_msg}\n\n"
            f"Context from Bhagavad Gita:\n"
            f"{'='*50}\n"
            f"{context_text}\n"
            f"{'='*50}\n\n"
            f"User Question: {query}\n\n"
            f"Answer:"
        )
        return prompt

    def generate(self, prompt, max_tokens=512):
        """
        Generate text using the active backend.

        Args:
            prompt (str): The complete prompt.
            max_tokens (int): Maximum tokens to generate.

        Returns:
            dict: {response, backend, tokens_generated, generation_time_sec}
        """
        if self.active_backend == "ollama":
            return self._generate_ollama(prompt, max_tokens)
        elif self.active_backend == "transformers":
            return self._generate_transformers(prompt, max_tokens)
        else:
            return {
                "response": "[Error] No generation backend available. "
                            "Please install Ollama or run: pip install torch transformers",
                "backend": "none",
                "tokens_generated": 0,
                "generation_time_sec": 0.0,
            }

    def _generate_ollama(self, prompt, max_tokens=512):
        """Generate using Ollama API."""
        start = time.time()
        try:
            payload = json.dumps({
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 2048,
                    "temperature": 0.7,
                    "num_predict": max_tokens,
                },
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "SanskritRAG/1.0",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            elapsed = time.time() - start
            response_text = result.get("response", "").strip()
            # Estimate tokens from response length
            tokens_est = len(response_text.split())

            return {
                "response": response_text,
                "backend": "ollama",
                "tokens_generated": tokens_est,
                "generation_time_sec": round(elapsed, 2),
            }

        except Exception as e:
            elapsed = time.time() - start
            return {
                "response": f"[Ollama Error] {str(e)}",
                "backend": "ollama",
                "tokens_generated": 0,
                "generation_time_sec": round(elapsed, 2),
            }

    def _generate_transformers(self, prompt, max_tokens=512):
        """Generate using HuggingFace Transformers on CPU."""
        import torch

        start = time.time()
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1536)
            input_len = inputs["input_ids"].shape[1]

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            # Decode only newly generated tokens
            generated_ids = outputs[0][input_len:]
            response_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
            tokens_gen = len(generated_ids)
            elapsed = time.time() - start

            return {
                "response": response_text,
                "backend": "transformers",
                "tokens_generated": tokens_gen,
                "generation_time_sec": round(elapsed, 2),
            }

        except Exception as e:
            elapsed = time.time() - start
            return {
                "response": f"[Transformers Error] {str(e)}",
                "backend": "transformers",
                "tokens_generated": 0,
                "generation_time_sec": round(elapsed, 2),
            }


if __name__ == "__main__":
    print("=" * 60)
    print("Sanskrit Document RAG - Generator Test")
    print("=" * 60)

    gen = Generator(backend="ollama")
    print(f"\nActive backend: {gen.active_backend}")

    test_prompt = (
        "System: You are a Sanskrit scholar.\n\n"
        "Question: What is the meaning of dharma?\n\n"
        "Answer:"
    )

    print(f"\nGenerating response...")
    result = gen.generate(test_prompt, max_tokens=100)
    print(f"Backend: {result['backend']}")
    print(f"Time: {result['generation_time_sec']}s")
    print(f"Tokens: {result['tokens_generated']}")
    print(f"Response:\n{result['response']}")
