"""
Roast Engine - Generates savage but helpful cost optimization roasts
"""
import random
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Roast:
    """A roast with context and severity"""
    title: str
    message: str
    recommendation: str
    roast_level: str
    savings: float


class RoastEngine:
    """Generates contextual roasts for cloud cost waste"""
    
    def __init__(self, use_ollama: bool = True, model: str = "mistral"):
        """
        Initialize roast engine
        
        Args:
            use_ollama: Use local Ollama for AI-powered roasts
            model: Ollama model to use (default: mistral)
        """
        self.use_ollama = use_ollama
        self.model = model
        self.ollama_client = None
        
        if use_ollama:
            try:
                import ollama
                self.ollama_client = ollama
                # Test connection
                self.ollama_client.list()
                print(f"✅ Connected to Ollama - using {model} for AI-powered roasts")
            except Exception as e:
                print(f"⚠️  Ollama not available ({e}), falling back to templates")
                self.use_ollama = False
    
    # Roast templates by waste type (fallback if Ollama fails)
    ROAST_TEMPLATES = {
        'oversized_vm': [
            {
                'roast': "Using a {size} VM for {purpose} is like hiring a rocket scientist to flip burgers",
                'level': "Galactic Overkill"
            },
            {
                'roast': "This {size} VM is working harder at wasting money than doing actual work",
                'level': "Professional Money Incinerator"
            },
            {
                'roast': "You're paying for a Ferrari to drive to the mailbox",
                'level': "Luxury Inefficiency"
            }
        ],
        'idle_resource': [
            {
                'roast': "This resource has been sitting idle longer than your gym membership",
                'level': "Digital Couch Potato"
            },
            {
                'roast': "Congratulations! You're heating Azure's data center for no reason",
                'level': "Expensive Heater"
            },
            {
                'roast': "This resource is more unused than your college degree",
                'level': "Peak Waste Achievement"
            }
        ],
        'old_storage': [
            {
                'roast': "You're paying premium prices to store digital dust",
                'level': "Cloud Hoarder"
            },
            {
                'roast': "This data hasn't been touched in {days} days. It's not a backup, it's archaeology",
                'level': "Digital Time Capsule"
            },
            {
                'roast': "Storage tier optimization is free. Unlike your current approach",
                'level': "Money Composting"
            }
        ],
        'unattached_disk': [
            {
                'roast': "You're paying for a disk that's not attached to anything. That's modern art levels of useless",
                'level': "Abstract Spending"
            },
            {
                'roast': "This orphaned disk costs more per month than most streaming subscriptions",
                'level': "Netflix But Worse"
            }
        ],
        'public_ip_unused': [
            {
                'roast': "Reserved a public IP and never used it. That's like buying a parking spot for a car you don't own",
                'level': "Preventive Waste"
            }
        ],
        'dev_prod_mix': [
            {
                'roast': "Running dev resources 24/7 is like leaving your car engine running while you sleep",
                'level': "Always-On Syndrome"
            },
            {
                'roast': "Dev environments don't need to run on weekends. They're not doctors",
                'level': "Workaholic Resources"
            }
        ]
    }
    
    def _generate_ai_roast(self, waste_type: str, context: Dict) -> Optional[Dict]:
        """
        Generate a roast using local Ollama LLM
        
        Args:
            waste_type: Type of waste
            context: Context about the resource
            
        Returns:
            Dict with 'roast' and 'level' or None if failed
        """
        if not self.use_ollama or not self.ollama_client:
            return None
        
        # Build prompt for Mistral
        prompt = f"""You are a sarcastic cloud cost optimizer. Generate a short, funny but helpful roast for this wasteful Azure resource.

Waste Type: {waste_type}
Resource: {context.get('title', 'Unknown resource')}
Details: {context.get('purpose', 'unknown')} - {context.get('recommendation', '')}
Cost Waste: ${context.get('savings', 0)}/month

Generate a roast that is:
1. One sentence, maximum 20 words
2. Funny and memorable
3. Uses analogies or comparisons
4. Savage but helpful

Also provide a short "Roast Level" name (2-3 words, creative and funny).

Format your response EXACTLY like this:
ROAST: Your one-sentence roast here
LEVEL: Your creative roast level name"""

        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.8,  # More creative
                    "top_p": 0.9,
                }
            )
            
            # Parse response
            text = response['response'].strip()
            roast_line = ""
            level_line = ""
            
            for line in text.split('\n'):
                if line.startswith('ROAST:'):
                    roast_line = line.replace('ROAST:', '').strip()
                elif line.startswith('LEVEL:'):
                    level_line = line.replace('LEVEL:', '').strip()
            
            if roast_line and level_line:
                return {
                    'roast': roast_line,
                    'level': level_line
                }
            
        except Exception as e:
            print(f"⚠️  Ollama generation failed: {e}")
            return None
        
        return None

    def generate_roast(self, waste_type: str, context: Dict) -> Roast:
        """
        Generate a roast for a specific type of waste
        
        Args:
            waste_type: Type of waste (oversized_vm, idle_resource, etc.)
            context: Additional context (size, purpose, cost, etc.)
        
        Returns:
            Roast object with message and recommendations
        """
        # Try AI-powered roast first
        ai_roast = self._generate_ai_roast(waste_type, context)
        
        if ai_roast:
            roast_message = ai_roast['roast']
            roast_level = ai_roast['level']
        else:
            # Fallback to templates
            templates = self.ROAST_TEMPLATES.get(waste_type, [
                {'roast': "This is wasteful and you should feel wasteful", 'level': "Generic Waste"}
            ])
            
            template = random.choice(templates)
            roast_message = template['roast'].format(**context)
            roast_level = template['level']
        
        return Roast(
            title=context.get('title', 'Cost Waste Detected'),
            message=roast_message,
            recommendation=context.get('recommendation', 'Fix this immediately'),
            roast_level=roast_level,
            savings=context.get('savings', 0)
        )
    
    def make_cost_relatable(self, monthly_cost: float) -> str:
        """Convert boring dollars into relatable comparisons"""
        yearly_cost = monthly_cost * 12
        
        # Monthly comparisons
        if monthly_cost < 20:
            spotify_count = int(monthly_cost / 10)
            return f"${monthly_cost:.2f}/month - That's {spotify_count} Spotify subscriptions"
        elif monthly_cost < 100:
            netflix_count = int(monthly_cost / 15)
            return f"${monthly_cost:.2f}/month - That's {netflix_count} Netflix accounts"
        elif monthly_cost < 500:
            return f"${monthly_cost:.2f}/month - That's ${yearly_cost:.2f}/year (a decent gaming PC)"
        elif monthly_cost < 2000:
            return f"${monthly_cost:.2f}/month - That's ${yearly_cost:.2f}/year (a used car)"
        else:
            return f"${monthly_cost:.2f}/month - That's ${yearly_cost:.2f}/year (your accountant is crying)"
    
    def generate_summary_roast(self, total_waste: float, waste_count: int) -> str:
        """Generate a summary roast for total waste"""
        yearly_waste = total_waste * 12
        
        if total_waste < 100:
            return f"You're wasting ${total_waste:.2f}/month. Not terrible, but not great."
        elif total_waste < 500:
            return f"💸 ${total_waste:.2f}/month wasted ({waste_count} issues). That's ${yearly_waste:.2f}/year you're donating to Microsoft."
        elif total_waste < 2000:
            return f"🔥 ${total_waste:.2f}/month wasted ({waste_count} issues). That's a used car every year. Hope you like walking."
        else:
            return f"🚨 ${total_waste:.2f}/month wasted ({waste_count} issues). That's ${yearly_waste:.2f}/year. This is a cry for help."
    
    def get_emoji_for_severity(self, savings: float) -> str:
        """Get emoji based on severity of waste"""
        if savings < 50:
            return "💰"
        elif savings < 200:
            return "💸"
        elif savings < 1000:
            return "🔥"
        else:
            return "🚨"
