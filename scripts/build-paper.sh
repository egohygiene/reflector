#!/usr/bin/env bash
# build-paper.sh — Build LaTeX paper(s) to PDF.

set -euo pipefail

REPOSITORY_ROOT="$(git rev-parse --show-toplevel)"
PAPER_DIRECTORY="${REPOSITORY_ROOT}/paper"
DOCS_DIRECTORY="${REPOSITORY_ROOT}/docs"

DEFAULT_PAPER="paper"
BUILD_ALL=false
OPEN_PDF=false
PUBLISH_PDF=false
TARGET="${DEFAULT_PAPER}"

usage() {
cat <<USAGE
Usage:
  ./scripts/build-paper.sh <paper-name|paper-path>
  ./scripts/build-paper.sh --all
  ./scripts/build-paper.sh <paper-name|paper-path> --open
  ./scripts/build-paper.sh <paper-name|paper-path> --publish
  ./scripts/build-paper.sh --all --publish

Flags:
  --all       Build all papers under paper/
  --open      Open the generated PDF after building
  --publish   Copy the generated publication PDF into docs/<slug>.pdf
USAGE
}

open_pdf() {
    local pdf_file="$1"

    if [[ ! -f "${pdf_file}" ]]; then
        return
    fi

    case "${OSTYPE}" in
        darwin*)
            open "${pdf_file}"
            ;;
        linux*)
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "${pdf_file}"
            fi
            ;;
        msys*|cygwin*|win32*)
            start "${pdf_file}"
            ;;
    esac
}

resolve_paper_directory() {
    local input="$1"

    if [[ ( "${input}" == "paper" || "${input}" == "reflector" ) && -d "${PAPER_DIRECTORY}" ]]; then
        printf '%s\n' "${PAPER_DIRECTORY}"
        return
    fi

    if [[ -d "${input}" ]]; then
        printf '%s\n' "${input}"
        return
    fi

    if [[ -d "${REPOSITORY_ROOT}/${input}" ]]; then
        printf '%s\n' "${REPOSITORY_ROOT}/${input}"
        return
    fi

    printf '%s\n' "${input}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all)
            BUILD_ALL=true
            shift
            ;;
        --open)
            OPEN_PDF=true
            shift
            ;;
        --publish)
            PUBLISH_PDF=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            TARGET="$1"
            shift
            ;;
    esac
done

build_paper() {
    local target="$1"
    local paper_directory

    paper_directory="$(resolve_paper_directory "${target}")"

    local paper_file="${paper_directory}/paper.tex"
    local latexmkrc_file="${REPOSITORY_ROOT}/.latexmkrc"
    local output_directory="${paper_directory}/.cache/out"
    local output_pdf="${output_directory}/paper.pdf"

    if [[ ! -d "${paper_directory}" ]]; then
        echo "Error: Directory '${paper_directory}' not found." >&2
        exit 1
    fi

    if [[ ! -f "${paper_file}" ]]; then
        echo "Error: Missing paper.tex at '${paper_file}'." >&2
        exit 1
    fi

    if [[ ! -f "${latexmkrc_file}" ]]; then
        echo "Error: Missing .latexmkrc at '${latexmkrc_file}'." >&2
        exit 1
    fi

    echo "Building: ${paper_file}"
    echo "Output:   ${output_directory}/"

    (
        cd "${paper_directory}"

        mkdir -p ".cache/aux" ".cache/out"

        latexmk \
            -pdf \
            -interaction=nonstopmode \
            -synctex=1 \
            -file-line-error \
            -shell-escape \
            -f \
            -gg \
            -cd \
            -r "${latexmkrc_file}" \
            "paper.tex"
    )

    if [[ ! -f "${output_pdf}" ]]; then
        echo "Error: Expected PDF not found at '${output_pdf}'." >&2
        exit 1
    fi

    echo "Build complete: ${output_pdf}"

    if [[ "${PUBLISH_PDF}" == "true" ]]; then
        publish_paper "${paper_directory}"
    fi

    if [[ "${OPEN_PDF}" == "true" ]]; then
        open_pdf "${output_pdf}"
    fi
}

publish_paper() {
    local paper_directory="$1"
    local slug

    slug="$(basename "${paper_directory}")"

    local source_pdf="${paper_directory}/.cache/out/paper.pdf"
    local dest_pdf="${DOCS_DIRECTORY}/${slug}.pdf"

    if [[ ! -f "${source_pdf}" ]]; then
        echo "Error: Cannot publish — PDF not found at '${source_pdf}'." >&2
        exit 1
    fi

    mkdir -p "${DOCS_DIRECTORY}"
    cp "${source_pdf}" "${dest_pdf}"

    echo "Published: ${dest_pdf}"
}

if [[ "${BUILD_ALL}" == "true" ]]; then
    build_paper "${PAPER_DIRECTORY}"
else
    build_paper "${TARGET}"
fi
