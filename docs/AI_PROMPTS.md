# AI Image Generation Prompts

This document describes the prompts used for each of the three generation modes in ProductSnap.

## Overview

ProductSnap uses carefully crafted prompts to generate professional product photography using the Gemini 2.5 Flash API (formerly Nano Banana API). Each mode has a specific prompt template optimized for its use case.

**Location**: `backend/app/services/nano_banana_client.py` (lines 17-32)

---

## Generation Modes & Prompts

### 1. Studio White (`STUDIO_WHITE`)

**Use Case**: E-commerce product shots with clean white backgrounds

**Prompt**:
```
Precisely isolate the product. Crisp edges. Shadow: subtle studio product shadow. 
Pure white (#FFFFFF) background. No background props. No text. Professional product photography.
```

**Key Instructions**:
- ✅ Precise product isolation
- ✅ Crisp, clean edges
- ✅ Subtle studio shadow for depth
- ✅ Pure white (#FFFFFF) background
- ❌ No background props
- ❌ No text overlays
- 🎯 Professional e-commerce style

**Example Output**: Clean product cutout on pure white, perfect for Amazon/Shopify listings.

---

### 2. Model Try-On (`MODEL_TRYON`)

**Use Case**: Products shown on human models (apparel, accessories, etc.)

**Prompt**:
```
Present the product on a realistic model. Maintain correct scale and placement. 
Clean studio lighting. Neutral backdrop. Focus on product clarity. 
Natural pose, professional model.
```

**Key Instructions**:
- ✅ Realistic human model
- ✅ Correct product scale and placement
- ✅ Clean studio lighting
- ✅ Neutral backdrop
- ✅ Natural, professional pose
- 🎯 Product clarity is priority

**Example Output**: Product naturally worn/held by a model with professional lighting.

---

### 3. Lifestyle Scene (`LIFESTYLE_SCENE`)

**Use Case**: Products in real-world, photorealistic environments

**Prompt**:
```
Place the product in a natural setting that fits the category. 
Balanced lighting, photorealistic materials, consistent shadows. 
Avoid brand logos and text. Create an authentic lifestyle environment.
```

**Key Instructions**:
- ✅ Natural, contextual setting
- ✅ Category-appropriate environment
- ✅ Balanced, realistic lighting
- ✅ Photorealistic materials
- ✅ Consistent shadow physics
- ❌ No brand logos or text
- 🎯 Authentic lifestyle feel

**Example Output**: Product in a real-world scene (e.g., coffee mug on a kitchen counter, headphones on a desk).

---

## Custom Prompts (Pro Tier Feature)

### How It Works

For **Pro tier users**, custom prompts can be appended to the base prompt:

```python
def get_prompt(self, mode: JobMode, custom_prompt: Optional[str] = None) -> str:
    base_prompt = self.PROMPT_TEMPLATES.get(mode, "")
    if custom_prompt:
        return f"{base_prompt}\n\nAdditional instructions: {custom_prompt}"
    return base_prompt
```

### Example

**Base Prompt** (Studio White):
```
Precisely isolate the product. Crisp edges. Shadow: subtle studio product shadow. 
Pure white (#FFFFFF) background. No background props. No text. Professional product photography.
```

**Custom Prompt** (User provides):
```
Add dramatic side lighting, metallic finish, blue accent color
```

**Final Prompt Sent to API**:
```
Precisely isolate the product. Crisp edges. Shadow: subtle studio product shadow. 
Pure white (#FFFFFF) background. No background props. No text. Professional product photography.

Additional instructions: Add dramatic side lighting, metallic finish, blue accent color
```

---

## Prompt Design Philosophy

### Core Principles

1. **Specificity** - Clear, actionable instructions
2. **Consistency** - Reproducible results across generations
3. **Quality Focus** - Professional photography standards
4. **Safety** - Explicit restrictions (no text, no logos)
5. **Flexibility** - Base prompt + custom additions

### What Makes These Prompts Effective

✅ **Precise Directives**
- "Precisely isolate" vs. vague "remove background"
- "#FFFFFF" vs. generic "white"
- "Subtle studio product shadow" vs. just "shadow"

✅ **Negative Constraints**
- "No background props"
- "No text"
- "Avoid brand logos"

✅ **Professional Standards**
- "Professional product photography"
- "Photorealistic materials"
- "Balanced lighting"

✅ **Technical Details**
- Shadow specifications
- Lighting descriptions
- Material realism requirements

---

## Modifying Prompts

### For Development/Testing

To test new prompts, edit `backend/app/services/nano_banana_client.py`:

```python
PROMPT_TEMPLATES = {
    JobMode.STUDIO_WHITE: (
        "Your new prompt here..."
    ),
    # ...
}
```

### Best Practices

1. **Test Incrementally** - Change one element at a time
2. **A/B Compare** - Keep old results for comparison
3. **Document Changes** - Note what works and what doesn't
4. **Use Mock Mode** - Test prompt formatting without API costs
5. **Monitor Results** - Track quality metrics across prompt versions

---

## API Configuration

### Current Setup

- **API**: Gemini 2.5 Flash (Google)
- **Mode**: Controlled by `IMAGE_GENERATION_MODE` env var
  - `mock` - Returns 1x1 PNG, no API calls
  - `live` - Real API calls to Gemini

### Environment Variables

```bash
# .env file
NANO_BANANA_API_KEY=your_gemini_api_key_here
NANO_BANANA_API_URL=https://generativelanguage.googleapis.com/v1beta
IMAGE_GENERATION_MODE=live  # or 'mock' for testing
```

---

## Prompt Evolution History

### Version 1.0 (Current)
- Initial prompts based on professional photography standards
- Tested with Gemini 2.5 Flash API
- Optimized for e-commerce, fashion, and lifestyle photography

### Future Improvements

Ideas for prompt enhancement:

1. **Category-Specific Prompts**
   - Electronics: emphasize reflections, metallic surfaces
   - Fashion: fabric texture, drape, fit
   - Food: appetizing lighting, fresh appearance

2. **Style Variations**
   - Minimalist
   - Luxury/Premium
   - Vintage/Retro
   - Modern/Tech

3. **Advanced Controls**
   - Lighting angle specifications
   - Color temperature (warm/cool)
   - Depth of field control
   - Material finish (matte/glossy)

---

## Troubleshooting

### Common Issues

**Poor Background Removal**
- Ensure "Precisely isolate" is in prompt
- Add "Crisp edges" instruction
- Specify background color explicitly

**Inconsistent Lighting**
- Add lighting type (e.g., "studio lighting", "natural daylight")
- Specify direction (e.g., "soft front lighting")
- Use "balanced lighting" for consistency

**Unwanted Elements**
- Add explicit negatives: "No text", "No logos", "No props"
- Be specific about what to exclude

**Scale/Proportion Issues**
- Add "Maintain correct scale and placement"
- Specify relative sizes when needed

---

## Related Files

- **Prompt Templates**: `backend/app/services/nano_banana_client.py`
- **Job Modes**: `backend/app/models/job.py`
- **Worker Implementation**: `backend/app/worker.py`
- **Mock Mode Docs**: `docs/IMAGE_GENERATION_MODE.md`

---

## Testing Prompts

### Using Mock Mode

```bash
# Set mock mode in .env
IMAGE_GENERATION_MODE=mock

# Restart services
docker compose restart backend worker

# Create test job - no API calls, no cost!
curl -X POST http://localhost:8000/api/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@product.jpg" \
  -F "mode=studio_white"
```

### Analyzing Results

1. **Visual Quality** - Does it match expectations?
2. **Consistency** - Similar products → similar results?
3. **Edge Cases** - Complex products (transparent, reflective, etc.)
4. **Performance** - Generation time, API costs

---

## Contributing

When proposing prompt changes:

1. **Document Rationale** - Why the change?
2. **Show Examples** - Before/after comparisons
3. **Test Thoroughly** - Multiple product types
4. **Consider Impact** - Existing users' expectations
5. **Version Control** - Track prompt versions

---

*Last Updated: October 9, 2025*
