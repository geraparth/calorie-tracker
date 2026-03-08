import streamlit as st
import smtplib
import json
import os
import requests
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

# ─────────────────────────────────────────────
#  CALORIE & MACRO DATABASE  (raw / common items)
#  calories: kcal | protein, carbs, fat, fiber: grams
#  unit: "g" → per 100 g  |  "piece" → per piece/serving
# ─────────────────────────────────────────────
FOOD_DATABASE = {
    # ══════════════════════════════════
    #  GRAINS & CEREALS
    # ══════════════════════════════════
    "Uncooked Rice (White)":      {"calories": 360, "protein": 7.0,  "carbs": 79.0, "fat": 0.6,  "fiber": 1.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Uncooked Rice (Brown)":      {"calories": 370, "protein": 7.9,  "carbs": 77.0, "fat": 2.9,  "fiber": 3.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Cooked Rice (White)":        {"calories": 130, "protein": 2.7,  "carbs": 28.0, "fat": 0.3,  "fiber": 0.4,  "unit": "g",     "serving_label": "per 100 g"},
    "Cooked Rice (Brown)":        {"calories": 123, "protein": 2.7,  "carbs": 26.0, "fat": 1.0,  "fiber": 1.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Basmati Rice (Uncooked)":    {"calories": 350, "protein": 7.0,  "carbs": 78.0, "fat": 0.5,  "fiber": 0.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Oats":                       {"calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9,  "fiber": 10.6, "unit": "g",     "serving_label": "per 100 g"},
    "Wheat Flour (Atta)":         {"calories": 340, "protein": 12.0, "carbs": 72.0, "fat": 1.7,  "fiber": 10.7, "unit": "g",     "serving_label": "per 100 g"},
    "Quinoa":                     {"calories": 368, "protein": 14.1, "carbs": 64.2, "fat": 6.1,  "fiber": 7.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Bread (White)":              {"calories": 265, "protein": 9.0,  "carbs": 49.0, "fat": 3.2,  "fiber": 2.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Bread (Brown / Wheat)":      {"calories": 247, "protein": 13.0, "carbs": 41.0, "fat": 3.4,  "fiber": 6.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Bread (Multigrain)":         {"calories": 250, "protein": 13.0, "carbs": 43.0, "fat": 3.8,  "fiber": 7.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Pasta (Uncooked)":           {"calories": 371, "protein": 13.0, "carbs": 75.0, "fat": 1.5,  "fiber": 3.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Pasta (Whole Wheat, Uncooked)": {"calories": 348, "protein": 14.6, "carbs": 68.0, "fat": 2.5, "fiber": 8.0, "unit": "g",    "serving_label": "per 100 g"},
    "Poha (Flattened Rice)":      {"calories": 346, "protein": 6.6,  "carbs": 77.3, "fat": 1.2,  "fiber": 1.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Semolina (Sooji / Rava)":    {"calories": 350, "protein": 12.7, "carbs": 72.8, "fat": 1.1,  "fiber": 3.9,  "unit": "g",     "serving_label": "per 100 g"},
    "Cornflakes":                 {"calories": 357, "protein": 7.0,  "carbs": 84.0, "fat": 0.4,  "fiber": 3.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Muesli":                     {"calories": 340, "protein": 9.0,  "carbs": 63.0, "fat": 6.0,  "fiber": 7.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Granola":                    {"calories": 471, "protein": 10.0, "carbs": 64.0, "fat": 20.0, "fiber": 5.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Roti / Chapati":             {"calories": 104, "protein": 3.5,  "carbs": 18.0, "fat": 2.0,  "fiber": 2.0,  "unit": "piece", "serving_label": "per piece (~40 g)"},
    "Paratha (Plain)":            {"calories": 180, "protein": 4.0,  "carbs": 23.0, "fat": 8.0,  "fiber": 1.5,  "unit": "piece", "serving_label": "per piece (~60 g)"},
    "Naan":                       {"calories": 262, "protein": 8.7,  "carbs": 45.4, "fat": 5.1,  "fiber": 2.0,  "unit": "piece", "serving_label": "per piece (~90 g)"},
    "Dosa (Plain)":               {"calories": 120, "protein": 3.5,  "carbs": 18.0, "fat": 3.5,  "fiber": 0.8,  "unit": "piece", "serving_label": "per piece"},
    "Idli":                       {"calories": 39,  "protein": 1.5,  "carbs": 7.9,  "fat": 0.2,  "fiber": 0.4,  "unit": "piece", "serving_label": "per piece (~30 g)"},
    "Vada (Medu Vada)":           {"calories": 150, "protein": 5.0,  "carbs": 14.0, "fat": 8.0,  "fiber": 2.0,  "unit": "piece", "serving_label": "per piece (~50 g)"},
    "Tortilla (Flour)":           {"calories": 312, "protein": 8.0,  "carbs": 52.0, "fat": 8.0,  "fiber": 2.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Tortilla (Corn)":            {"calories": 218, "protein": 5.7,  "carbs": 44.6, "fat": 2.8,  "fiber": 5.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Couscous":                   {"calories": 376, "protein": 12.8, "carbs": 77.4, "fat": 0.6,  "fiber": 5.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Barley":                     {"calories": 354, "protein": 12.5, "carbs": 73.5, "fat": 2.3,  "fiber": 17.3, "unit": "g",     "serving_label": "per 100 g"},
    "Millet (Bajra)":             {"calories": 378, "protein": 11.0, "carbs": 73.0, "fat": 4.2,  "fiber": 8.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Ragi (Finger Millet)":       {"calories": 328, "protein": 7.3,  "carbs": 72.0, "fat": 1.3,  "fiber": 3.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Jowar (Sorghum)":            {"calories": 329, "protein": 10.4, "carbs": 72.6, "fat": 1.9,  "fiber": 9.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Amaranth":                   {"calories": 371, "protein": 13.6, "carbs": 65.3, "fat": 7.0,  "fiber": 6.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Buckwheat (Kuttu)":          {"calories": 343, "protein": 13.3, "carbs": 71.5, "fat": 3.4,  "fiber": 10.0, "unit": "g",     "serving_label": "per 100 g"},

    # ══════════════════════════════════
    #  PROTEINS – DAIRY / VEGETARIAN
    # ══════════════════════════════════
    "Paneer":                     {"calories": 265, "protein": 18.3, "carbs": 1.2,  "fat": 20.8, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Tofu (Firm)":                {"calories": 144, "protein": 17.3, "carbs": 2.8,  "fat": 8.7,  "fiber": 2.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Tofu (Silken)":              {"calories": 55,  "protein": 4.8,  "carbs": 2.0,  "fat": 3.0,  "fiber": 0.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Tempeh":                     {"calories": 192, "protein": 20.3, "carbs": 7.6,  "fat": 10.8, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Cheddar Cheese":             {"calories": 402, "protein": 25.0, "carbs": 1.3,  "fat": 33.1, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Mozzarella Cheese":          {"calories": 280, "protein": 28.0, "carbs": 3.1,  "fat": 17.1, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Parmesan Cheese":            {"calories": 431, "protein": 38.5, "carbs": 4.1,  "fat": 29.0, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Feta Cheese":                {"calories": 264, "protein": 14.2, "carbs": 4.1,  "fat": 21.3, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Cream Cheese":               {"calories": 342, "protein": 5.9,  "carbs": 4.1,  "fat": 34.2, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Cottage Cheese (Low-fat)":   {"calories": 98,  "protein": 11.1, "carbs": 3.4,  "fat": 4.3,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Greek Yogurt":               {"calories": 59,  "protein": 10.0, "carbs": 3.6,  "fat": 0.7,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Curd / Yogurt":              {"calories": 60,  "protein": 3.5,  "carbs": 4.7,  "fat": 3.3,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Milk (Whole)":               {"calories": 61,  "protein": 3.2,  "carbs": 4.8,  "fat": 3.3,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Milk (Skimmed)":             {"calories": 34,  "protein": 3.4,  "carbs": 5.0,  "fat": 0.1,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Milk (Almond, Unsweetened)": {"calories": 15,  "protein": 0.6,  "carbs": 0.3,  "fat": 1.2,  "fiber": 0.2,  "unit": "g",     "serving_label": "per 100 ml"},
    "Milk (Oat)":                 {"calories": 43,  "protein": 1.0,  "carbs": 7.0,  "fat": 1.5,  "fiber": 0.8,  "unit": "g",     "serving_label": "per 100 ml"},
    "Buttermilk":                 {"calories": 40,  "protein": 3.3,  "carbs": 4.8,  "fat": 0.9,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Soy Milk":                   {"calories": 33,  "protein": 2.9,  "carbs": 1.8,  "fat": 1.6,  "fiber": 0.4,  "unit": "g",     "serving_label": "per 100 ml"},
    "Whey Protein Powder":        {"calories": 120, "protein": 24.0, "carbs": 3.0,  "fat": 1.5,  "fiber": 0.0,  "unit": "piece", "serving_label": "per scoop (~30 g)"},
    "Casein Protein Powder":      {"calories": 115, "protein": 24.0, "carbs": 3.0,  "fat": 0.5,  "fiber": 0.0,  "unit": "piece", "serving_label": "per scoop (~30 g)"},

    # ══════════════════════════════════
    #  PROTEINS – EGGS & MEAT
    # ══════════════════════════════════
    "Egg (Whole, Boiled)":        {"calories": 78,  "protein": 6.3,  "carbs": 0.6,  "fat": 5.3,  "fiber": 0.0,  "unit": "piece", "serving_label": "per piece (~50 g)"},
    "Egg White":                  {"calories": 17,  "protein": 3.6,  "carbs": 0.2,  "fat": 0.1,  "fiber": 0.0,  "unit": "piece", "serving_label": "per piece"},
    "Egg (Scrambled, 1 large)":   {"calories": 91,  "protein": 6.1,  "carbs": 1.0,  "fat": 6.7,  "fiber": 0.0,  "unit": "piece", "serving_label": "per piece"},
    "Chicken Breast":             {"calories": 165, "protein": 31.0, "carbs": 0.0,  "fat": 3.6,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Chicken Thigh":              {"calories": 209, "protein": 26.0, "carbs": 0.0,  "fat": 10.9, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Chicken Wings":              {"calories": 203, "protein": 30.5, "carbs": 0.0,  "fat": 8.1,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Chicken (Whole, Skin-on)":   {"calories": 239, "protein": 27.3, "carbs": 0.0,  "fat": 13.6, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Mutton / Lamb":              {"calories": 250, "protein": 25.6, "carbs": 0.0,  "fat": 16.0, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Goat Meat":                  {"calories": 143, "protein": 27.1, "carbs": 0.0,  "fat": 3.0,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Beef (Lean)":                {"calories": 250, "protein": 26.0, "carbs": 0.0,  "fat": 15.0, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Pork (Lean)":                {"calories": 242, "protein": 27.3, "carbs": 0.0,  "fat": 14.0, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Bacon":                      {"calories": 541, "protein": 37.0, "carbs": 1.4,  "fat": 42.0, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Fish (Salmon)":              {"calories": 208, "protein": 20.4, "carbs": 0.0,  "fat": 13.4, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Fish (Tilapia)":             {"calories": 128, "protein": 26.2, "carbs": 0.0,  "fat": 2.6,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Fish (Cod)":                 {"calories": 82,  "protein": 18.0, "carbs": 0.0,  "fat": 0.7,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Fish (Tuna, Fresh)":         {"calories": 144, "protein": 23.3, "carbs": 0.0,  "fat": 4.9,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Fish (Mackerel)":            {"calories": 205, "protein": 18.6, "carbs": 0.0,  "fat": 13.9, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Fish (Sardine)":             {"calories": 208, "protein": 24.6, "carbs": 0.0,  "fat": 11.5, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Fish (Hilsa / Ilish)":       {"calories": 310, "protein": 22.0, "carbs": 0.0,  "fat": 24.0, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Prawns / Shrimp":            {"calories": 99,  "protein": 24.0, "carbs": 0.2,  "fat": 0.3,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Crab":                       {"calories": 97,  "protein": 19.4, "carbs": 0.0,  "fat": 1.5,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Lobster":                    {"calories": 89,  "protein": 19.0, "carbs": 0.0,  "fat": 0.9,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Turkey Breast":              {"calories": 135, "protein": 30.0, "carbs": 0.0,  "fat": 1.0,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Turkey (Ground)":            {"calories": 170, "protein": 21.0, "carbs": 0.0,  "fat": 9.4,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Tuna (Canned in Water)":     {"calories": 116, "protein": 25.5, "carbs": 0.0,  "fat": 0.8,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Tuna (Canned in Oil)":       {"calories": 198, "protein": 29.1, "carbs": 0.0,  "fat": 8.2,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},

    # ══════════════════════════════════
    #  LEGUMES & PULSES (per 100 g, uncooked)
    # ══════════════════════════════════
    "Chana Dal":                  {"calories": 360, "protein": 22.0, "carbs": 60.0, "fat": 5.3,  "fiber": 11.0, "unit": "g",     "serving_label": "per 100 g"},
    "Moong Dal":                  {"calories": 347, "protein": 24.0, "carbs": 59.0, "fat": 1.2,  "fiber": 8.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Masoor Dal (Red Lentil)":    {"calories": 343, "protein": 25.0, "carbs": 57.0, "fat": 1.1,  "fiber": 10.8, "unit": "g",     "serving_label": "per 100 g"},
    "Toor Dal":                   {"calories": 342, "protein": 22.0, "carbs": 57.0, "fat": 1.5,  "fiber": 15.0, "unit": "g",     "serving_label": "per 100 g"},
    "Urad Dal (Black Gram)":      {"calories": 341, "protein": 25.2, "carbs": 59.0, "fat": 1.4,  "fiber": 18.3, "unit": "g",     "serving_label": "per 100 g"},
    "Rajma (Kidney Beans)":       {"calories": 333, "protein": 23.6, "carbs": 60.0, "fat": 0.8,  "fiber": 24.9, "unit": "g",     "serving_label": "per 100 g"},
    "Chickpeas (Kabuli Chana)":   {"calories": 364, "protein": 19.3, "carbs": 61.0, "fat": 6.0,  "fiber": 17.4, "unit": "g",     "serving_label": "per 100 g"},
    "Black Beans":                {"calories": 341, "protein": 21.6, "carbs": 62.4, "fat": 0.9,  "fiber": 15.5, "unit": "g",     "serving_label": "per 100 g"},
    "Black Eyed Peas (Lobia)":    {"calories": 336, "protein": 23.5, "carbs": 60.0, "fat": 1.3,  "fiber": 10.6, "unit": "g",     "serving_label": "per 100 g"},
    "Green Moong (Whole)":        {"calories": 347, "protein": 24.0, "carbs": 62.6, "fat": 1.2,  "fiber": 16.3, "unit": "g",     "serving_label": "per 100 g"},
    "Soybean":                    {"calories": 446, "protein": 36.5, "carbs": 30.2, "fat": 19.9, "fiber": 9.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Peanuts":                    {"calories": 567, "protein": 25.8, "carbs": 16.1, "fat": 49.2, "fiber": 8.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Edamame":                    {"calories": 121, "protein": 11.9, "carbs": 8.6,  "fat": 5.2,  "fiber": 5.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Hummus":                     {"calories": 166, "protein": 7.9,  "carbs": 14.3, "fat": 9.6,  "fiber": 6.0,  "unit": "g",     "serving_label": "per 100 g"},

    # ══════════════════════════════════
    #  VEGETABLES (per 100 g, raw)
    # ══════════════════════════════════
    "Spinach":                    {"calories": 23,  "protein": 2.9,  "carbs": 3.6,  "fat": 0.4,  "fiber": 2.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Kale":                       {"calories": 49,  "protein": 4.3,  "carbs": 8.8,  "fat": 0.9,  "fiber": 3.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Broccoli":                   {"calories": 34,  "protein": 2.8,  "carbs": 6.6,  "fat": 0.4,  "fiber": 2.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Cauliflower":                {"calories": 25,  "protein": 1.9,  "carbs": 5.0,  "fat": 0.3,  "fiber": 2.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Carrot":                     {"calories": 41,  "protein": 0.9,  "carbs": 9.6,  "fat": 0.2,  "fiber": 2.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Tomato":                     {"calories": 18,  "protein": 0.9,  "carbs": 3.9,  "fat": 0.2,  "fiber": 1.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Onion":                      {"calories": 40,  "protein": 1.1,  "carbs": 9.3,  "fat": 0.1,  "fiber": 1.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Garlic":                     {"calories": 149, "protein": 6.4,  "carbs": 33.1, "fat": 0.5,  "fiber": 2.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Ginger":                     {"calories": 80,  "protein": 1.8,  "carbs": 17.8, "fat": 0.8,  "fiber": 2.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Potato":                     {"calories": 77,  "protein": 2.0,  "carbs": 17.5, "fat": 0.1,  "fiber": 2.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Sweet Potato":               {"calories": 86,  "protein": 1.6,  "carbs": 20.1, "fat": 0.1,  "fiber": 3.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Capsicum (Bell Pepper)":     {"calories": 31,  "protein": 1.0,  "carbs": 6.0,  "fat": 0.3,  "fiber": 2.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Cucumber":                   {"calories": 15,  "protein": 0.7,  "carbs": 3.6,  "fat": 0.1,  "fiber": 0.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Mushroom (Button)":          {"calories": 22,  "protein": 3.1,  "carbs": 3.3,  "fat": 0.3,  "fiber": 1.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Mushroom (Shiitake)":        {"calories": 34,  "protein": 2.2,  "carbs": 6.8,  "fat": 0.5,  "fiber": 2.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Peas (Green)":               {"calories": 81,  "protein": 5.4,  "carbs": 14.5, "fat": 0.4,  "fiber": 5.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Corn":                       {"calories": 86,  "protein": 3.3,  "carbs": 19.0, "fat": 1.4,  "fiber": 2.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Bottle Gourd (Lauki)":       {"calories": 14,  "protein": 0.6,  "carbs": 3.4,  "fat": 0.0,  "fiber": 0.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Bitter Gourd (Karela)":      {"calories": 17,  "protein": 1.0,  "carbs": 3.7,  "fat": 0.2,  "fiber": 2.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Ridge Gourd (Turai)":        {"calories": 20,  "protein": 1.2,  "carbs": 3.9,  "fat": 0.2,  "fiber": 0.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Okra (Bhindi)":              {"calories": 33,  "protein": 1.9,  "carbs": 7.5,  "fat": 0.2,  "fiber": 3.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Cabbage":                    {"calories": 25,  "protein": 1.3,  "carbs": 5.8,  "fat": 0.1,  "fiber": 2.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Beetroot":                   {"calories": 43,  "protein": 1.6,  "carbs": 9.6,  "fat": 0.2,  "fiber": 2.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Zucchini":                   {"calories": 17,  "protein": 1.2,  "carbs": 3.1,  "fat": 0.3,  "fiber": 1.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Lettuce (Iceberg)":          {"calories": 14,  "protein": 0.9,  "carbs": 3.0,  "fat": 0.1,  "fiber": 1.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Lettuce (Romaine)":          {"calories": 17,  "protein": 1.2,  "carbs": 3.3,  "fat": 0.3,  "fiber": 2.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Avocado":                    {"calories": 160, "protein": 2.0,  "carbs": 8.5,  "fat": 14.7, "fiber": 6.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Asparagus":                  {"calories": 20,  "protein": 2.2,  "carbs": 3.9,  "fat": 0.1,  "fiber": 2.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Artichoke":                  {"calories": 47,  "protein": 3.3,  "carbs": 10.5, "fat": 0.2,  "fiber": 5.4,  "unit": "g",     "serving_label": "per 100 g"},
    "Brussels Sprouts":           {"calories": 43,  "protein": 3.4,  "carbs": 9.0,  "fat": 0.3,  "fiber": 3.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Celery":                     {"calories": 16,  "protein": 0.7,  "carbs": 3.0,  "fat": 0.2,  "fiber": 1.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Radish (Mooli)":             {"calories": 16,  "protein": 0.7,  "carbs": 3.4,  "fat": 0.1,  "fiber": 1.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Turnip":                     {"calories": 28,  "protein": 0.9,  "carbs": 6.4,  "fat": 0.1,  "fiber": 1.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Eggplant (Baingan)":         {"calories": 25,  "protein": 1.0,  "carbs": 6.0,  "fat": 0.2,  "fiber": 3.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Green Beans":                {"calories": 31,  "protein": 1.8,  "carbs": 7.0,  "fat": 0.1,  "fiber": 3.4,  "unit": "g",     "serving_label": "per 100 g"},
    "Spring Onion":               {"calories": 32,  "protein": 1.8,  "carbs": 7.3,  "fat": 0.2,  "fiber": 2.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Coriander Leaves":           {"calories": 23,  "protein": 2.1,  "carbs": 3.7,  "fat": 0.5,  "fiber": 2.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Mint Leaves":                {"calories": 44,  "protein": 3.3,  "carbs": 8.4,  "fat": 0.7,  "fiber": 6.8,  "unit": "g",     "serving_label": "per 100 g"},

    # ══════════════════════════════════
    #  FRUITS
    # ══════════════════════════════════
    "Apple":                      {"calories": 95,  "protein": 0.5,  "carbs": 25.1, "fat": 0.3,  "fiber": 4.4,  "unit": "piece", "serving_label": "per piece (~182 g)"},
    "Banana":                     {"calories": 105, "protein": 1.3,  "carbs": 27.0, "fat": 0.4,  "fiber": 3.1,  "unit": "piece", "serving_label": "per piece (~118 g)"},
    "Orange":                     {"calories": 62,  "protein": 1.2,  "carbs": 15.4, "fat": 0.2,  "fiber": 3.1,  "unit": "piece", "serving_label": "per piece (~131 g)"},
    "Mango":                      {"calories": 200, "protein": 2.8,  "carbs": 50.3, "fat": 1.3,  "fiber": 5.4,  "unit": "piece", "serving_label": "per piece (~336 g)"},
    "Grapes":                     {"calories": 69,  "protein": 0.7,  "carbs": 18.1, "fat": 0.2,  "fiber": 0.9,  "unit": "g",     "serving_label": "per 100 g"},
    "Watermelon":                 {"calories": 30,  "protein": 0.6,  "carbs": 7.6,  "fat": 0.2,  "fiber": 0.4,  "unit": "g",     "serving_label": "per 100 g"},
    "Papaya":                     {"calories": 43,  "protein": 0.5,  "carbs": 10.8, "fat": 0.3,  "fiber": 1.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Pineapple":                  {"calories": 50,  "protein": 0.5,  "carbs": 13.1, "fat": 0.1,  "fiber": 1.4,  "unit": "g",     "serving_label": "per 100 g"},
    "Pomegranate":                {"calories": 83,  "protein": 1.7,  "carbs": 18.7, "fat": 1.2,  "fiber": 4.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Strawberry":                 {"calories": 32,  "protein": 0.7,  "carbs": 7.7,  "fat": 0.3,  "fiber": 2.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Blueberries":                {"calories": 57,  "protein": 0.7,  "carbs": 14.5, "fat": 0.3,  "fiber": 2.4,  "unit": "g",     "serving_label": "per 100 g"},
    "Raspberries":                {"calories": 52,  "protein": 1.2,  "carbs": 11.9, "fat": 0.7,  "fiber": 6.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Blackberries":               {"calories": 43,  "protein": 1.4,  "carbs": 9.6,  "fat": 0.5,  "fiber": 5.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Cranberries":                {"calories": 46,  "protein": 0.4,  "carbs": 12.2, "fat": 0.1,  "fiber": 4.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Guava":                      {"calories": 68,  "protein": 2.6,  "carbs": 14.3, "fat": 1.0,  "fiber": 5.4,  "unit": "piece", "serving_label": "per piece (~55 g)"},
    "Kiwi":                       {"calories": 42,  "protein": 0.8,  "carbs": 10.1, "fat": 0.4,  "fiber": 2.1,  "unit": "piece", "serving_label": "per piece (~69 g)"},
    "Pear":                       {"calories": 101, "protein": 0.7,  "carbs": 27.1, "fat": 0.3,  "fiber": 5.5,  "unit": "piece", "serving_label": "per piece (~178 g)"},
    "Peach":                      {"calories": 59,  "protein": 1.4,  "carbs": 14.3, "fat": 0.4,  "fiber": 2.3,  "unit": "piece", "serving_label": "per piece (~150 g)"},
    "Plum":                       {"calories": 30,  "protein": 0.5,  "carbs": 7.5,  "fat": 0.2,  "fiber": 0.9,  "unit": "piece", "serving_label": "per piece (~66 g)"},
    "Apricot":                    {"calories": 17,  "protein": 0.5,  "carbs": 3.9,  "fat": 0.1,  "fiber": 0.7,  "unit": "piece", "serving_label": "per piece (~35 g)"},
    "Cherry":                     {"calories": 63,  "protein": 1.1,  "carbs": 16.0, "fat": 0.2,  "fiber": 2.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Fig (Fresh)":                {"calories": 74,  "protein": 0.8,  "carbs": 19.2, "fat": 0.3,  "fiber": 2.9,  "unit": "g",     "serving_label": "per 100 g"},
    "Fig (Dried)":                {"calories": 249, "protein": 3.3,  "carbs": 63.9, "fat": 0.9,  "fiber": 9.8,  "unit": "g",     "serving_label": "per 100 g"},
    "Dates (Medjool)":            {"calories": 277, "protein": 1.8,  "carbs": 75.0, "fat": 0.2,  "fiber": 6.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Raisins":                    {"calories": 299, "protein": 3.1,  "carbs": 79.2, "fat": 0.5,  "fiber": 3.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Prunes (Dried Plums)":       {"calories": 240, "protein": 2.2,  "carbs": 63.9, "fat": 0.4,  "fiber": 7.1,  "unit": "g",     "serving_label": "per 100 g"},
    "Lychee":                     {"calories": 66,  "protein": 0.8,  "carbs": 16.5, "fat": 0.4,  "fiber": 1.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Jackfruit":                  {"calories": 95,  "protein": 1.7,  "carbs": 23.2, "fat": 0.6,  "fiber": 1.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Coconut (Fresh)":            {"calories": 354, "protein": 3.3,  "carbs": 15.2, "fat": 33.5, "fiber": 9.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Coconut (Desiccated)":       {"calories": 660, "protein": 6.9,  "carbs": 23.7, "fat": 64.5, "fiber": 16.3, "unit": "g",     "serving_label": "per 100 g"},

    # ══════════════════════════════════
    #  NUTS & SEEDS (per 100 g)
    # ══════════════════════════════════
    "Almonds":                    {"calories": 579, "protein": 21.2, "carbs": 21.6, "fat": 49.9, "fiber": 12.5, "unit": "g",     "serving_label": "per 100 g"},
    "Cashews":                    {"calories": 553, "protein": 18.2, "carbs": 30.2, "fat": 43.9, "fiber": 3.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Walnuts":                    {"calories": 654, "protein": 15.2, "carbs": 13.7, "fat": 65.2, "fiber": 6.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Pecans":                     {"calories": 691, "protein": 9.2,  "carbs": 13.9, "fat": 72.0, "fiber": 9.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Pistachios":                 {"calories": 562, "protein": 20.2, "carbs": 27.2, "fat": 45.3, "fiber": 10.6, "unit": "g",     "serving_label": "per 100 g"},
    "Macadamia Nuts":             {"calories": 718, "protein": 7.9,  "carbs": 13.8, "fat": 75.8, "fiber": 8.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Brazil Nuts":                {"calories": 659, "protein": 14.3, "carbs": 12.3, "fat": 67.1, "fiber": 7.5,  "unit": "g",     "serving_label": "per 100 g"},
    "Hazelnuts":                  {"calories": 628, "protein": 15.0, "carbs": 16.7, "fat": 60.8, "fiber": 9.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Pine Nuts":                  {"calories": 673, "protein": 13.7, "carbs": 13.1, "fat": 68.4, "fiber": 3.7,  "unit": "g",     "serving_label": "per 100 g"},
    "Chia Seeds":                 {"calories": 486, "protein": 16.5, "carbs": 42.1, "fat": 30.7, "fiber": 34.4, "unit": "g",     "serving_label": "per 100 g"},
    "Flax Seeds":                 {"calories": 534, "protein": 18.3, "carbs": 28.9, "fat": 42.2, "fiber": 27.3, "unit": "g",     "serving_label": "per 100 g"},
    "Sunflower Seeds":            {"calories": 584, "protein": 20.8, "carbs": 20.0, "fat": 51.5, "fiber": 8.6,  "unit": "g",     "serving_label": "per 100 g"},
    "Pumpkin Seeds":              {"calories": 559, "protein": 30.2, "carbs": 10.7, "fat": 49.1, "fiber": 6.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Sesame Seeds":               {"calories": 573, "protein": 17.7, "carbs": 23.5, "fat": 49.7, "fiber": 11.8, "unit": "g",     "serving_label": "per 100 g"},
    "Hemp Seeds":                 {"calories": 553, "protein": 31.6, "carbs": 8.7,  "fat": 48.8, "fiber": 4.0,  "unit": "g",     "serving_label": "per 100 g"},

    # ══════════════════════════════════
    #  OILS & FATS (per 100 g / ml)
    # ══════════════════════════════════
    "Olive Oil":                  {"calories": 884, "protein": 0.0,  "carbs": 0.0,  "fat": 100.0,"fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Coconut Oil":                {"calories": 862, "protein": 0.0,  "carbs": 0.0,  "fat": 100.0,"fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Mustard Oil":                {"calories": 884, "protein": 0.0,  "carbs": 0.0,  "fat": 100.0,"fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Sunflower Oil":              {"calories": 884, "protein": 0.0,  "carbs": 0.0,  "fat": 100.0,"fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Avocado Oil":                {"calories": 884, "protein": 0.0,  "carbs": 0.0,  "fat": 100.0,"fiber": 0.0,  "unit": "g",     "serving_label": "per 100 ml"},
    "Ghee":                       {"calories": 900, "protein": 0.0,  "carbs": 0.0,  "fat": 99.5, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Butter":                     {"calories": 717, "protein": 0.9,  "carbs": 0.1,  "fat": 81.1, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Peanut Butter":              {"calories": 588, "protein": 25.1, "carbs": 20.0, "fat": 50.4, "fiber": 6.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Almond Butter":              {"calories": 614, "protein": 21.0, "carbs": 18.8, "fat": 55.5, "fiber": 10.5, "unit": "g",     "serving_label": "per 100 g"},
    "Tahini (Sesame Paste)":      {"calories": 595, "protein": 17.0, "carbs": 21.2, "fat": 53.8, "fiber": 9.3,  "unit": "g",     "serving_label": "per 100 g"},
    "Mayonnaise":                 {"calories": 680, "protein": 1.0,  "carbs": 0.6,  "fat": 75.0, "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},

    # ══════════════════════════════════
    #  BEVERAGES & MISC
    # ══════════════════════════════════
    "Black Coffee":               {"calories": 2,   "protein": 0.3,  "carbs": 0.0,  "fat": 0.0,  "fiber": 0.0,  "unit": "piece", "serving_label": "per cup (240 ml)"},
    "Tea (No Sugar)":             {"calories": 2,   "protein": 0.0,  "carbs": 0.5,  "fat": 0.0,  "fiber": 0.0,  "unit": "piece", "serving_label": "per cup (240 ml)"},
    "Green Tea":                  {"calories": 2,   "protein": 0.0,  "carbs": 0.5,  "fat": 0.0,  "fiber": 0.0,  "unit": "piece", "serving_label": "per cup (240 ml)"},
    "Coconut Water":              {"calories": 19,  "protein": 0.7,  "carbs": 3.7,  "fat": 0.2,  "fiber": 1.1,  "unit": "g",     "serving_label": "per 100 ml"},
    "Orange Juice (Fresh)":       {"calories": 45,  "protein": 0.7,  "carbs": 10.4, "fat": 0.2,  "fiber": 0.2,  "unit": "g",     "serving_label": "per 100 ml"},
    "Protein Bar":                {"calories": 200, "protein": 20.0, "carbs": 22.0, "fat": 7.0,  "fiber": 3.0,  "unit": "piece", "serving_label": "per bar (~60 g)"},
    "Dark Chocolate (70%)":       {"calories": 598, "protein": 7.8,  "carbs": 45.9, "fat": 42.6, "fiber": 10.9, "unit": "g",     "serving_label": "per 100 g"},
    "Dark Chocolate (85%)":       {"calories": 604, "protein": 10.0, "carbs": 36.7, "fat": 46.3, "fiber": 12.5, "unit": "g",     "serving_label": "per 100 g"},
    "Milk Chocolate":             {"calories": 535, "protein": 7.6,  "carbs": 59.4, "fat": 29.7, "fiber": 3.4,  "unit": "g",     "serving_label": "per 100 g"},
    "Honey":                      {"calories": 304, "protein": 0.3,  "carbs": 82.4, "fat": 0.0,  "fiber": 0.2,  "unit": "g",     "serving_label": "per 100 g"},
    "Maple Syrup":                {"calories": 260, "protein": 0.0,  "carbs": 67.0, "fat": 0.1,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Sugar":                      {"calories": 387, "protein": 0.0,  "carbs": 100.0,"fat": 0.0,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Jaggery":                    {"calories": 383, "protein": 0.4,  "carbs": 97.0, "fat": 0.1,  "fiber": 0.0,  "unit": "g",     "serving_label": "per 100 g"},
    "Rice Cake":                  {"calories": 35,  "protein": 0.7,  "carbs": 7.3,  "fat": 0.3,  "fiber": 0.4,  "unit": "piece", "serving_label": "per piece (~9 g)"},
    "Popcorn (Air-popped)":       {"calories": 375, "protein": 12.0, "carbs": 74.3, "fat": 4.5,  "fiber": 14.5, "unit": "g",     "serving_label": "per 100 g"},
    "Trail Mix":                  {"calories": 462, "protein": 13.0, "carbs": 44.0, "fat": 28.0, "fiber": 5.0,  "unit": "g",     "serving_label": "per 100 g"},
}

MEALS = ["Breakfast", "Lunch", "Dinner", "Snacks"]

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_hona_hai_data.json")

# ─────────────────────────────────────
#  PERSISTENCE  helpers
# ─────────────────────────────────────
def _load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _today_key():
    return str(date.today())

def get_today_data():
    data = _load_data()
    key = _today_key()
    if key not in data:
        data[key] = {m: [] for m in MEALS}
        _save_data(data)
    return data, key

# ─────────────────────────────────────
#  EMAIL  helper
# ─────────────────────────────────────
def send_email_summary(sender_email, sender_password, receiver_email, subject, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# ─────────────────────────────────────
#  STREAMLIT  APP
# ─────────────────────────────────────
st.set_page_config(page_title="Daily Calorie Tracker", page_icon="🔥", layout="wide")

# ── Custom CSS ──
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00c853, #00bfa5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-top: -8px;
        margin-bottom: 28px;
    }
    .meal-header {
        font-size: 1.35rem;
        font-weight: 700;
        border-bottom: 2px solid #00c853;
        padding-bottom: 4px;
        margin-bottom: 12px;
    }
    .calorie-badge {
        background: #00c853;
        color: white;
        padding: 4px 14px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 1rem;
    }
    .total-card {
        background: linear-gradient(135deg, #00c853 0%, #00bfa5 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 20px 0;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔥 Daily Calorie Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Track every bite, crush every goal.</div>', unsafe_allow_html=True)

# ── Initialize session-only meal data (keyed by date) ──
if "meals_data" not in st.session_state:
    st.session_state["meals_data"] = {}

# Date picker
selected_date = st.date_input("📅 Select date", value=date.today())
date_key = str(selected_date)

# Ensure date entry exists
if date_key not in st.session_state["meals_data"]:
    st.session_state["meals_data"][date_key] = {m: [] for m in MEALS}

today_meals = st.session_state["meals_data"][date_key]

# ── Sidebar — Food Database Reference ──
with st.sidebar:
    st.header("📖 Food Calorie & Macro Reference")
    search_term = st.text_input("🔍 Search item", placeholder="e.g. paneer, egg, rice …")
    filtered = {k: v for k, v in FOOD_DATABASE.items()
                if search_term.lower() in k.lower()} if search_term else FOOD_DATABASE

    # group by category for nicer display
    st.markdown(f"**{len(filtered)}** items found")
    for name, info in sorted(filtered.items()):
        st.markdown(
            f"**{name}** — `{info['calories']} kcal` *({info['serving_label']})*  \n"
            f"&nbsp;&nbsp;P: {info['protein']}g · C: {info['carbs']}g · F: {info['fat']}g · Fiber: {info['fiber']}g"
        )

# ─────────────────────────────────────
#  MAIN — Add Items
# ─────────────────────────────────────
food_names = sorted(FOOD_DATABASE.keys())

# ── Add from Database ──
with st.expander("➕ Add item from database", expanded=True):
    sel_key = "select_food"
    qty_key = "qty_food"
    meal_key = "meal_select"

    # Dropdowns outside the form so they trigger immediate reruns
    col_meal, col_food = st.columns([1.5, 3])
    col_meal.selectbox(
        "Meal",
        options=MEALS,
        key=meal_key,
    )
    col_food.selectbox(
        "Select food item",
        options=food_names,
        key=sel_key,
        index=None,
        placeholder="Search & pick a food item …",
    )

    # Show unit hint — updates instantly on selection change
    sel_food_hint = st.session_state.get(sel_key)
    if sel_food_hint and sel_food_hint in FOOD_DATABASE:
        hint_info = FOOD_DATABASE[sel_food_hint]
        unit_text = "grams (g)" if hint_info["unit"] == "g" else "count (pieces)"
        st.info(f"📏 **{sel_food_hint}** — enter quantity in **{unit_text}** ({hint_info['serving_label']})")

    with st.form(key="add_food_form"):
        col_qty_form, _ = st.columns([1, 3])
        col_qty_form.number_input(
            "Quantity",
            min_value=0.1,
            value=1.0,
            step=0.5,
            format="%.1f",
            key=qty_key,
        )

        submitted = st.form_submit_button("➕ Add Item")

    # Process submission AFTER form block
    if submitted:
        selected_food = st.session_state.get(sel_key)
        qty = st.session_state.get(qty_key, 1.0)
        selected_meal = st.session_state.get(meal_key, "Breakfast")
        if selected_food:
            info = FOOD_DATABASE[selected_food]
            if info["unit"] == "g":
                mult = qty / 100
                unit_label = "g"
            else:
                mult = qty
                unit_label = "piece(s)"

            today_meals[selected_meal].append({
                "name": selected_food,
                "quantity": qty,
                "unit_label": unit_label,
                "calories": round(info["calories"] * mult, 1),
                "protein": round(info["protein"] * mult, 1),
                "carbs": round(info["carbs"] * mult, 1),
                "fat": round(info["fat"] * mult, 1),
                "fiber": round(info["fiber"] * mult, 1),
            })
            st.rerun()

# ── Manual Entry ──
with st.expander("✏️ Manually add entry"):
    with st.form(key="manual_form"):
        m_col1, m_col2 = st.columns([1.5, 3])
        m_col1.selectbox("Meal", options=MEALS, key="manual_meal_select")
        m_col2.text_input(
            "Meal / item description",
            placeholder="e.g. Restaurant pasta, Home-cooked dal …",
            key="manual_name",
        )

        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        mc1.number_input("Calories (kcal)", min_value=0, value=100, step=10, key="manual_cal")
        mc2.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="manual_protein")
        mc3.number_input("Carbs (g)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="manual_carbs")
        mc4.number_input("Fat (g)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="manual_fat")
        mc5.number_input("Fiber (g)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="manual_fiber")

        manual_submitted = st.form_submit_button("➕ Add Manual Entry")

    if manual_submitted:
        manual_name = st.session_state.get("manual_name", "").strip()
        manual_meal = st.session_state.get("manual_meal_select", "Breakfast")
        manual_cals = st.session_state.get("manual_cal", 100)
        manual_p = st.session_state.get("manual_protein", 0.0)
        manual_c = st.session_state.get("manual_carbs", 0.0)
        manual_f = st.session_state.get("manual_fat", 0.0)
        manual_fb = st.session_state.get("manual_fiber", 0.0)
        if manual_name:
            today_meals[manual_meal].append({
                "name": f"📝 {manual_name}",
                "quantity": 1,
                "unit_label": "manual",
                "calories": manual_cals,
                "protein": manual_p,
                "carbs": manual_c,
                "fat": manual_f,
                "fiber": manual_fb,
            })
            st.rerun()
        else:
            st.warning("Please enter a description for the item.")

st.markdown("---")

# ─────────────────────────────────────
#  ITEMS FOR SELECTED DATE (grouped by meal)
# ─────────────────────────────────────
for meal in MEALS:
    meal_items = today_meals.get(meal, [])
    if not meal_items:
        continue

    meal_total = sum(item["calories"] for item in meal_items)
    st.markdown(f'<div class="meal-header">🍽️ {meal}</div>', unsafe_allow_html=True)

    cols_header = st.columns([2.5, 1, 1, 1, 1, 1, 1, 0.5])
    cols_header[0].markdown("**Item**")
    cols_header[1].markdown("**Qty**")
    cols_header[2].markdown("**Calories**")
    cols_header[3].markdown("**Protein**")
    cols_header[4].markdown("**Carbs**")
    cols_header[5].markdown("**Fat**")
    cols_header[6].markdown("**Fiber**")
    cols_header[7].markdown("**Del**")

    for idx, item in enumerate(meal_items):
        cols = st.columns([2.5, 1, 1, 1, 1, 1, 1, 0.5])
        cols[0].write(item["name"])
        cols[1].write(f"{item['quantity']} {item['unit_label']}")
        cols[2].write(f"{item['calories']} kcal")
        cols[3].write(f"{item.get('protein', 0)}g")
        cols[4].write(f"{item.get('carbs', 0)}g")
        cols[5].write(f"{item.get('fat', 0)}g")
        cols[6].write(f"{item.get('fiber', 0)}g")
        if cols[7].button("🗑️", key=f"del_{meal}_{idx}"):
            today_meals[meal].pop(idx)
            st.rerun()

    meal_protein = round(sum(item.get("protein", 0) for item in meal_items), 1)
    meal_carbs = round(sum(item.get("carbs", 0) for item in meal_items), 1)
    meal_fat = round(sum(item.get("fat", 0) for item in meal_items), 1)
    meal_fiber = round(sum(item.get("fiber", 0) for item in meal_items), 1)
    st.markdown(
        f'<span class="calorie-badge">{meal}: {meal_total} kcal &nbsp;|&nbsp; '
        f'P: {meal_protein}g · C: {meal_carbs}g · F: {meal_fat}g · Fiber: {meal_fiber}g</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

# Show message if no items at all
if not any(today_meals.get(m) for m in MEALS):
    st.caption("No items added yet for this date. Use the forms above to add items.")

st.markdown("---")

# ─────────────────────────────────────
#  DAILY  TOTAL
# ─────────────────────────────────────
all_items = [item for m in MEALS for item in today_meals.get(m, [])]
grand_total = round(sum(i["calories"] for i in all_items), 1)
grand_protein = round(sum(i.get("protein", 0) for i in all_items), 1)
grand_carbs = round(sum(i.get("carbs", 0) for i in all_items), 1)
grand_fat = round(sum(i.get("fat", 0) for i in all_items), 1)
grand_fiber = round(sum(i.get("fiber", 0) for i in all_items), 1)

st.markdown(
    f'<div class="total-card">'
    f'📊 Total for {selected_date.strftime("%b %d, %Y")}: {grand_total} kcal<br>'
    f'<span style="font-size:0.75em;font-weight:600;">'
    f'Protein: {grand_protein}g &nbsp;·&nbsp; Carbs: {grand_carbs}g &nbsp;·&nbsp; '
    f'Fat: {grand_fat}g &nbsp;·&nbsp; Fiber: {grand_fiber}g</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────
#  EMAIL  SUMMARY SECTION
# ─────────────────────────────────────
st.markdown("---")
st.subheader("📧 Email Daily Summary")

with st.expander("Configure & Send Email"):
    st.info(
        "**Gmail users:** Use an [App Password](https://myaccount.google.com/apppasswords) instead of your regular password. "
        "Enable 2-Step Verification first."
    )
    with st.form("email_form"):
        ecol1, ecol2 = st.columns(2)
        sender_email = ecol1.text_input("Sender Gmail", placeholder="you@gmail.com")
        sender_password = ecol1.text_input("App Password", type="password")
        receiver_email = ecol2.text_input("Receiver Email", placeholder="friend@email.com")

        send_btn = st.form_submit_button("📤 Send Summary")

        if send_btn:
            if not sender_email or not sender_password or not receiver_email:
                st.error("Please fill in all email fields.")
            else:
                # Build HTML email body
                rows_html = ""
                for m in MEALS:
                    items = today_meals.get(m, [])
                    meal_cal = sum(i["calories"] for i in items)
                    meal_p = round(sum(i.get("protein", 0) for i in items), 1)
                    meal_c = round(sum(i.get("carbs", 0) for i in items), 1)
                    meal_f = round(sum(i.get("fat", 0) for i in items), 1)
                    meal_fb = round(sum(i.get("fiber", 0) for i in items), 1)
                    if items:
                        for i, item in enumerate(items):
                            rows_html += f"""
                            <tr>
                                {"<td rowspan='" + str(len(items)) + "' style='font-weight:700;vertical-align:top;padding:8px;border:1px solid #ddd;'>" + m + "</td>" if i == 0 else ""}
                                <td style='padding:8px;border:1px solid #ddd;'>{item['name']}</td>
                                <td style='padding:8px;border:1px solid #ddd;text-align:center;'>{item['quantity']} {item['unit_label']}</td>
                                <td style='padding:8px;border:1px solid #ddd;text-align:right;'>{item['calories']} kcal</td>
                                <td style='padding:8px;border:1px solid #ddd;text-align:right;'>{item.get('protein',0)}g</td>
                                <td style='padding:8px;border:1px solid #ddd;text-align:right;'>{item.get('carbs',0)}g</td>
                                <td style='padding:8px;border:1px solid #ddd;text-align:right;'>{item.get('fat',0)}g</td>
                                <td style='padding:8px;border:1px solid #ddd;text-align:right;'>{item.get('fiber',0)}g</td>
                            </tr>"""
                        rows_html += f"""
                        <tr style='background:#e8f5e9;'>
                            <td colspan='3' style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:700;'>{m} Total</td>
                            <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:700;'>{meal_cal} kcal</td>
                            <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:700;'>{meal_p}g</td>
                            <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:700;'>{meal_c}g</td>
                            <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:700;'>{meal_f}g</td>
                            <td style='padding:8px;border:1px solid #ddd;text-align:right;font-weight:700;'>{meal_fb}g</td>
                        </tr>"""
                    else:
                        rows_html += f"""
                        <tr>
                            <td style='font-weight:700;padding:8px;border:1px solid #ddd;'>{m}</td>
                            <td colspan='7' style='padding:8px;border:1px solid #ddd;color:#999;'>No items</td>
                        </tr>"""

                html_body = f"""
                <html><body style="font-family:Arial,sans-serif;max-width:750px;margin:auto;">
                <h1 style="color:#00c853;text-align:center;">\U0001f525 Daily Calorie Tracker</h1>
                <h3 style="text-align:center;color:#555;">Daily Calorie & Macro Summary \u2014 {selected_date.strftime("%b %d, %Y")}</h3>
                <table style="width:100%;border-collapse:collapse;margin:20px 0;">
                    <thead>
                        <tr style="background:#00c853;color:white;">
                            <th style="padding:10px;border:1px solid #ddd;">Meal</th>
                            <th style="padding:10px;border:1px solid #ddd;">Item</th>
                            <th style="padding:10px;border:1px solid #ddd;">Qty</th>
                            <th style="padding:10px;border:1px solid #ddd;">Calories</th>
                            <th style="padding:10px;border:1px solid #ddd;">Protein</th>
                            <th style="padding:10px;border:1px solid #ddd;">Carbs</th>
                            <th style="padding:10px;border:1px solid #ddd;">Fat</th>
                            <th style="padding:10px;border:1px solid #ddd;">Fiber</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
                <div style="background:linear-gradient(135deg,#00c853,#00bfa5);color:white;
                            text-align:center;padding:18px;border-radius:12px;font-size:1.3em;font-weight:800;">
                    \U0001f525 Grand Total: {grand_total} kcal<br>
                    <span style="font-size:0.7em;">P: {grand_protein}g \u00b7 C: {grand_carbs}g \u00b7 F: {grand_fat}g \u00b7 Fiber: {grand_fiber}g</span>
                </div>
                <p style="text-align:center;color:#aaa;margin-top:20px;font-size:0.85em;">
                    Sent with \u2764\ufe0f from Daily Calorie Tracker
                </p>
                </body></html>
                """

                try:
                    send_email_summary(
                        sender_email, sender_password, receiver_email,
                        f"Daily Calorie Tracker — Summary ({selected_date.strftime('%b %d, %Y')})",
                        html_body,
                    )
                    st.success("✅ Email sent successfully!")
                except Exception as e:
                    st.error(f"Failed to send email: {e}")

# ─────────────────────────────────────
#  WHATSAPP  SUMMARY SECTION
# ─────────────────────────────────────
st.markdown("---")
st.subheader("📱 WhatsApp Daily Summary")

with st.expander("Configure & Send WhatsApp Message"):
    st.info(
        "**Free via CallMeBot:**\n\n"
        "1. Save **+34 644 71 81 84** in your phone contacts\n"
        "2. Send `I allow callmebot to send me messages` to that number on WhatsApp\n"
        "3. You'll receive an **API key** — enter it below\n\n"
        "[CallMeBot setup guide](https://www.callmebot.com/blog/free-api-whatsapp-messages/)"
    )
    with st.form("whatsapp_form"):
        wcol1, wcol2 = st.columns(2)
        wa_phone = wcol1.text_input("Phone number (with country code)", placeholder="e.g. +919876543210")
        wa_apikey = wcol2.text_input("CallMeBot API Key", placeholder="e.g. 1234567")

        wa_btn = st.form_submit_button("📱 Send via WhatsApp")

        if wa_btn:
            if not wa_phone or not wa_apikey:
                st.error("Please enter both phone number and API key.")
            else:
                # Build plain-text summary
                lines = []
                lines.append(f"🔥 *Daily Calorie Tracker*")
                lines.append(f"📅 {selected_date.strftime('%b %d, %Y')}")
                lines.append("")
                for m in MEALS:
                    items = today_meals.get(m, [])
                    if items:
                        meal_cal = sum(i['calories'] for i in items)
                        meal_p = round(sum(i.get('protein', 0) for i in items), 1)
                        meal_c = round(sum(i.get('carbs', 0) for i in items), 1)
                        meal_f = round(sum(i.get('fat', 0) for i in items), 1)
                        meal_fb = round(sum(i.get('fiber', 0) for i in items), 1)
                        lines.append(f"🍽️ *{m}*")
                        for item in items:
                            lines.append(f"  • {item['name']} — {item['quantity']} {item['unit_label']} — {item['calories']} kcal")
                        lines.append(f"  _{m} Total: {meal_cal} kcal | P:{meal_p}g C:{meal_c}g F:{meal_f}g Fiber:{meal_fb}g_")
                        lines.append("")
                lines.append(f"🔥 *Grand Total: {grand_total} kcal*")
                lines.append(f"P: {grand_protein}g · C: {grand_carbs}g · F: {grand_fat}g · Fiber: {grand_fiber}g")

                message = "\n".join(lines)
                encoded_msg = urllib.parse.quote(message)
                phone_clean = wa_phone.strip().replace(" ", "").replace("-", "")
                if phone_clean.startswith("+"):
                    phone_clean = phone_clean[1:]

                url = f"https://api.callmebot.com/whatsapp.php?phone={phone_clean}&text={encoded_msg}&apikey={wa_apikey.strip()}"

                try:
                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200 and "queued" in resp.text.lower():
                        st.success("✅ WhatsApp message sent successfully!")
                    else:
                        st.error(f"Failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error sending WhatsApp message: {e}")

# ─────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────
st.markdown(
    "<div style='text-align:center;color:#bbb;margin-top:40px;font-size:0.85rem;'>"
    "Made with ❤️ — Daily Calorie Tracker © 2026</div>",
    unsafe_allow_html=True,
)
