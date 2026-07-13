#!/bin/bash
# Master control script — shows everything available
# Usage: bash master.sh [command]

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

show_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║    LLM-as-a-Judge Bias Research — Master Control    ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_help() {
    echo ""
    echo "Available commands:"
    echo ""
    echo -e "  ${GREEN}help${NC}           Show this help"
    echo -e "  ${GREEN}status${NC}         Show experiment dashboard"
    echo -e "  ${GREEN}explore${NC}        Explore bias interaction results"
    echo -e "  ${GREEN}rootcause${NC}      Explore root cause results"
    echo -e "  ${GREEN}biaslist${NC}       List all bias types"
    echo -e "  ${GREEN}biastats${NC}       Show bias statistics"
    echo -e "  ${GREEN}faq${NC}            Show FAQ"
    echo -e "  ${GREEN}tests${NC}          Run test suite"
    echo -e "  ${GREEN}proposals${NC}      List all proposals"
    echo -e "  ${GREEN}papers${NC}         List all paper drafts"
    echo -e "  ${GREEN}figures${NC}        Generate figures"
    echo -e "  ${GREEN}report${NC}         Generate analysis report"
    echo -e "  ${GREEN}setup${NC}          Install dependencies"
    echo -e "  ${GREEN}browse${NC}         Browse results files"
    echo -e "  ${GREEN}all${NC}            Run all checks"
    echo ""
}

show_status() {
    cd "$(dirname "$0")"
    python3 dashboard.py
}

show_faq() {
    cd "$(dirname "$0")"
    python3 FAQ.py | head -40
}

run_tests() {
    cd "$(dirname "$0")"
    python3 tests/run_tests.py
}

list_proposals() {
    echo -e "\n${BLUE}Proposals:${NC}"
    for f in proposals/*.md; do
        size=$(wc -c < "$f")
        echo -e "  ${GREEN}$(basename $f)${NC} ($(echo "scale=1; $size/1024" | bc) KB)"
    done
}

list_papers() {
    echo -e "\n${BLUE}Paper Drafts:${NC}"
    for f in paper/*.md paper/*.tex paper/*.html paper/*.bib; do
        if [ -f "$f" ]; then
            words=$(wc -w < "$f")
            echo -e "  ${GREEN}$(basename $f)${NC} (~$words words)"
        fi
    done
}

show_bias_stats() {
    cd "$(dirname "$0")"
    python3 bias_explorer.py --stats
}

# Main
cd "$(dirname "$0")"
show_header

case "${1:-help}" in
    help)       show_help ;;
    status)     show_status ;;
    explore)    python3 explore_results.py ;;
    rootcause)  python3 explore_rootcause.py ;;
    biaslist)   python3 bias_explorer.py --list ;;
    biastats)   show_bias_stats ;;
    faq)        show_faq ;;
    tests)      run_tests ;;
    proposals)  list_proposals ;;
    papers)     list_papers ;;
    figures)    python3 pipeline_biasinteraction/generate_figures.py ;;
    report)     python3 pipeline_biasinteraction/generate_report.py ;;
    setup)      bash setup.sh ;;
    browse)     python3 results_browser.py ;;
    all)
        echo -e "${BLUE}Running all checks...${NC}\n"
        run_tests
        echo ""
        list_proposals
        echo ""
        list_papers
        echo ""
        show_bias_stats
        echo -e "\n${GREEN}All checks complete.${NC}"
        ;;
    *)
        echo -e "${RED}Unknown command: ${1}${NC}"
        show_help
        ;;
esac
