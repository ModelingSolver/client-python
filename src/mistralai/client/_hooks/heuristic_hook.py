import json
import httpx
# C'est ici que sont définies les interfaces réelles dans le SDK Mistral
from mistralai.client._hooks.sdkhooks import BeforeRequestHook
from mistralai.client._hooks.types import HookContext
from ...heuristics import HeuristicGuard

class HeuristicGuardHook(BeforeRequestHook):
    def before_request(self, hook_ctx: HookContext, request: httpx.Request) -> httpx.Request:
        if request.method == "POST" and "/chat/completions" in str(request.url):
            # Lecture sécurisée du corps
            body = json.loads(request.read())
            messages = body.get("messages", [])
            last_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
            
            # Ton filtre
            if not HeuristicGuard.analyze(last_msg)["valid"]:
                raise ValueError("Blocked by HeuristicGuard")
        return request