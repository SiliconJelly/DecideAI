#!/usr/bin/env bash
# End-to-end cURL smoke test for DecideAI API (no jq required)
# NOTE: This script stores the auth token in $TOKEN but never prints its value.

set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:8000}
USERNAME=${USERNAME:-}
PASSWORD=${PASSWORD:-}

info()  { printf "\033[1;34m[i]\033[0m %s\n" "$*"; }
ok()    { printf "\033[1;32m[✓]\033[0m %s\n" "$*"; }
fail()  { printf "\033[1;31m[✗]\033[0m %s\n" "$*"; }

# Check server health
info "Checking health at $BASE_URL/health"
HTTP=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL/health")
if [[ "$HTTP" != "200" ]]; then
  fail "Health check failed (HTTP $HTTP). Is the server running?"
  exit 1
fi
# Optionally show body
curl -sS "$BASE_URL/health" | python3 -m json.tool || true
ok "Health check OK"

# Login and store token securely (no echo)
if [[ -z "${USERNAME:-}" || -z "${PASSWORD:-}" ]]; then
  fail "USERNAME and PASSWORD environment variables are required to login."
  exit 1
fi
info "Logging in as $USERNAME"
TOKEN=$(curl -sS -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  | python3 -c 'import sys, json; print(json.load(sys.stdin).get("access_token",""))')

if [[ -z "${TOKEN:-}" ]]; then
  fail "Failed to obtain access token (check credentials)."
  exit 1
fi
ok "Login OK (token stored in memory)"

# Current user
info "Fetching current user"
curl -sS -X GET "$BASE_URL/auth/me" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | sed -E 's/("access_token": ").*(")/\1***REDACTED***\2/'
ok "Current user OK"

# Direct search (RAG)
info "Direct search (RAG): 'remote work policy'"
curl -sS -X POST "$BASE_URL/ai/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"remote work policy","top_k":3}' | python3 -m json.tool | head -n 50
ok "Search OK"

# AI query without RAG
info "AI query (no RAG)"
curl -sS -X POST "$BASE_URL/ai/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the key principles of good HR management?","use_rag":false}' | python3 -m json.tool | head -n 50
ok "AI query (no RAG) OK"

# AI query with RAG
info "AI query (with RAG)"
curl -sS -X POST "$BASE_URL/ai/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"How many vacation days do employees get?","use_rag":true,"top_k":3}' | python3 -m json.tool | head -n 50
ok "AI query (with RAG) OK"

ok "All cURL smoke tests passed!"