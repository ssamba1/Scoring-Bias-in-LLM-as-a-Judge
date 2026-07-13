#!/usr/bin/env python3
"""API key management system. Loads keys from environment variables or .env file."""
import os, sys
from pathlib import Path

class APIKeyManager:
    """Manages API keys for all judge models."""
    
    REQUIRED_KEYS = {
        "claude": "ANTHROPIC_API_KEY",
        "gpt4o": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "llama": "TOGETHER_API_KEY",
    }
    
    # Alternative env var names to try
    ALT_NAMES = {
        "ANTHROPIC_API_KEY": ["CLAUDE_API_KEY", "ANTHROPIC_KEY"],
        "OPENAI_API_KEY": ["OPENAI_KEY", "GPT_KEY"],
        "GEMINI_API_KEY": ["GOOGLE_API_KEY", "PALM_API_KEY"],
        "DEEPSEEK_API_KEY": ["DEEPSEEK_KEY"],
        "TOGETHER_API_KEY": ["TOGETHER_KEY"],
    }
    
    def __init__(self, env_file=None):
        self.keys = {}
        self.load_env_file(env_file)
        self.load_environment()
    
    def load_env_file(self, path=None):
        """Load .env file if it exists."""
        if path is None:
            path = Path(__file__).parent.parent / ".env"
        
        path = Path(path)
        if not path.exists():
            return
        
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip("'").strip('"')
    
    def load_environment(self):
        """Load keys from environment variables."""
        for short_name, env_var in self.REQUIRED_KEYS.items():
            # Try primary env var
            value = os.environ.get(env_var)
            
            # Try alternatives
            if not value and env_var in self.ALT_NAMES:
                for alt in self.ALT_NAMES[env_var]:
                    value = os.environ.get(alt)
                    if value:
                        break
            
            if value:
                self.keys[short_name] = value
    
    def get(self, judge_name):
        """Get API key for a judge model."""
        return self.keys.get(judge_name)
    
    def check_all(self):
        """Check which keys are available."""
        status = {}
        for name, env_var in self.REQUIRED_KEYS.items():
            status[name] = {
                "available": name in self.keys,
                "env_var": env_var,
                "key_preview": f"...{self.keys[name][-4:]}" if name in self.keys else None,
            }
        return status
    
    def print_status(self):
        """Print key availability."""
        print("="*50)
        print("API Key Status")
        print("="*50)
        for name, info in self.check_all().items():
            if info["available"]:
                print(f"  ✓ {name:<12} {info['env_var']:<20} ...{info['key_preview']}")
            else:
                print(f"  ✗ {name:<12} {info['env_var']:<20} NOT SET")
        
        missing = [n for n, i in self.check_all().items() if not i["available"]]
        if missing:
            print(f"\n  Missing keys for: {', '.join(missing)}")
            print(f"  Set environment variables or create a .env file")
        else:
            print(f"\n  ✓ ALL KEYS AVAILABLE")

def main():
    manager = APIKeyManager()
    manager.print_status()

if __name__ == "__main__":
    main()
