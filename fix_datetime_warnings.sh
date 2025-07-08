#!/bin/bash

# Fix datetime deprecation warnings across all Python files
echo "🔧 Fixing datetime deprecation warnings..."

# Files to fix
files=(
    "backend/api_versions/v1.py"
    "backend/api_versions/v2.py"
    "backend/app.py"
    "backend/app.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "Fixing $file..."

        # Add timezone import if not present
        if ! grep -q "from datetime import.*timezone" "$file"; then
            # Replace the datetime import line
            sed -i 's/from datetime import datetime/from datetime import datetime, timezone/' "$file"
        fi

        # Replace datetime.utcnow() with datetime.now(timezone.utc)
        sed -i 's/datetime\.utcnow()\.isoformat() + "Z"/datetime.now(timezone.utc).isoformat()/g' "$file"

        echo "✅ Fixed $file"
    else
        echo "⚠️ File $file not found"
    fi
done

echo "🎯 All datetime deprecation warnings fixed!"
