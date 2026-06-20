import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from unittest.mock import MagicMock
from mistralai.client._hooks.heuristic_hook import HeuristicGuardHook
from mistralai.client._hooks import HookContext

def test_heuristic_block_empty_prompt():
    # 1. On simule le contexte
    mock_ctx = MagicMock(spec=HookContext)
    
    # 2. On simule la requête HTTP
    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.url = "https://api.mistral.ai/v1/chat/completions"
    
    # Simule un corps de message vide
    mock_request.read.return_value = b'{"messages": [{"role": "user", "content": ""}]}'
    
    # 3. Test du hook
    hook = HeuristicGuardHook()
    
    try:
        hook.before_request(mock_ctx, mock_request)
        print("❌ TEST ÉCHOUÉ : Le prompt vide n'a pas été bloqué.")
    except ValueError as e:
        print(f"✅ TEST RÉUSSI : Le prompt a bien été bloqué -> {e}")

if __name__ == "__main__":
    test_heuristic_block_empty_prompt()