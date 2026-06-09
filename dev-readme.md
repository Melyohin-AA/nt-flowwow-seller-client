Do static analysis: `mypy nt_flowwow_seller_client`

Test coverage:
1. `pytest --cov=nt_flowwow_seller_client tests`
2. `coverage html`

Generate docs (Linux):
1. `cd sphinx; make html; cd ..`
2. `rm -rf docs`
3. `mv sphinx/build/html docs`

Generate docs (Windows):
1. `sphinx\make.bat html`
2. `rmdir /s /q docs`
3. `move sphinx\build\html docs`

Build: `python -m build`
Upload: `python -m twine upload dist/*`
