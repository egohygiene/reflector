#!/usr/bin/env bash
# build-paper.sh — Build LaTeX paper(s) to PDF.

set -euo pipefail

REPOSITORY_ROOT="$(git rev-parse --show-toplevel)"
PAPERS_DIRECTORY="${REPOSITORY_ROOT}/papers"
DOCS_DIRECTORY="${REPOSITORY_ROOT}/docs"

DEFAULT_PAPER="reflector"
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
  --all       Build all papers under papers/
  --open      Open the generated PDF after building
  --publish   Copy the generated publication assets into docs/<slug>/ and docs/papers/<slug>/
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

    if [[ -d "${input}" ]]; then
        printf '%s\n' "${input}"
        return
    fi

    if [[ -d "${PAPERS_DIRECTORY}/${input}" ]]; then
        printf '%s\n' "${PAPERS_DIRECTORY}/${input}"
        return
    fi

    if [[ -d "${REPOSITORY_ROOT}/${input}" ]]; then
        printf '%s\n' "${REPOSITORY_ROOT}/${input}"
        return
    fi

    printf '%s\n' "${PAPERS_DIRECTORY}/${input}"
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
    local latexmkrc_file="${paper_directory}/.latexmkrc"
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
            -r ".latexmkrc" \
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
    local dest_dir="${DOCS_DIRECTORY}/${slug}"
    local dest_pdf="${dest_dir}/${slug}.pdf"
    local compat_dir="${DOCS_DIRECTORY}/papers/${slug}"
    local compat_pdf="${compat_dir}/${slug}.pdf"
    local figures_source_dir="${paper_directory}/figures"
    local figures_dest_dir="${dest_dir}/figures"
    local figures_compat_dir="${compat_dir}/figures"
    local publish_dir

    if [[ ! -f "${source_pdf}" ]]; then
        echo "Error: Cannot publish — PDF not found at '${source_pdf}'." >&2
        exit 1
    fi

    mkdir -p "${dest_dir}" "${compat_dir}"
    cp "${source_pdf}" "${dest_pdf}"
    cp "${source_pdf}" "${compat_pdf}"

    if [[ -d "${figures_source_dir}" ]]; then
        for publish_dir in "${figures_dest_dir}" "${figures_compat_dir}"; do
            mkdir -p "${publish_dir}"
            cp -R "${figures_source_dir}/." "${publish_dir}/"
        done
    fi

    echo "Published: ${dest_pdf}"
    echo "Published: ${compat_pdf}"
}

if [[ "${BUILD_ALL}" == "true" ]]; then
    mapfile -t PAPER_DIRECTORIES < <(
        find "${PAPERS_DIRECTORY}" -mindepth 1 -maxdepth 1 -type d | sort
    )

    for directory in "${PAPER_DIRECTORIES[@]}"; do
        if [[ -f "${directory}/paper.tex" ]]; then
            build_paper "${directory}"
        else
            echo "Warning: Skipping '${directory}' — no paper.tex found." >&2
        fi
    done
else
    build_paper "${TARGET}"
fi
