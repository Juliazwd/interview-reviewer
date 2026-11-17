# 一键初始化：创建虚拟环境并安装依赖（Windows PowerShell）
# 用法: 在项目根目录执行  .\scripts\setup.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path ".venv")) {
    Write-Host ">> 创建虚拟环境 .venv ..." -ForegroundColor Cyan
    python -m venv .venv
}

Write-Host ">> 安装依赖（docling 体积较大，首次需要几分钟）..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host ">> 完成！后续使用方式：" -ForegroundColor Green
Write-Host "   激活环境:   .\.venv\Scripts\Activate.ps1"
Write-Host "   启动应用:   python app.py"
Write-Host "   (或在 IDE 中把解释器指向 .\.venv\Scripts\python.exe)"
