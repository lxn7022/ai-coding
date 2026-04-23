#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

LAST_STATUS=""
LAST_BODY=""

perform_request() {
  local method="$1"
  local path="$2"
  local data="${3:-}"
  local body_file="$TMP_DIR/body.json"

  if [[ -n "$data" ]]; then
    LAST_STATUS="$(curl -sS -o "$body_file" -w "%{http_code}" \
      -X "$method" "${BASE_URL}${path}" \
      -H "Content-Type: application/json" \
      -d "$data")"
  else
    LAST_STATUS="$(curl -sS -o "$body_file" -w "%{http_code}" \
      -X "$method" "${BASE_URL}${path}")"
  fi

  LAST_BODY="$(<"$body_file")"
}

assert_status() {
  local name="$1"
  local expected="$2"
  if [[ "$LAST_STATUS" == "$expected" ]]; then
    echo "[PASS] $name -> $LAST_STATUS"
  else
    echo "[FAIL] $name -> expect $expected, got $LAST_STATUS"
    echo "       response: $LAST_BODY"
    exit 1
  fi
}

echo "Base URL: $BASE_URL"

# 健康检查（服务是否启动）
perform_request "GET" "/"
assert_status "GET /" "200"

# 1) 批量创建 20 个学生
STUDENT_ID=""
for i in $(seq 1 20); do
  STUDENT_NO="$(printf "S91%03d" "$i")"
  STUDENT_NAME="$(printf "Alice%02d" "$i")"
  AGE="$((18 + (i % 5)))"

  perform_request "POST" "/students" "{
  \"student_no\": \"${STUDENT_NO}\",
  \"name\": \"${STUDENT_NAME}\",
  \"age\": ${AGE},
  \"gender\": \"female\",
  \"major\": \"Computer Science\"
}"
  assert_status "POST /students #$i" "201"

  CREATED_ID="$(printf '%s' "$LAST_BODY" | /opt/anaconda3/envs/fastapi-env/bin/python -c "import json,sys; print(json.load(sys.stdin)['id'])")"
  if [[ -z "$STUDENT_ID" ]]; then
    STUDENT_ID="$CREATED_ID"
  fi
done
echo "created 20 students, first student id: $STUDENT_ID"

# 2) 查询学生
perform_request "GET" "/students/$STUDENT_ID"
assert_status "GET /students/{id}" "200"

# 3) 列表查询
perform_request "GET" "/students?skip=0&limit=10&name=Ali"
assert_status "GET /students" "200"

# 4) 更新学生
perform_request "PUT" "/students/$STUDENT_ID" '{
  "student_no": "S90001",
  "name": "Alice Zhang",
  "age": 21,
  "gender": "female",
  "major": "Software Engineering"
}'
assert_status "PUT /students/{id}" "200"

# 5) 学号冲突 409
perform_request "POST" "/students" '{
  "student_no": "S90002",
  "name": "Bob",
  "age": 19,
  "gender": "male",
  "major": "Math"
}'
assert_status "POST /students second create" "201"

perform_request "POST" "/students" '{
  "student_no": "S90002",
  "name": "Bob2",
  "age": 20,
  "gender": "male",
  "major": "Math"
}'
assert_status "POST /students duplicate no" "409"

# 6) 非法年龄 422
perform_request "POST" "/students" '{
  "student_no": "S90003",
  "name": "Carol",
  "age": 0,
  "gender": "female",
  "major": "Physics"
}'
assert_status "POST /students invalid age" "422"

# 7) 删除与删除后 404
perform_request "DELETE" "/students/$STUDENT_ID"
assert_status "DELETE /students/{id}" "204"

perform_request "GET" "/students/$STUDENT_ID"
assert_status "GET /students/{id} after delete" "404"

echo "All checks passed."
