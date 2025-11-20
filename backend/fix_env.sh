#!/bin/bash
# Fix .env file formatting

cd "$(dirname "$0")"

# Backup current .env
cp .env .env.backup

# Fix the formatting issue - add newline after GROQ_API_KEY if missing
# Then ensure SSL vars are on their own lines
cat .env | sed 's/J8k7SSL_CERT_FILE/J8k7\nSSL_CERT_FILE/g' > .env.tmp
mv .env.tmp .env

echo "✅ .env file fixed!"
echo ""
echo "Current .env (last 6 lines):"
tail -6 .env

