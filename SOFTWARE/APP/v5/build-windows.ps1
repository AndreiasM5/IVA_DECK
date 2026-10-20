param([string]$Python="python", [string]$InnoCompiler="ISCC.exe")
$ErrorActionPreference='Stop'
Push-Location $PSScriptRoot
try {
    & $Python -m pip install -r requirements-build.txt
    if ($LASTEXITCODE) { throw 'Dependencies failed' }
    & $Python packaging/collect_licenses.py build/licenses
    if ($LASTEXITCODE) { throw 'License collection failed' }
    & $Python -m PyInstaller --noconfirm --clean --distpath dist --workpath build/pyinstaller packaging/IVA-DECK.spec
    if ($LASTEXITCODE) { throw 'PyInstaller failed' }
    & $InnoCompiler packaging/installer.iss
    if ($LASTEXITCODE) { throw 'Installer failed' }
    Copy-Item INSTALLATION.txt dist/IVA-DECK/INSTALLATION.txt
    Compress-Archive -Path dist/IVA-DECK -DestinationPath release/IVA-DECK-5.0.0-Portable-x64.zip -Force
    Get-ChildItem release -File | Where-Object { $_.Extension -in '.exe','.zip' } | ForEach-Object {
        $hash=(Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $($_.Name)"
    } | Set-Content release/SHA256SUMS.txt -Encoding ascii
} finally { Pop-Location }
