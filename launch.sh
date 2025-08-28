#!/bin/bash

# 🌟 ستاره داوود - اکوسیستم ربات‌های هوشمند اسرائیل
# Magen David - Israeli Smart Bot Ecosystem
# اسکریپت راه‌اندازی خودکار

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🌟 ستاره داوود - اکوسیستم ربات‌های هوشمند اسرائیل 🌟        ║"
echo "║                                                              ║"
echo "║                    Magen David - Israeli Smart Bot Ecosystem ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# بررسی وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ پایتون 3 یافت نشد!"
    echo "لطفاً پایتون 3.8 یا بالاتر را نصب کنید."
    exit 1
fi

# بررسی نسخه Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ نسخه پایتون شما ($PYTHON_VERSION) قدیمی است!"
    echo "نسخه $REQUIRED_VERSION یا بالاتر مورد نیاز است."
    exit 1
fi

echo "✅ نسخه پایتون: $PYTHON_VERSION"

# بررسی وجود فایل‌های ضروری
REQUIRED_FILES=("main.py" "config.py" "models.py" "gemini_integration.py" "magen_david_bot.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ فایل ضروری یافت نشد: $file"
        exit 1
    fi
done

echo "✅ تمام فایل‌های ضروری موجود است"

# بررسی وجود فایل .env
if [ ! -f ".env" ]; then
    echo "⚠️ فایل .env یافت نشد!"
    echo "فایل .env.example را کپی کرده و تنظیمات خود را وارد کنید."
    
    if [ -f ".env.example" ]; then
        echo "کپی کردن فایل نمونه..."
        cp .env.example .env
        echo "✅ فایل .env ایجاد شد. لطفاً تنظیمات خود را وارد کنید."
        echo "سپس دوباره اسکریپت را اجرا کنید."
        exit 1
    else
        echo "❌ فایل .env.example نیز یافت نشد!"
        exit 1
    fi
fi

echo "✅ فایل .env موجود است"

# بررسی وابستگی‌ها
echo "🔍 بررسی وابستگی‌ها..."

# بررسی discord.py
if ! python3 -c "import discord" &> /dev/null; then
    echo "⚠️ کتابخانه discord.py یافت نشد. در حال نصب..."
    pip3 install discord.py
fi

# بررسی google-generativeai
if ! python3 -c "import google.generativeai" &> /dev/null; then
    echo "⚠️ کتابخانه google-generativeai یافت نشد. در حال نصب..."
    pip3 install google-generativeai
fi

# بررسی python-dotenv
if ! python3 -c "import dotenv" &> /dev/null; then
    echo "⚠️ کتابخانه python-dotenv یافت نشد. در حال نصب..."
    pip3 install python-dotenv
fi

echo "✅ تمام وابستگی‌ها بررسی شد"

# راه‌اندازی ربات
echo ""
echo "🚀 راه‌اندازی ربات ستاره داوود..."
echo "برای توقف، Ctrl+C را فشار دهید."
echo ""

# اجرای ربات
python3 main.py

# بررسی وضعیت خروج
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ربات با موفقیت متوقف شد"
else
    echo ""
    echo "❌ ربات با خطا متوقف شد"
    echo "لاگ‌ها را بررسی کنید: tail -f israel_rp.log"
fi