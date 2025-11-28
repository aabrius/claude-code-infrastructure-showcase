#!/bin/bash

# GAM API Journey Validation Script
# This script runs comprehensive journey tests to validate all user paths

set -e

echo "🚀 GAM API Journey Validation Starting..."
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create reports directory
mkdir -p tests/reports/journeys

echo -e "\n📋 Phase 1: Authentication Journeys"
echo "-----------------------------------"
python -m pytest tests/journeys/test_authentication_journeys.py -v --tb=short || {
    echo -e "${RED}❌ Authentication journeys failed${NC}"
    exit 1
}

echo -e "\n📊 Phase 2: Report Generation Journeys"
echo "--------------------------------------"
python -m pytest tests/journeys/test_report_generation_journeys.py -v --tb=short || {
    echo -e "${RED}❌ Report generation journeys failed${NC}"
    exit 1
}

echo -e "\n📈 Phase 3: Generating Journey Summary"
echo "-------------------------------------"
python tests/journeys/run_journey_tests.py --categories authentication report_generation

echo -e "\n📋 Phase 4: Journey Coverage Analysis"
echo "------------------------------------"

# Check if all expected journey files exist
expected_journeys=(
    "test_authentication_journeys.py"
    "test_report_generation_journeys.py"
    "test_api_journeys.py"
    "test_mcp_journeys.py" 
    "test_sdk_journeys.py"
    "test_error_handling_journeys.py"
    "test_performance_journeys.py"
)

missing_journeys=()
for journey in "${expected_journeys[@]}"; do
    if [ ! -f "tests/journeys/$journey" ]; then
        missing_journeys+=("$journey")
    fi
done

if [ ${#missing_journeys[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing journey test files:${NC}"
    for missing in "${missing_journeys[@]}"; do
        echo "   - $missing"
    done
fi

echo -e "\n🎯 Phase 5: Validation Results"
echo "-----------------------------"

# Check if journey summary exists
if [ -f "tests/reports/journeys/journey_test_summary.md" ]; then
    echo -e "${GREEN}✅ Journey test summary generated${NC}"
    
    # Extract key metrics
    if grep -q "Success Rate.*100" tests/reports/journeys/journey_test_summary.md; then
        echo -e "${GREEN}✅ All implemented journeys passing (100% success rate)${NC}"
    else
        echo -e "${YELLOW}⚠️  Some journeys failing - check summary report${NC}"
    fi
    
    echo ""
    echo "📄 Full report available at: tests/reports/journeys/journey_test_summary.md"
    echo "📊 JSON report available at: tests/reports/journeys/journey_test_summary.json"
else
    echo -e "${RED}❌ Journey summary not generated${NC}"
    exit 1
fi

echo -e "\n🏁 Journey Validation Complete!"
echo "==============================="

# Final recommendations
echo ""
echo "📝 Next Steps:"
echo "1. Review the journey test summary report"
echo "2. Implement missing journey test files"
echo "3. Fix any failing journeys before UI development"
echo "4. Consider adding integration tests with real GAM API"
echo ""
echo "Once all journeys are validated, you can proceed with confidence to:"
echo "• Build the Report Builder UI"
echo "• Create production deployment configurations"
echo "• Update documentation for the final structure"

exit 0