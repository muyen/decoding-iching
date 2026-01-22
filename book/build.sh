#!/bin/bash

# ============================================================
# Book Build Script for Amazon KDP
# Generates EPUB (for Kindle) and PDF (for Print-on-Demand)
# ============================================================

# Set error handling
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
BOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${BOOK_DIR}/output"
TITLE="解碼易經"
FILENAME="decoding-iching"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Building: ${TITLE}${NC}"
echo -e "${GREEN}========================================${NC}"

# Check for Pandoc
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}Error: Pandoc is not installed.${NC}"
    echo "Please install Pandoc: brew install pandoc"
    exit 1
fi

# Function to concatenate all markdown files in order
concatenate_chapters() {
    local output_file="${OUTPUT_DIR}/full_book.md"

    echo -e "${YELLOW}Concatenating chapters...${NC}"

    # Clear/create output file
    > "${output_file}"

    # Front matter
    cat "${BOOK_DIR}/front_matter/00_title_page.md" >> "${output_file}"
    echo -e "\n\n---\n\n" >> "${output_file}"

    cat "${BOOK_DIR}/front_matter/01_copyright.md" >> "${output_file}"
    echo -e "\n\n---\n\n" >> "${output_file}"

    cat "${BOOK_DIR}/front_matter/02_dedication.md" >> "${output_file}"
    echo -e "\n\n---\n\n" >> "${output_file}"

    cat "${BOOK_DIR}/front_matter/02b_executive_summary.md" >> "${output_file}"
    echo -e "\n\n---\n\n" >> "${output_file}"

    cat "${BOOK_DIR}/front_matter/03_introduction.md" >> "${output_file}"
    echo -e "\n\n---\n\n" >> "${output_file}"

    # Part 1
    echo -e "# 第一部分：入門\n\n" >> "${output_file}"
    for chapter in 01 02 03 04 05; do
        cat "${BOOK_DIR}/chapters/${chapter}_"*.md >> "${output_file}"
        echo -e "\n\n---\n\n" >> "${output_file}"
    done

    # Part 2
    echo -e "# 第二部分：核心發現\n\n" >> "${output_file}"
    for chapter in 06 07 08 09 10 13; do
        cat "${BOOK_DIR}/chapters/${chapter}_"*.md >> "${output_file}"
        echo -e "\n\n---\n\n" >> "${output_file}"
    done

    # Part 3
    echo -e "# 第三部分：實際應用\n\n" >> "${output_file}"
    for chapter in 14 15 16 17 18 19; do
        cat "${BOOK_DIR}/chapters/${chapter}_"*.md >> "${output_file}"
        echo -e "\n\n---\n\n" >> "${output_file}"
    done

    # Part 4
    echo -e "# 第四部分：深入理解\n\n" >> "${output_file}"
    for chapter in 20 21 22 23 24; do
        cat "${BOOK_DIR}/chapters/${chapter}_"*.md >> "${output_file}"
        echo -e "\n\n---\n\n" >> "${output_file}"
    done

    # Appendices
    echo -e "# 附錄\n\n" >> "${output_file}"
    for appendix in A1 A2 A3 A4; do
        cat "${BOOK_DIR}/chapters/${appendix}_"*.md >> "${output_file}"
        echo -e "\n\n---\n\n" >> "${output_file}"
    done

    # Back matter
    cat "${BOOK_DIR}/back_matter/01_about_author.md" >> "${output_file}"
    echo -e "\n\n---\n\n" >> "${output_file}"

    cat "${BOOK_DIR}/back_matter/02_figure_index.md" >> "${output_file}"
    echo -e "\n\n---\n\n" >> "${output_file}"

    cat "${BOOK_DIR}/back_matter/03_quick_reference.md" >> "${output_file}"

    # Collapse multiple blank lines to maximum 1 blank line
    awk 'NF{blank=0} !NF{blank++} blank<=1' "${output_file}" > "${output_file}.tmp" && mv "${output_file}.tmp" "${output_file}"

    echo -e "${GREEN}✓ Chapters concatenated${NC}"
}

# Build EPUB (for Kindle)
build_epub() {
    echo -e "${YELLOW}Building EPUB for Kindle...${NC}"

    pandoc "${OUTPUT_DIR}/full_book.md" \
        --metadata-file="${BOOK_DIR}/metadata.yaml" \
        --toc \
        --toc-depth=2 \
        --epub-chapter-level=1 \
        --epub-cover-image="${BOOK_DIR}/images/cover.jpg" \
        --resource-path="${BOOK_DIR}:${BOOK_DIR}/images" \
        -o "${OUTPUT_DIR}/${FILENAME}.epub"

    echo -e "${GREEN}✓ EPUB created: ${OUTPUT_DIR}/${FILENAME}.epub${NC}"
}

# Build PDF (for Print-on-Demand)
build_pdf() {
    echo -e "${YELLOW}Building PDF for Print...${NC}"

    # Check for xelatex (needed for CJK fonts)
    if ! command -v xelatex &> /dev/null; then
        echo -e "${YELLOW}Warning: xelatex not found. Using pdflatex instead.${NC}"
        echo "For better CJK support, install: brew install --cask mactex"
        PDF_ENGINE="pdflatex"
    else
        PDF_ENGINE="xelatex"
    fi

    pandoc "${OUTPUT_DIR}/full_book.md" \
        --metadata-file="${BOOK_DIR}/metadata.yaml" \
        --pdf-engine="${PDF_ENGINE}" \
        --toc \
        --toc-depth=2 \
        --resource-path="${BOOK_DIR}" \
        -V geometry:margin=1in \
        -V papersize:a5 \
        -V fontsize:11pt \
        -o "${OUTPUT_DIR}/${FILENAME}.pdf" 2>/dev/null || {
            echo -e "${YELLOW}PDF generation requires LaTeX. Skipping PDF.${NC}"
            echo "Install LaTeX for PDF: brew install --cask mactex"
        }

    if [ -f "${OUTPUT_DIR}/${FILENAME}.pdf" ]; then
        echo -e "${GREEN}✓ PDF created: ${OUTPUT_DIR}/${FILENAME}.pdf${NC}"
    fi
}

# Build HTML (for preview)
build_html() {
    echo -e "${YELLOW}Building HTML preview...${NC}"

    pandoc "${OUTPUT_DIR}/full_book.md" \
        --metadata-file="${BOOK_DIR}/metadata.yaml" \
        --toc \
        --toc-depth=2 \
        --standalone \
        --css="${BOOK_DIR}/style.css" \
        --resource-path="${BOOK_DIR}" \
        -o "${OUTPUT_DIR}/${FILENAME}.html"

    echo -e "${GREEN}✓ HTML created: ${OUTPUT_DIR}/${FILENAME}.html${NC}"
}

# Main execution
main() {
    echo -e "${YELLOW}Starting build process...${NC}\n"

    concatenate_chapters

    case "${1:-all}" in
        epub)
            build_epub
            ;;
        pdf)
            build_pdf
            ;;
        html)
            build_html
            ;;
        all|*)
            build_epub
            build_pdf
            build_html
            ;;
    esac

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  Build complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "Output files in: ${OUTPUT_DIR}"
    ls -la "${OUTPUT_DIR}/"
}

# Run main function
main "$@"
