import re

class HeuristicGuard:
    """
    Filtre heuristique pour requêtes LLM.
    Calcule le score S_Ω pour valider la structure avant inférence.
    """
    
    OPERANTS = {'donne', 'fais', 'analyse', 'génère', 'genere', 'calcule', 
                'audit', 'verdict', 'système', 'crée', 'cree', 'optimise', 
                'explique', 'compare', 'résume', 'resume', 'évalue', 'evalue', 
                'teste', 'montre', 'prouve', 'liste', 'décris', 'decris', 'generate'}
    
    FORMATS = {'json', 'tableau', 'liste', 'markdown', 'csv', 'expert', 
               'physique', 'code', 'python', 'sql'}

    THRESH_OPTIMAL = 2.3
    THRESH_ADMISSIBLE = 1.0

    @classmethod
    def analyze(cls, prompt: str) -> dict:
        prompt = prompt.strip()
        if len(prompt) < 3:
            return {"S": 0, "verdict": "INCOHERENCE", "valid": False}

        tokens = prompt.lower().split()
        t_len = len(tokens)
        
        # Calcul de base
        beta = 1.0
        # Malus si trop court ou trop long
        if t_len < 4: beta *= 0.6
        if t_len > 100: beta *= 0.85
        
        # Complexité sémantique
        complex_terms = len([t for t in tokens if len(t) > 7])
        if (complex_terms / t_len) > 0.4: beta *= 1.15
        
        # Calcul du gradient (deltaC)
        score_delta = 0.1
        if any(op in tokens for op in cls.OPERANTS): score_delta += 0.45
        if any(fmt in tokens for fmt in cls.FORMATS): score_delta += 0.35
        
        delta_c = min(1.0, score_delta + 0.1)
        lambda_val = max(0.08, 1.1 - (score_delta * 0.85))
        
        s_score = (beta * delta_c) / lambda_val
        
        # Verdict
        verdict = "INCOHERENCE"
        if s_score >= cls.THRESH_OPTIMAL: verdict = "OPTIMAL"
        elif s_score >= cls.THRESH_ADMISSIBLE: verdict = "ADMISSIBLE"
        
        return {
            "S": round(s_score, 2),
            "verdict": verdict,
            "valid": s_score >= cls.THRESH_ADMISSIBLE
        }

# --- Exemple d'utilisation dans une pipeline ---
def gateway_middleware(prompt: str):
    analysis = HeuristicGuard.analyze(prompt)
    
    if not analysis["valid"]:
        print(f"BLOCK: Prompt rejeté (Score: {analysis['S']})")
        return None
        
    return prompt # On laisse passer