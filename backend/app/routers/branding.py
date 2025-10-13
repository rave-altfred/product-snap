"""Branding API - Expose design system tokens and assets"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/branding")
async def get_branding():
    """
    Get all branding information including colors, fonts, logos, shadows, and animations.
    This endpoint provides the complete design system for ProductSnap.
    """
    return {
        "app_info": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
        "colors": {
            "primary": {
                "50": "#e6f4f9",
                "100": "#ccebf4",
                "200": "#99d6e9",
                "300": "#66c2de",
                "400": "#33add3",
                "500": "#1a8fb8",
                "600": "#154d6b",
                "700": "#0f3a50",
                "800": "#0a3f5e",
                "900": "#082f49",
                "950": "#051d2e",
                "description": "Primary brand color - Ocean blue theme"
            },
            "accent": {
                "50": "#e6fbff",
                "100": "#ccf7ff",
                "200": "#99efff",
                "300": "#66e7ff",
                "400": "#33dfff",
                "500": "#00d4ff",
                "600": "#00b8e6",
                "700": "#008fb3",
                "800": "#006680",
                "900": "#004d66",
                "description": "Accent color - Bright cyan for highlights"
            },
            "success": {
                "50": "#f0fdf4",
                "100": "#dcfce7",
                "500": "#22c55e",
                "600": "#16a34a",
                "700": "#15803d",
                "description": "Success state color - Green"
            },
            "semantic": {
                "background_light": "#f9fafb",  # gray-50 - solid light background
                "background_dark": "#111827",   # gray-900 - solid dark background
                "text_light": "#111827",       # gray-900 - dark text for light mode
                "text_dark": "#f9fafb",        # gray-100 - light text for dark mode
                "card_light": "#ffffff",       # white cards in light mode
                "card_dark": "rgba(31, 41, 55, 0.8)",  # gray-800/80 in dark mode
            }
        },
        "typography": {
            "font_family": {
                "sans": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                "description": "Default sans-serif font stack"
            },
            "font_weights": {
                "normal": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700,
            },
            "font_sizes": {
                "xs": "0.75rem",    # 12px
                "sm": "0.875rem",   # 14px
                "base": "1rem",     # 16px
                "lg": "1.125rem",   # 18px
                "xl": "1.25rem",    # 20px
                "2xl": "1.5rem",    # 24px
                "3xl": "1.875rem",  # 30px
                "4xl": "2.25rem",   # 36px
                "5xl": "3rem",      # 48px
            }
        },
        "spacing": {
            "border_radius": {
                "sm": "0.5rem",     # 8px
                "md": "0.75rem",    # 12px
                "lg": "1rem",       # 16px
                "xl": "1.5rem",     # 24px
                "2xl": "2rem",      # 32px
                "description": "Standard border radius values"
            },
            "padding": {
                "xs": "0.5rem",     # 8px
                "sm": "0.75rem",    # 12px
                "md": "1rem",       # 16px
                "lg": "1.5rem",     # 24px
                "xl": "2rem",       # 32px
                "description": "Standard padding values"
            }
        },
        "shadows": {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            "glass": "0 8px 32px 0 rgba(31, 38, 135, 0.1)",
            "glass_dark": "0 8px 32px 0 rgba(0, 0, 0, 0.3)",
            "glow": "0 0 20px rgba(0, 212, 255, 0.3)",
            "glow_lg": "0 0 40px rgba(0, 212, 255, 0.4)",
            "description": "Shadow effects for depth and glows"
        },
        "gradients": {
            "primary_button": {
                "from": "#1a8fb8",  # primary-600
                "to": "#0f3a50",    # primary-700
                "hover_from": "#0f3a50",  # primary-700
                "hover_to": "#0a3f5e",    # primary-800
                "description": "Primary button gradient"
            },
            "text_gradient": {
                "from": "#1a8fb8",  # primary-600
                "to": "#00b8e6",    # accent-600
                "description": "Gradient text effect"
            },
            "feature_icon": {
                "from": "#1a8fb8",  # primary-500
                "to": "#154d6b",    # primary-600
                "description": "Feature icon gradient"
            },
            "stat_card_light": {
                "from": "white",
                "to": "rgba(224, 242, 254, 0.8)",  # blue-50/80
                "description": "Stat card background (light mode)"
            },
            "stat_card_dark": {
                "from": "rgba(31, 41, 55, 0.9)",  # gray-800/90
                "to": "rgba(5, 29, 46, 0.3)",     # primary-950/30
                "description": "Stat card background (dark mode)"
            }
        },
        "animations": {
            "transitions": {
                "default": "200ms",
                "slow": "300ms",
                "description": "Standard transition durations"
            },
            "keyframes": {
                "fade_in": {
                    "from": {"opacity": 0.85},
                    "to": {"opacity": 1},
                    "duration": "0.2s",
                    "timing": "ease-out"
                },
                "slide_up": {
                    "from": {"transform": "translateY(20px)", "opacity": 0},
                    "to": {"transform": "translateY(0)", "opacity": 1},
                    "duration": "0.5s",
                    "timing": "ease-out"
                },
                "scale_in": {
                    "from": {"transform": "scale(0.95)", "opacity": 0},
                    "to": {"transform": "scale(1)", "opacity": 1},
                    "duration": "0.3s",
                    "timing": "ease-out"
                },
                "glow": {
                    "0%": {"box_shadow": "0 0 20px rgba(0, 212, 255, 0.3)"},
                    "50%": {"box_shadow": "0 0 40px rgba(0, 212, 255, 0.5)"},
                    "100%": {"box_shadow": "0 0 20px rgba(0, 212, 255, 0.3)"},
                    "duration": "2s",
                    "timing": "ease-in-out infinite"
                }
            },
            "hover_effects": {
                "button_scale": "scale(1.05)",
                "button_active": "scale(0.95)",
                "card_scale": "scale(1.02)",
                "icon_scale": "scale(1.1) rotate(3deg)",
                "description": "Standard hover transformations"
            }
        },
        "components": {
            "button": {
                "primary": {
                    "background": "gradient from primary-600 to primary-700",
                    "text": "white",
                    "padding": "0.75rem 1.5rem",
                    "border_radius": "0.75rem",
                    "shadow": "shadow-lg with primary-500/30",
                    "hover": "scale(1.05), shadow-glow"
                },
                "secondary": {
                    "background": "white (light) / gray-800/80 (dark) with backdrop-blur",
                    "border": "2px solid gray-300 (light) / gray-700 (dark)",
                    "text": "gray-800 (light) / gray-200 (dark)",
                    "hover": "border becomes primary-400 (light) / primary-700 (dark)"
                }
            },
            "card": {
                "default": {
                    "background": "white/80 (light) / gray-800/80 (dark) with backdrop-blur",
                    "border": "1px solid gray-200 (light) / gray-700/50 (dark)",
                    "border_radius": "1rem",
                    "padding": "1.5rem to 2rem",
                    "shadow": "shadow-lg (light) / shadow-glass-dark (dark)",
                    "hover": "shadow-xl, scale(1.02)"
                },
                "stat": {
                    "background": "gradient from white to blue-50/80 (light) / gray-800/90 to primary-950/30 (dark)",
                    "border": "gray-200 (light) / gray-700 (dark)"
                },
                "feature": {
                    "hover_border": "primary-300 (light) / primary-700 (dark)",
                    "icon_hover": "scale(1.1) rotate(3deg) with shadow-glow"
                }
            },
            "input": {
                "background": "white (light) / gray-800/80 (dark) with backdrop-blur",
                "border": "2px solid gray-300 (light) / gray-700 (dark)",
                "focus": "ring-2 ring-primary-500, border-primary-500",
                "padding": "0.875rem 1.25rem",
                "border_radius": "0.75rem"
            },
            "navigation": {
                "background": "white/90 (light) / gray-900/70 (dark) with backdrop-blur-lg",
                "border": "border-b gray-200 (light) / gray-800/50 (dark)",
                "shadow": "shadow-md"
            }
        },
        "assets": {
            "logo": {
                "primary": "/assets/logo.png",
                "description": "Primary ProductSnap logo"
            },
            "banners": [
                {
                    "name": "banner1",
                    "path": "/assets/banner1.png",
                    "description": "Banner image 1"
                },
                {
                    "name": "banner2",
                    "path": "/assets/banner2.png",
                    "description": "Banner image 2"
                },
                {
                    "name": "banner3",
                    "path": "/assets/banner3.png",
                    "description": "Banner image 3"
                }
            ]
        },
        "theme_modes": {
            "light": {
                "enabled": True,
                "background": "bg-gray-50 (solid light gray)",
                "text": "gray-900 (dark text)",
                "card_bg": "white",
                "border": "gray-200"
            },
            "dark": {
                "enabled": True,
                "background": "bg-gray-900 (solid dark)",
                "text": "gray-100 (light text)",
                "card_bg": "gray-800/80",
                "border": "gray-700"
            },
            "default_mode": "light",
            "storage_key": "productsnap-theme"
        },
        "design_principles": {
            "glass_morphism": "Backdrop blur with semi-transparent backgrounds",
            "gradient_heavy": "Extensive use of gradients for depth and visual interest",
            "interactive": "Hover effects with scale transformations and glows",
            "modern": "Rounded corners (0.75rem to 1rem), soft shadows, smooth transitions",
            "accessible": "High contrast ratios, clear focus states, semantic colors"
        }
    }
