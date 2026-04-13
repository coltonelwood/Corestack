"""Prompt template management."""

from __future__ import annotations

from pydantic import BaseModel


class PromptTemplate(BaseModel):
    """A reusable prompt template with variable substitution."""

    name: str
    system: str = "You are a helpful business operations assistant."
    template: str
    description: str = ""

    def render(self, **variables: str) -> str:
        """Render the template with the given variables."""
        return self.template.format(**variables)


# ── Built-in templates ───────────────────────────────────────

PRODUCT_DESCRIPTION = PromptTemplate(
    name="product_description",
    system="You are an expert e-commerce copywriter. Write compelling, SEO-optimized product descriptions.",
    template=(
        "Write a product description for:\n"
        "Product: {product_name}\n"
        "Category: {category}\n"
        "Brand voice: {brand_voice}\n"
        "Target audience: {audience}\n\n"
        "Requirements:\n"
        "- 150-200 words\n"
        "- Include key benefits\n"
        "- Use power words\n"
        "- End with a call to action"
    ),
    description="Generate an SEO-optimized product description.",
)

COMPETITOR_ANALYSIS = PromptTemplate(
    name="competitor_analysis",
    system="You are a senior market research analyst. Provide data-driven insights.",
    template=(
        "Analyze the competitive landscape for:\n"
        "Business: {business_name}\n"
        "Industry: {industry}\n"
        "Competitors: {competitors}\n\n"
        "Provide:\n"
        "1. Pricing comparison\n"
        "2. Strengths and weaknesses\n"
        "3. Market positioning opportunities\n"
        "4. Recommended actions"
    ),
    description="Analyze competitors and provide strategic recommendations.",
)

CAMPAIGN_COPY = PromptTemplate(
    name="campaign_copy",
    system="You are a performance marketing expert. Write high-converting ad copy.",
    template=(
        "Create ad copy for:\n"
        "Product: {product_name}\n"
        "Channel: {channel}\n"
        "Target audience: {audience}\n"
        "Goal: {goal}\n"
        "Tone: {tone}\n\n"
        "Generate:\n"
        "- 3 headline options (max 30 characters each)\n"
        "- 2 body copy options (max 90 characters each)\n"
        "- 1 call-to-action"
    ),
    description="Generate ad copy for a marketing campaign.",
)

TEMPLATES: dict[str, PromptTemplate] = {
    t.name: t for t in [PRODUCT_DESCRIPTION, COMPETITOR_ANALYSIS, CAMPAIGN_COPY]
}
