#!/bin/bash
#
# Automated MCP Server Test Suite
#
# This script runs comprehensive tests against the MCP server
# using MCP Inspector CLI and FastMCP Client.
#
# Usage:
#   ./scripts/test_mcp_automated.sh              # Run all tests
#   ./scripts/test_mcp_automated.sh --quick      # Quick smoke tests only
#   ./scripts/test_mcp_automated.sh --cloud      # Include cloud tests
#   ./scripts/test_mcp_automated.sh --report     # Generate JSON report
#   ./scripts/test_mcp_automated.sh --help       # Show help
#
# Environment Variables:
#   GAM_MCP_JWT_TOKEN    - JWT token for Cloud Run authentication
#   MCP_SERVER_URL       - Custom HTTP server URL
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Test configuration
REPORT_FILE="test-results/mcp-test-report.json"
TEST_RESULTS=()
PASSED=0
FAILED=0
SKIPPED=0

# Output functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_test() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    ((PASSED++))
    TEST_RESULTS+=("{\"name\": \"$1\", \"status\": \"pass\"}")
}

print_fail() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    echo -e "${RED}  Error: $2${NC}"
    ((FAILED++))
    TEST_RESULTS+=("{\"name\": \"$1\", \"status\": \"fail\", \"error\": \"$2\"}")
}

print_skip() {
    echo -e "${YELLOW}○ SKIP: $1 ($2)${NC}"
    ((SKIPPED++))
    TEST_RESULTS+=("{\"name\": \"$1\", \"status\": \"skip\", \"reason\": \"$2\"}")
}

# Inspector helper
run_inspector_test() {
    local test_name="$1"
    local method="$2"
    local tool_name="$3"
    local expected_field="$4"
    shift 4
    local tool_args=("$@")

    print_test "$test_name"

    # Build command
    local cmd=(
        npx @modelcontextprotocol/inspector --cli
        -e MCP_AUTH_ENABLED=false
        -e MCP_TRANSPORT=stdio
        --
        uv run --directory applications/mcp-server python main.py
        --method "$method"
    )

    if [ -n "$tool_name" ]; then
        cmd+=(--tool-name "$tool_name")
    fi

    for arg in "${tool_args[@]}"; do
        cmd+=(--tool-arg "$arg")
    done

    # Run test
    local output
    if output=$("${cmd[@]}" 2>&1); then
        if echo "$output" | grep -q "$expected_field"; then
            print_pass "$test_name"
            return 0
        else
            print_fail "$test_name" "Expected field '$expected_field' not found"
            return 1
        fi
    else
        print_fail "$test_name" "Command failed"
        return 1
    fi
}

# Test functions
test_tools_list() {
    run_inspector_test \
        "List Tools" \
        "tools/list" \
        "" \
        "gam_quick_report"
}

test_get_quick_report_types() {
    run_inspector_test \
        "Get Quick Report Types" \
        "tools/call" \
        "gam_get_quick_report_types" \
        "quick_report_types"
}

test_get_common_combinations() {
    run_inspector_test \
        "Get Common Combinations" \
        "tools/call" \
        "gam_get_common_combinations" \
        "combinations"
}

test_get_dimensions_metrics() {
    run_inspector_test \
        "Get Dimensions/Metrics (HISTORICAL)" \
        "tools/call" \
        "gam_get_dimensions_metrics" \
        "dimensions" \
        "report_type=HISTORICAL" "category=both"
}

test_get_reach_metrics() {
    run_inspector_test \
        "Get Dimensions/Metrics (REACH)" \
        "tools/call" \
        "gam_get_dimensions_metrics" \
        "metrics" \
        "report_type=REACH" "category=metrics"
}

test_quick_report_delivery() {
    print_test "Quick Report (Delivery)"

    local output
    if output=$(npx @modelcontextprotocol/inspector --cli \
        -e MCP_AUTH_ENABLED=false \
        -e MCP_TRANSPORT=stdio \
        -- uv run --directory applications/mcp-server python main.py \
        --method tools/call \
        --tool-name gam_quick_report \
        --tool-arg report_type=delivery \
        --tool-arg days_back=7 2>&1); then

        if echo "$output" | grep -q '"success": true'; then
            print_pass "Quick Report (Delivery)"
        elif echo "$output" | grep -q "mock mode\|GAM client not available"; then
            print_skip "Quick Report (Delivery)" "Running in mock mode"
        else
            print_fail "Quick Report (Delivery)" "Unexpected response"
        fi
    else
        print_fail "Quick Report (Delivery)" "Command failed"
    fi
}

test_list_reports() {
    print_test "List Reports"

    local output
    if output=$(npx @modelcontextprotocol/inspector --cli \
        -e MCP_AUTH_ENABLED=false \
        -e MCP_TRANSPORT=stdio \
        -- uv run --directory applications/mcp-server python main.py \
        --method tools/call \
        --tool-name gam_list_reports \
        --tool-arg limit=5 2>&1); then

        if echo "$output" | grep -q '"success": true'; then
            print_pass "List Reports"
        elif echo "$output" | grep -q "mock mode\|GAM client not available"; then
            print_skip "List Reports" "Running in mock mode"
        else
            print_fail "List Reports" "Unexpected response"
        fi
    else
        print_fail "List Reports" "Command failed"
    fi
}

test_cloud_connection() {
    if [ -z "$GAM_MCP_JWT_TOKEN" ]; then
        print_skip "Cloud Run Connection" "GAM_MCP_JWT_TOKEN not set"
        return
    fi

    print_test "Cloud Run Connection"

    local cloud_url="https://gam-mcp-server-183972668403.us-central1.run.app/mcp"

    local output
    if output=$(npx @modelcontextprotocol/inspector --cli \
        "$cloud_url" \
        --transport http \
        --header "Authorization: Bearer $GAM_MCP_JWT_TOKEN" \
        --method tools/list 2>&1); then

        if echo "$output" | grep -q "gam_quick_report"; then
            print_pass "Cloud Run Connection"
        elif echo "$output" | grep -q "unauthorized\|401"; then
            print_fail "Cloud Run Connection" "Authentication failed"
        else
            print_fail "Cloud Run Connection" "Unexpected response"
        fi
    else
        print_fail "Cloud Run Connection" "Connection failed"
    fi
}

test_cloud_tool_call() {
    if [ -z "$GAM_MCP_JWT_TOKEN" ]; then
        print_skip "Cloud Run Tool Call" "GAM_MCP_JWT_TOKEN not set"
        return
    fi

    print_test "Cloud Run Tool Call"

    local cloud_url="https://gam-mcp-server-183972668403.us-central1.run.app/mcp"

    local output
    if output=$(npx @modelcontextprotocol/inspector --cli \
        "$cloud_url" \
        --transport http \
        --header "Authorization: Bearer $GAM_MCP_JWT_TOKEN" \
        --method tools/call \
        --tool-name gam_get_quick_report_types 2>&1); then

        if echo "$output" | grep -q '"success": true'; then
            print_pass "Cloud Run Tool Call"
        else
            print_fail "Cloud Run Tool Call" "Unexpected response"
        fi
    else
        print_fail "Cloud Run Tool Call" "Command failed"
    fi
}

# Run pytest integration tests
run_pytest_tests() {
    print_header "Running Pytest Integration Tests"

    if pytest tests/integration/test_mcp_server_real.py -v --tb=short -x 2>&1; then
        print_pass "Pytest Integration Tests"
    else
        print_fail "Pytest Integration Tests" "Some tests failed"
    fi
}

# Generate report
generate_report() {
    mkdir -p "$(dirname "$REPORT_FILE")"

    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local total=$((PASSED + FAILED + SKIPPED))

    cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$timestamp",
  "summary": {
    "total": $total,
    "passed": $PASSED,
    "failed": $FAILED,
    "skipped": $SKIPPED,
    "pass_rate": $(echo "scale=2; $PASSED * 100 / $total" | bc 2>/dev/null || echo "0")
  },
  "tests": [
    $(IFS=,; echo "${TEST_RESULTS[*]}")
  ]
}
EOF

    echo -e "\n${BLUE}Report saved to: $REPORT_FILE${NC}"
}

# Print summary
print_summary() {
    print_header "Test Summary"

    local total=$((PASSED + FAILED + SKIPPED))

    echo -e "Total Tests:  $total"
    echo -e "${GREEN}Passed:       $PASSED${NC}"
    echo -e "${RED}Failed:       $FAILED${NC}"
    echo -e "${YELLOW}Skipped:      $SKIPPED${NC}"

    if [ $FAILED -gt 0 ]; then
        echo -e "\n${RED}Some tests failed!${NC}"
        return 1
    else
        echo -e "\n${GREEN}All tests passed!${NC}"
        return 0
    fi
}

# Usage
show_usage() {
    cat << EOF
MCP Server Automated Test Suite

Usage:
  $0 [options]

Options:
  --quick       Run quick smoke tests only (metadata tools)
  --full        Run all tests including slow report tests
  --cloud       Include Cloud Run deployment tests
  --pytest      Run pytest integration tests
  --report      Generate JSON report
  --help        Show this help

Environment Variables:
  GAM_MCP_JWT_TOKEN    JWT token for Cloud Run authentication
  MCP_SERVER_URL       Custom HTTP server URL

Examples:
  $0                   # Run default tests
  $0 --quick           # Quick smoke tests
  $0 --cloud           # Include cloud tests
  $0 --full --report   # Full tests with report

EOF
}

# Main
main() {
    local run_quick=false
    local run_full=false
    local run_cloud=false
    local run_pytest=false
    local generate_json=false

    # Parse args
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                run_quick=true
                shift
                ;;
            --full)
                run_full=true
                shift
                ;;
            --cloud)
                run_cloud=true
                shift
                ;;
            --pytest)
                run_pytest=true
                shift
                ;;
            --report)
                generate_json=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    print_header "MCP Server Automated Tests"

    # Check requirements
    if ! command -v npx &> /dev/null; then
        echo "Error: npx is required"
        exit 1
    fi

    if ! command -v uv &> /dev/null; then
        echo "Error: uv is required"
        exit 1
    fi

    # Run tests
    print_header "Core Tests (Metadata Tools)"
    test_tools_list
    test_get_quick_report_types
    test_get_common_combinations
    test_get_dimensions_metrics
    test_get_reach_metrics

    if [ "$run_quick" != true ]; then
        print_header "API Tests (Requires GAM Credentials)"
        test_quick_report_delivery
        test_list_reports
    fi

    if [ "$run_cloud" = true ]; then
        print_header "Cloud Run Tests"
        test_cloud_connection
        test_cloud_tool_call
    fi

    if [ "$run_pytest" = true ]; then
        run_pytest_tests
    fi

    # Generate report if requested
    if [ "$generate_json" = true ]; then
        generate_report
    fi

    # Print summary
    print_summary
}

main "$@"
