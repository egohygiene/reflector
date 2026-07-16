# Troubleshooting

## LaTeX build failures

- inspect `paper/.cache/aux/paper.log`
- run `bash scripts/print-latex-diagnostics.sh paper`
- verify all `\input{}` and bibliography paths

## Missing biber

Install `biber` from your TeX distribution or package manager.

## Metadata sync failures

Run:

```bash
python3 scripts/sync-version.py --check
python3 scripts/validate-metadata.py
```

## ChkTeX warnings

Run:

```bash
bash scripts/lint-paper.sh paper
```
