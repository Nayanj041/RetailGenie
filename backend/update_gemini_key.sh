#!/bin/bash

# 🔑 Update Gemini API Key Script
# This script helps you update the Gemini API key in your .env files

echo "🔑 RetailGenie - Update Gemini API Key"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run this script from the backend directory."
    exit 1
fi

echo "📝 Current Gemini API Key (first 20 characters):"
current_key=$(grep "GEMINI_API_KEY=" .env | cut -d'=' -f2 | cut -c1-20)
echo "   $current_key..."
echo ""

echo "🌐 To get a new API key:"
echo "   1. Go to: https://aistudio.google.com/"
echo "   2. Sign in with Google"
echo "   3. Click 'Get API Key'"
echo "   4. Create or select project"
echo "   5. Click 'Create API Key'"
echo "   6. Copy the new key"
echo ""

read -p "Enter your new Gemini API key: " new_api_key

if [ -z "$new_api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Validate API key format (should start with AIza and be about 39 characters)
if [[ ! $new_api_key =~ ^AIza.{35}$ ]]; then
    echo "⚠️  Warning: API key format looks unusual."
    echo "   Expected format: AIza... (39 characters total)"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled."
        exit 1
    fi
fi

echo ""
echo "🔄 Updating .env file..."

# Backup original .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Update the API key in .env
sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$new_api_key/" .env

echo "✅ Updated .env file"

# Also update .env.production if it exists
if [ -f ".env.production" ]; then
    sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$new_api_key/" .env.production
    echo "✅ Updated .env.production file"
fi

echo ""
echo "🧪 Testing new API key..."

# Test the new API key
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('🤖 Testing Gemini API...')
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Test connection - say \"API working perfectly\"')
    print(f'✅ SUCCESS: {response.text}')
    print('')
    print('🚀 Your Gemini API key is working!')
    print('   You can now proceed with deployment.')
except Exception as e:
    print(f'❌ ERROR: {str(e)}')
    print('')
    print('🔧 Please check:')
    print('   1. API key is correct')
    print('   2. API key has proper permissions')
    print('   3. Billing is enabled for your Google Cloud project')
"

echo ""
echo "🎉 Update complete!"
echo "📁 Backup saved as: .env.backup.$(date +%Y%m%d_%H%M%S)"
echo ""
echo "📋 Next steps:"
echo "   1. If the test above passed, you're ready to deploy!"
echo "   2. If it failed, double-check your API key"
echo "   3. Review the deployment guide: COMPLETE_DEPLOYMENT_GUIDE.md"
